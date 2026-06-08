
# Faculty Feedback System

An automated, data-driven web application built to streamline academic evaluation loops. The system allows students to anonymously rate faculty members across key diagnostic metrics, while providing administrators with a powerful backend dashboard to manage faculty rosters, customize evaluation parameters, and track real-time performance scorecards.

---

## 🏢 System Architecture

The application utilizes a classic **Client-Server-Database (Three-Tier)** architecture. The lightweight Flask backend serves dynamic HTML templates, processes form compliance logic, and handles relational tracking queries directly with the local MySQL database instance.

```
         +---------------------------------------+
         |            Client Browser             |
         |  (HTML5 / CSS3 / Vanilla JavaScript)  |
         +---------------------------------------+
                        /          \
         (Student Portal)          (Admin Dashboard)
                      /              \
                     v                v
         +---------------------------------------+
         |         Flask Backend Engine          |
         |       (Python / Jinja2 Routes)        |
         +---------------------------------------+
                             |
                (PyMySQL Database Driver)
                             |
                             v
         +---------------------------------------+
         |      MySQL Relational Database        |
         |        (Persistent Storage)           |
         +---------------------------------------+

```

---

## 📊 Database Schema (ER Diagram)

The system relies on a strictly structured relational schema ensuring data integrity. It uses cascading foreign key checks (`ON DELETE CASCADE`) to tie individual evaluation responses and anonymous text comments back to their core faculty and survey question entities.

```
  +------------------+             +----------------------+
  |     FACULTY      |             |  FEEDBACK_RESPONSE   |
  +------------------+             +----------------------+
  | PK | faculty_id  |<----+       | PK | response_id     |
  |    | faculty_name|     |       | FK | feedback_id     |-----+
  |    | department  |     |       | FK | question_id     |--+  |
  |    | subject     |     |       |    | rating (1-5)    |  |  |
  +------------------+     |       +----------------------+  |  |
                           |                                 |  |
  +------------------+     |       +----------------------+  |  |
  |     FEEDBACK     |     |       |      QUESTIONS       |  |  |
  +------------------+     |       +----------------------+  |  |
  | PK | feedback_id |-----+       | PK | question_id     |<-+  |
  | FK | faculty_id  |             |    | question_text   |     |
  |    | timestamp   |             |    | status          |     |
  +------------------+             +----------------------+     |
           |                                                    |
           v                                                    |
  +------------------+                                          |
  |     COMMENTS     |                                          |
  +------------------+                                          |
  | PK | comment_id  |                                          |
  | FK | feedback_id |<-----------------------------------------+
  |    | comment_text|
  +------------------+

```

---

## 🔄 System Workflow & Data Flow

To demonstrate how data flows securely through the application from submission to aggregation, the system follows this operational sequence:

### 1. The Student Feedback Loop

1. **Request:** The student loads the homepage. The Flask server queries the `faculty` table to fetch the active CSE (AI) department list.
2. **Render:** The UI displays a dynamic form mapping each active professor to their assigned subject.
3. **Submission:** The student fills out the 1-to-5 star rating metrics and writes optional comments.
4. **Database Transaction:**
* A master record is created in the `feedback` table linked to the chosen `faculty_id`.
* Individual metric scores are mapped row-by-row into the `feedback_response` table.
* Descriptive remarks are stored independently in the `comments` table.



### 2. The Administrative Analytics Loop

1. **Authentication:** The Admin logs in using the session credentials gate (`admin` / `admin123`).
2. **Live Data Aggregation:** When the dashboard loads, the Flask app executes an internal relational query using SQL aggregation functions (`AVG()` and `ROUND()`).
3. **Scorecard Render:** The interface transforms raw database numbers into clean, real-time performance score cards and averages for each teacher.
4. **Inventory Management:** Administrators can add new staff or deactivate question entries directly from the dashboard, which instantly modifies the database state.

---

## ⚡ Tech Stack

* **Frontend UI:** Semantic HTML5, Flexible CSS Layouts, Vanilla JavaScript
* **Backend Engine:** Python, Flask Web Framework
* **Database Tier:** MySQL Relational Storage Core
* **Driver Layer:** PyMySQL Data Connector

---

## ⚙️ Key Feature Modules

### 👨‍🎓 Student Evaluation View

* **Dynamic UI Forms:** Automatic loading of the real-time CSE (AI) faculty roster directly from database parameters.
* **Anonymous Audits:** Submits evaluation ratings securely without capturing or mapping identifying student credentials.
* **Comprehensive Diagnostics:** Tracks multiple distinct diagnostic parameters simultaneously for a well-rounded appraisal.

### 🛡️ Administrative Console

* **Roster Onboarding:** Add, modify, or completely purge faculty members instantly via modular browser screens.
* **Diagnostic Controls:** Inject, pause, or deactivate individual evaluation metrics on the fly.
* **Aggregation Dashboards:** Displays automated live performance scorecards with calculated running averages.

---

To run:

python app.py
