"""
Generate Synthetic Power BI Dataset
Creates an anonymized, multi-semester college performance dataset for Power BI Desktop reporting.
"""
import csv
import random
from pathlib import Path

random.seed(42)

POWERBI_CSV_PATH = Path(__file__).resolve().parent / "campus_insight_dataset.csv"

DEPARTMENTS = ["Computer Science", "Information Science", "Electronics & Comm", "Mechanical Engg"]
SUBJECTS = [
    ("CS301", "Data Structures", 3, 4),
    ("CS302", "Digital Electronics", 3, 3),
    ("CS303", "Discrete Mathematics", 3, 4),
    ("CS401", "Design & Analysis of Algorithms", 4, 4),
    ("CS402", "Operating Systems", 4, 4),
    ("CS403", "Microcontrollers", 4, 3),
    ("CS501", "Database Management Systems", 5, 4),
    ("CS502", "Computer Networks", 5, 4),
    ("CS503", "Theory of Computation", 5, 3),
    ("CS504", "Software Engineering", 5, 3),
]

STUDENT_COUNT = 60
STUDENT_IDS = [f"ANON_STU_{i:03d}" for i in range(1, STUDENT_COUNT + 1)]

rows = []
for stu_id in STUDENT_IDS:
    dept = random.choice(DEPARTMENTS)
    sec = random.choice(["A", "B"])
    batch = 2022
    
    # Base academic ability factor (50 to 95)
    ability = random.gauss(72, 12)
    ability = max(35, min(96, ability))

    for sub_code, sub_name, sem, credits in SUBJECTS:
        # Semester noise
        sub_noise = random.uniform(-10, 10)
        perf = max(20, min(98, ability + sub_noise))

        # Max marks: 40 CIE, 60 SEE
        int_marks = round((perf / 100.0) * 40.0 + random.uniform(-2, 2), 1)
        int_marks = max(10.0, min(40.0, int_marks))

        # External marks
        ext_marks = round((perf / 100.0) * 60.0 + random.uniform(-4, 4), 1)
        ext_marks = max(12.0, min(60.0, ext_marks))

        tot_marks = round(int_marks + ext_marks, 1)
        pct = round(tot_marks, 1)

        # Pass criteria: internal >= 16, external >= 21, total >= 40
        is_passed = 1 if (int_marks >= 16.0 and ext_marks >= 21.0 and tot_marks >= 40.0) else 0

        if not is_passed:
            grade = "F"
            grade_points = 0
        elif pct >= 90:
            grade = "O"
            grade_points = 10
        elif pct >= 80:
            grade = "A+"
            grade_points = 9
        elif pct >= 70:
            grade = "A"
            grade_points = 8
        elif pct >= 60:
            grade = "B+"
            grade_points = 7
        elif pct >= 55:
            grade = "B"
            grade_points = 6
        elif pct >= 50:
            grade = "C"
            grade_points = 5
        else:
            grade = "P"
            grade_points = 4

        rows.append({
            "Student_ID": stu_id,
            "Department": dept,
            "Section": sec,
            "Batch_Year": batch,
            "Semester": sem,
            "Subject_Code": sub_code,
            "Subject_Name": sub_name,
            "Credits": credits,
            "Internal_Marks": int_marks,
            "External_Marks": ext_marks,
            "Total_Marks": tot_marks,
            "Percentage": pct,
            "Grade": grade,
            "Grade_Points": grade_points,
            "Is_Passed": is_passed,
            "Is_Published": 1
        })

fieldnames = list(rows[0].keys())
with open(POWERBI_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} synthetic anonymized rows in {POWERBI_CSV_PATH}")
