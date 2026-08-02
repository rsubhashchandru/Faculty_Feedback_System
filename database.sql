CREATE DATABASE IF NOT EXISTS faculty_feedback_db;
USE faculty_feedback_db;

-- 1. Admin Credentials (Default: username: admin , password: admin123)
CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- 2. Faculty Directory
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- 3. Evaluation Evaluation Questions
CREATE TABLE IF NOT EXISTS questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text VARCHAR(255) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active'
) ENGINE=InnoDB;

-- 4. Feedback Submissions Base Record
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    student_name VARCHAR(100) DEFAULT 'Anonymous',
    student_usn VARCHAR(20) DEFAULT 'N/A',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Individual Metric Responses (1 to 5 ratings mapped to questions)
CREATE TABLE IF NOT EXISTS feedback_response (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_id INT NOT NULL,
    question_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    CONSTRAINT unique_response UNIQUE (feedback_id, question_id)
) ENGINE=InnoDB;

-- 6. Open-text Comments Layer
CREATE TABLE IF NOT EXISTS comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- SEED SCRIPT FOR BASELINE RUN:
-- Login credentials: username = admin, password = admin123
INSERT INTO admin (username, password_hash) VALUES 
('admin', 'admin123');

INSERT INTO faculty (faculty_name, department, subject) VALUES 
('Dr. Alan Turing', 'Computer Science', 'DBMS'),
('Prof. Ada Lovelace', 'Computer Science', 'Software Engineering'),
('Dr. Richard Feynman', 'Information Science', 'Computer Networks');

INSERT INTO questions (question_text, status) VALUES 
('Faculty covers syllabus completely.', 'active'),
('Faculty explains concepts clearly.', 'active'),
('Faculty is punctual.', 'active'),
('Faculty encourages participation.', 'active'),
('Faculty responds to doubts effectively.', 'active');