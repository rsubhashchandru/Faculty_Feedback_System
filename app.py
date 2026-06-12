from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from config import Config
from sqlalchemy import text
from decimal import Decimal
import datetime

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# --- Authentication Middleware Helper ---
def is_admin_logged_in():
    return 'admin_logged_in' in session

# --- PUBLIC ROUTE: STUDENT FEEDBACK ---
@app.route('/', methods=['GET', 'POST'])
def student_panel():
    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        student_name = request.form.get('student_name') or 'Anonymous'
        student_usn = request.form.get('student_usn') or 'N/A'
        comment_text = request.form.get('comment')
        
        if not faculty_id:
            flash('Please select a faculty member.', 'danger')
            return redirect(url_for('student_panel'))
            
        # Extract question responses dynamically from incoming form dict
        responses = {}
        for key, value in request.form.items():
            if key.startswith('question_'):
                q_id = key.split('_')[1]
                responses[q_id] = value

        try:
            # 1. Store Base Feedback Entry
            fb_insert = text("INSERT INTO feedback (faculty_id, student_name, student_usn) VALUES (:f_id, :s_name, :s_usn)")
            result = db.session.execute(fb_insert, {'f_id': faculty_id, 's_name': student_name, 's_usn': student_usn})
            feedback_id = result.lastrowid
            
            # 2. Store Atomic Rating Metrics
            for q_id, rating in responses.items():
                resp_insert = text("INSERT INTO feedback_response (feedback_id, question_id, rating) VALUES (:fb_id, :q_id, :rate)")
                db.session.execute(resp_insert, {'fb_id': feedback_id, 'q_id': q_id, 'rate': rating})
                
            # 3. Store Optional Comment Form Block
            if comment_text and comment_text.strip():
                comm_insert = text("INSERT INTO comments (feedback_id, comment_text) VALUES (:fb_id, :c_text)")
                db.session.execute(comm_insert, {'fb_id': feedback_id, 'c_text': comment_text.strip()})
                
            db.session.commit()
            flash('Thank you! Your feedback has been successfully recorded.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while saving feedback: {str(e)}', 'danger')
            
        return redirect(url_for('student_panel'))

    # GET Request Logic
    faculties = db.session.execute(text("SELECT * FROM faculty")).fetchall()
    active_questions = db.session.execute(text("SELECT * FROM questions WHERE status='active'")).fetchall()
    return render_template('student.html', faculties=faculties, questions=active_questions)


# --- ADMIN ROUTE: AUTHENTICATION ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin_user = db.session.execute(text("SELECT * FROM admin WHERE username = :user"), {'user': username}).fetchone()
        
        if admin_user and admin_user.password_hash == password:
            session['admin_logged_in'] = True
            session['admin_username'] = admin_user.username
            flash('Successfully logged into dashboard panel.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials entered.', 'danger')
            
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out from dashboard.', 'info')
    return redirect(url_for('admin_login'))


# --- ADMIN ROUTE: METRICS DASHBOARD ---
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    # Read metrics stats via custom relational aggregate tracking functions
    total_fac = db.session.execute(text("SELECT COUNT(*) FROM faculty")).scalar() or 0
    total_q = db.session.execute(text("SELECT COUNT(*) FROM questions WHERE status='active'")).scalar() or 0
    total_fb = db.session.execute(text("SELECT COUNT(*) FROM feedback")).scalar() or 0
    avg_sys = db.session.execute(text("SELECT ROUND(AVG(rating), 2) FROM feedback_response")).scalar() or 0.00

    # Build Global Faculty Performance Breakdown
    fac_perf_query = text("""
        SELECT f.faculty_name, ROUND(AVG(fr.rating), 2) AS avg_rating
        FROM faculty f
        LEFT JOIN feedback fb ON f.faculty_id = fb.faculty_id
        LEFT JOIN feedback_response fr ON fb.feedback_id = fr.feedback_id
        GROUP BY f.faculty_id, f.faculty_name
        ORDER BY avg_rating DESC
    """)
    fac_performance = db.session.execute(fac_perf_query).fetchall()

    # Build Global System Distribution Metrics
    dist_query = text("""
        SELECT rating, COUNT(*) as count 
        FROM feedback_response 
        GROUP BY rating 
        ORDER BY rating ASC
    """)
    distribution = db.session.execute(dist_query).fetchall()
    
    # Process structure maps into dictionary configurations for chart parsers
    chart_data = {
        'fac_labels': [row.faculty_name for row in fac_performance],
        'fac_ratings': [float(row.avg_rating) if row.avg_rating else 0.0 for row in fac_performance],
        'dist_counts': [0] * 5
    }
    for row in distribution:
        if 1 <= row.rating <= 5:
            chart_data['dist_counts'][row.rating - 1] = row.count

    return render_template('admin_dashboard.html', total_fac=total_fac, total_q=total_q, 
                           total_fb=total_fb, avg_sys=avg_sys, chart_data=chart_data)


# --- ADMIN ROUTE: FACULTY CRUD MANAGEMENT ---
@app.route('/admin/faculty', methods=['GET', 'POST'])
def faculty_management():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('faculty_name')
        dept = request.form.get('department')
        subj = request.form.get('subject')
        
        if action == 'add':
            db.session.execute(text("INSERT INTO faculty (faculty_name, department, subject) VALUES (:name, :dept, :subj)"),
                               {'name': name, 'dept': dept, 'subj': subj})
        elif action == 'edit':
            f_id = request.form.get('faculty_id')
            db.session.execute(text("UPDATE faculty SET faculty_name=:name, department=:dept, subject=:subj WHERE faculty_id=:id"),
                               {'name': name, 'dept': dept, 'subj': subj, 'id': f_id})
        elif action == 'delete':
            f_id = request.form.get('faculty_id')
            db.session.execute(text("DELETE FROM faculty WHERE faculty_id=:id"), {'id': f_id})
            
        db.session.commit()
        flash('Faculty tracking record updated successfully.', 'success')
        return redirect(url_for('faculty_management'))
        
    faculties = db.session.execute(text("SELECT * FROM faculty")).fetchall()
    return render_template('faculty.html', faculties=faculties)


# --- ADMIN ROUTE: QUESTION SELECTION CONTROLLER ---
@app.route('/admin/questions', methods=['GET', 'POST'])
def question_management():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        text_content = request.form.get('question_text')
        
        if action == 'add':
            db.session.execute(text("INSERT INTO questions (question_text, status) VALUES (:txt, 'active')"), {'txt': text_content})
        elif action == 'toggle':
            q_id = request.form.get('question_id')
            curr_status = request.form.get('current_status')
            new_status = 'inactive' if curr_status == 'active' else 'active'
            db.session.execute(text("UPDATE questions SET status=:status WHERE question_id=:id"), {'status': new_status, 'id': q_id})
        elif action == 'delete':
            q_id = request.form.get('question_id')
            db.session.execute(text("DELETE FROM questions WHERE question_id=:id"), {'id': q_id})
            
        db.session.commit()
        flash('Evaluation inventory parameters synchronized.', 'success')
        return redirect(url_for('question_management'))
        
    questions = db.session.execute(text("SELECT * FROM questions")).fetchall()
    return render_template('questions.html', questions=questions)


# --- ADMIN ROUTE: REPORT MODULE ---
@app.route('/admin/reports')
def reports():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
        
    faculty_id = request.args.get('faculty_id')
    faculties = db.session.execute(text("SELECT * FROM faculty")).fetchall()
    
    report_data = None
    if faculty_id:
        try:
            # 1. Overall profile metric configurations
            meta_row = db.session.execute(text("SELECT * FROM faculty WHERE faculty_id=:id"), {'id': faculty_id}).fetchone()
            count = db.session.execute(text("SELECT COUNT(*) FROM feedback WHERE faculty_id=:id"), {'id': faculty_id}).scalar() or 0
            raw_score = db.session.execute(text("""
                SELECT ROUND(AVG(fr.rating), 2) FROM feedback_response fr 
                JOIN feedback f ON fr.feedback_id=f.feedback_id WHERE f.faculty_id=:id
            """), {'id': faculty_id}).scalar()
            # FIX: ROUND(AVG()) returns MySQL Decimal — cast to float to prevent serialization errors
            score = float(raw_score) if raw_score is not None else 0.00

            # Safe conversion for meta row
            meta = None
            if meta_row:
                meta = {
                    'faculty_id': meta_row[0],
                    'faculty_name': meta_row[1],
                    'department': meta_row[2],
                    'subject': meta_row[3]
                }

            # 2. Extract atomic question metric breakdown
            q_breakdown = db.session.execute(text("""
                SELECT q.question_text, ROUND(AVG(fr.rating),2) AS q_avg
                FROM questions q
                JOIN feedback_response fr ON q.question_id=fr.question_id
                JOIN feedback f ON fr.feedback_id=f.feedback_id
                WHERE f.faculty_id=:id
                GROUP BY q.question_id, q.question_text
            """), {'id': faculty_id}).fetchall()

            # 3. Pull associated contextual comments text blocks
            # FIX: 'submitted_at' column may not exist in the live DB — select only comment_text
            # and order by comment_id to avoid "Unknown column" OperationalError
            comms = db.session.execute(text("""
                SELECT c.comment_text FROM comments c
                JOIN feedback f ON c.feedback_id=f.feedback_id
                WHERE f.faculty_id=:id ORDER BY c.comment_id DESC
            """), {'id': faculty_id}).fetchall()

            # Safe breakdown for charts and loops
            radar_labels = []
            radar_scores = []
            clean_q_breakdown = []
            for r in q_breakdown:
                q_text = r[0] if r[0] else ""
                # FIX: ROUND(AVG()) returns Decimal — always cast to float
                q_avg = float(r[1]) if r[1] is not None else 0.0

                clean_q_breakdown.append({'question_text': q_text, 'q_avg': round(q_avg, 2)})
                short_text = q_text[:20] + '...' if len(q_text) > 20 else q_text
                radar_labels.append(short_text)
                radar_scores.append(q_avg)

            clean_comments = []
            for c in comms:
                clean_comments.append({'comment_text': c[0], 'submitted_at': 'N/A'})

            report_data = {
                'meta': meta,
                'count': count,
                'score': score,
                'q_breakdown': clean_q_breakdown,
                'comments': clean_comments,
                'radar_labels': radar_labels,
                'radar_scores': radar_scores
            }
        except Exception as e:
            db.session.rollback()
            flash(f'Error generating report: {str(e)}', 'danger')

    return render_template('reports.html', faculties=faculties, selected_id=faculty_id, report_data=report_data)