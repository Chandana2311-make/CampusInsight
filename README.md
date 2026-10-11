<p align="center">
  <img src="assets/campusinsight_logo.svg" alt="CampusInsight Logo" width="460">
</p>

# 🎓 CampusInsight
### Student Result Analysis & Academic Improvement System

CampusInsight is a secure, layered academic intelligence system designed for colleges and universities. Built with **Python**, **Streamlit**, **SQLite**, **Pandas**, and **Plotly**, it enables departments to evaluate semester-end examinations, enforce institutional passing cutoffs, maintain immutable audit trails, and deliver personalized, evidence-grounded academic recovery roadmaps to students.

---

## 🏛️ System Architecture

CampusInsight adheres to strict separation of concerns across a clean, modular 4-tier architecture:

```
CampusInsight/
├── assets/                    # Official vector branding artwork & favicons
│   ├── campusinsight_logo.svg          # Primary scalable brand logo
│   ├── campusinsight_sidebar_logo.svg  # High-contrast dark sidebar emblem
│   └── favicon.svg                     # Browser tab favicon mark
├── app.py                     # Streamlit application entrypoint & role-based router
├── config.py                  # University grading criteria, passing rules, theme tokens
├── database/
│   ├── connection.py          # SQLite connection manager with WAL mode & foreign keys
│   ├── schema.sql             # Relational DDL (users, students, subjects, results, etc.)
│   ├── init_db.py             # Schema initialisation and table migration verification
│   └── seed_data.py           # Synthetic demonstration college dataset
├── repositories/              # Low-level parameterized data access layer
│   ├── user_repository.py     # User credentials & accounts
│   ├── student_repository.py  # Student profiles (USN, branch, semester, section)
│   ├── faculty_repository.py  # Faculty course allocations
│   ├── subject_repository.py  # Course configurations & credit thresholds
│   ├── result_repository.py   # Student marks, publishing flags & acknowledgements
│   ├── query_repository.py    # Discrepancy query lifecycle
│   ├── assessment_repository.py # Topic-level quiz and test evidence
│   ├── improvement_repository.py # Improvement plans & practice logs
│   └── audit_repository.py    # Immutable audit logging
├── services/                  # Business logic & security policy enforcement
│   ├── auth_service.py        # PBKDF2 password hashing & role authentication
│   ├── grading_service.py     # Configurable passing rules, grade scales, SGPA/CGPA
│   ├── result_service.py      # Flexible CSV validation, publishing controls & mark updates
│   ├── query_service.py       # Submitted -> Under Review -> Resolved/Rejected
│   ├── improvement_service.py # Grounded rule-based recommendation engine (Rules 1-6)
│   └── analytics_service.py   # Pass %, class averages, grade distributions, risk flags
├── ui/                        # Reusable Streamlit SaaS interface
│   ├── styles.py              # CSS design tokens & high-contrast button styling
│   ├── components.py          # Logo renderer, KPI metric cards, badges, banners
│   ├── charts.py              # Interactive Plotly chart builders
│   ├── pages_student/         # Student portal views (Overview, Results, Plan, Queries)
│   └── pages_faculty/         # Faculty portal views (Roster, CSV, Analytics, Support, Audit)
├── sample_data/               # Valid and invalid test CSV files
├── powerbi/                   # Anonymized dataset & Power BI Desktop reporting guide
└── tests/                     # Comprehensive pytest unit and permission test suite
```

---

## 📊 Dataset Information

### 1. Source & Nature of Data
All default demonstration datasets bundled with CampusInsight are **100% synthetic**. They were systematically generated specifically for this software engineering project to enable thorough evaluation of the recommendation engine, security boundaries, and analytics without exposing any real student personal information or violating educational privacy standards.

> **Privacy & Attribution Notice:** No data was scraped, harvested, or collected from any real college, university, or actual student. All student names, USNs (University Seat Numbers), email addresses, marks, and topic assessment scores are purely synthetic demonstration records.

### 2. Bundled Datasets & Files

| Dataset / File Path | Rows | Columns | Description & Purpose |
|---|---|---|---|
| [`database/seed_data.py`](database/seed_data.py) | 55 Results | Relational DB | Seed script populating SQLite with 10 user accounts (2 faculty, 8 students), 8 courses, 55 multi-semester examination results, 6 topic assessment scores, 2 discrepancy queries, and 3 audit logs. |
| [`sample_data/valid_marks_upload.csv`](sample_data/valid_marks_upload.csv) | 8 | 4 | Clean sample CSV for faculty to test batch uploading valid marks for enrolled Semester 5 Computer Science students (`1CI22CS101` to `1CI22CS108`). |
| [`sample_data/invalid_marks_sample.csv`](sample_data/invalid_marks_sample.csv) | 6 | 4 | Test CSV containing deliberate edge cases (out-of-range marks, negative values, duplicate USN, unregistered student) to verify the error preview table. |
| [`powerbi/campus_insight_dataset.csv`](powerbi/campus_insight_dataset.csv) | 600 | 16 | Cross-departmental multi-semester academic performance dataset across 60 anonymized students (`ANON_STU_001` to `ANON_STU_060`) for Power BI Desktop reporting. |

### 3. Fields & Descriptions

#### Academic Results (`sample_data/valid_marks_upload.csv` & SQLite `results`):
- `USN`: Student University Seat Number / Roll Number (e.g. `1CI22CS101`).
- `Internal`: Continuous Internal Evaluation score (CIE, Range: 0.0 to 40.0; Pass threshold: ≥ 16.0 / 40%).
- `External`: Semester End Examination score (SEE, Range: 0.0 to 60.0; Pass threshold: ≥ 21.0 / 60%).
- `Is_Absent`: Binary flag (`0` = Present, `1` = Absent for exam).
- `Total_Marks`: Aggregated score (`Internal + External`, Range: 0.0 to 100.0; Pass threshold: ≥ 40.0 / 100%).
- `Grade`: Computed letter grade (`O`, `A+`, `A`, `B+`, `B`, `C`, `P`, `F`).
- `Grade_Points`: 10-point scale grade points (`10` for O down to `0` for F).
- `Is_Passed`: Binary clearance flag (`1` = Cleared, `0` = Not cleared / Arrear).

#### Power BI Anonymized Dataset (`powerbi/campus_insight_dataset.csv`):
Includes additional institutional dimensions: `Department`, `Section`, `Batch_Year`, `Semester`, `Subject_Code`, `Subject_Name`, `Credits`, `Percentage`, and `Is_Published`.

### 4. Limitations
- **Synthetic Distribution:** Scores are modeled around a Gaussian distribution with a mean of ~72% and a standard deviation of 12%, with deliberate outliers added to test all 6 improvement engine rules.
- **Controlled Edge Cases:** The dataset intentionally includes engineered academic scenarios:
  - Student `1CI22CS103` (Chirag Nair) failed `CS503` (SEE = 18/60) to test **Rule 1 (Subject Recovery)** with topic-level quiz evidence.
  - Student `1CI22CS104` (Divya Kulkarni) scored low CIE (17/40) in `CS501` to test **Rule 2 (Internal Reinforcement)**.
  - Student `1CI22CS105` (Esha Menon) scored high CIE (35/40) but lower SEE (25/60) in `CS502` to test **Rule 3 (Exam Technique)**.
  - Course `CS505` is saved as **Unpublished** to test **Rule 5 (Unpublished Result Resolution)** and student data isolation.

### 5. Optional College CSV Import Workflow
While the synthetic demonstration dataset is loaded by default, **authorized faculty can upload their college's official mark sheets** via the Faculty Portal:
1. Log in with a faculty account (e.g. `dr.sharma`).
2. Navigate to **📊 Result Management** -> **📤 Authorized College CSV Import**.
3. Download the official blank CSV template (`campusinsight_marks_template.csv`) with the button provided.
4. Upload your departmental CSV file. The system accepts flexible column header variations:
   - **Student ID:** `USN`, `Roll_No`, `Reg_No`, or `Student_ID`
   - **Internal Marks:** `Internal`, `CIE`, `Internal_Marks`, or `IA_Marks`
   - **External Exam:** `External`, `SEE`, `External_Marks`, or `University_Marks`
   - **Absentee Status:** `Is_Absent` or `Absent`
5. Review the validation summary and preview any invalid rows.
6. Click **📥 Import Valid Rows**. The records are imported as **UNPUBLISHED** so faculty can review them before releasing them to students via the **Explicit Publication Control** tab.

---

## 🔒 Security & Data Governance

1. **Password Hashing:** Passwords are never stored in plaintext; hashed using **PBKDF2-HMAC-SHA256** with unique salts and 100,000 iterations.
2. **Student Isolation:** Students can access only their own results and discrepancy queries.
3. **Faculty Isolation:** Faculty can view and modify results *only* for courses and sections officially assigned to them.
4. **Mandatory Mark Change Justification:** Any mark change requires a justification reason of at least 5 characters.
5. **Immutable Audit Trail:** All mark amendments, bulk CSV imports, publication status changes, and query resolutions record actor, timestamp, prior value, updated value, and reason.
6. **Unpublished Results Guard:** Results imported via CSV remain unpublished by default and are completely hidden from student profiles until authorized faculty explicitly release them.
7. **Safeguarded Acknowledgement:** Students may formally confirm inspecting their results; confirming receipt does **not** waive their right to submit an evaluation query.

---

## 🚀 Quick Start (Windows PowerShell)

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Open PowerShell in the Project Directory
```powershell
cd "c:\Users\Chandana P\Downloads\CampusInsight"
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Seed the Database
```powershell
python database/seed_data.py
```

### 5. Run the Test Suite
Verify that all unit, permission, and workflow tests pass:
```powershell
python -m pytest tests/ -v
```

### 6. Launch the Streamlit Application
```powershell
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

---

## 👥 Demo Accounts (Local Evaluation)

Use the convenient **One-Click Demo Profiles** selector on the login screen or enter these credentials:

| Role | Username | Password | Persona & Purpose |
|---|---|---|---|
| **Faculty** | `dr.sharma` | `Password123!` | Dr. Ramesh Sharma (Instructor for CS501 & CS503) |
| **Faculty** | `prof.anita` | `Password123!` | Prof. Anita Deshmukh (Instructor for CS502 & CS504) |
| **Student** | `usn101` | `Student123!` | Aarav Patel (Top performer, 1CI22CS101) |
| **Student** | `usn102` | `Student123!` | Bhavya Rao (High achiever, 1CI22CS102) |
| **Student** | `usn103` | `Student123!` | Chirag Nair (Needs recovery plan in CS503, 1CI22CS103) |
| **Student** | `usn104` | `Student123!` | Divya Kulkarni (Low internal score in CS501, 1CI22CS104) |
| **Student** | `usn105` | `Student123!` | Esha Menon (Strong CIE, low SEE disparity in CS502) |

---

## 🧠 Academic Improvement Engine (Rules 1 – 6)

Located in [`services/improvement_service.py`](services/improvement_service.py), the recommendation engine uses supportive, non-stigmatizing language and generates plans grounded strictly in verified assessment evidence:

- **Rule 1 (Failed Subject):** Formulates an intensive recovery plan, past-paper drills, and tutorial reviews. If topic assessment evidence exists, prioritizes verified weak modules (e.g. *Turing Machines*).
- **Rule 2 (Low Internal Score):** Suggests assignment completion, faculty office hours, and foundational practice.
- **Rule 3 (Strong CIE, Weak SEE):** Identifies examination execution hurdles and suggests 3-hour timed simulations.
- **Rule 4 (Declining Semester Trend):** Flags multi-semester SGPA dips and recommends a 1-on-1 mentor session.
- **Rule 5 (Absent / Unpublished):** Directs students to administrative resolution without labeling them failed.
- **Rule 6 (Passed Below Target):** Suggests targeted elevation to bridge the gap to their target SGPA.

---

## 📊 Power BI Desktop Integration

A synthetic 600-row anonymized dataset is available in `powerbi/campus_insight_dataset.csv`. Follow [`powerbi/README.md`](powerbi/README.md) to set up:
- Pass Rate % and Average Marks DAX measures
- Multi-semester SGPA progression line charts
- Grade distribution clustered column visuals
- CIE vs. SEE correlation scatter plots
