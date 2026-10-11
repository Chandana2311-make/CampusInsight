# CampusInsight Power BI Desktop Reporting Guide

This guide walks you through importing the synthetic, anonymized academic dataset into **Power BI Desktop** to build institutional dashboards and visual analytics.

> **Data Privacy Notice:** All student identifiers are strictly anonymized (`ANON_STU_001`, etc.). In accordance with institutional data governance policies, individual personal identifiers (names, contact info) are never exported into public or external analytical models.

---

## 1. Dataset Overview

- **Source File:** `powerbi/campus_insight_dataset.csv`
- **Rows:** 600 anonymized student-course assessment records
- **Features Included:**
  - `Student_ID`: Anonymized surrogate key
  - `Department`: Academic engineering discipline
  - `Semester`: Semester index (Sem 3, Sem 4, Sem 5)
  - `Subject_Code`, `Subject_Name`: Course identification
  - `Credits`: Course credit weighting (3 or 4 credits)
  - `Internal_Marks`: Continuous Internal Evaluation (CIE, Max 40)
  - `External_Marks`: Semester End Examination (SEE, Max 60)
  - `Total_Marks`: Aggregated score (Max 100)
  - `Percentage`: Normalized subject score
  - `Grade`: Letter grade (`O`, `A+`, `A`, `B+`, `B`, `C`, `P`, `F`)
  - `Grade_Points`: Grade points (10 to 0)
  - `Is_Passed`: Binary flag (1 = Cleared, 0 = Arrear/Not Cleared)

---

## 2. Step-by-Step Power BI Desktop Import

1. **Open Power BI Desktop**.
2. On the Home ribbon, click **Get Data** -> **Text/CSV**.
3. Browse to and select `CampusInsight/powerbi/campus_insight_dataset.csv`.
4. In the preview window, confirm:
   - File Origin: `65001: Unicode (UTF-8)`
   - Delimiter: `Comma`
   - Data Type Detection: `Based on first 200 rows`
5. Click **Transform Data** to open the Power Query Editor.
6. Verify Data Types:
   - `Student_ID`, `Department`, `Section`, `Subject_Code`, `Subject_Name`, `Grade`: `Text`
   - `Semester`, `Batch_Year`, `Credits`, `Grade_Points`, `Is_Passed`: `Whole Number`
   - `Internal_Marks`, `External_Marks`, `Total_Marks`, `Percentage`: `Decimal Number`
7. Click **Close & Apply**.

---

## 3. Recommended DAX Measures

Create a dedicated Measures table or add these DAX formulas to `campus_insight_dataset`:

### 1. Total Student Assessments
```dax
Total Assessments = COUNTROWS(campus_insight_dataset)
```

### 2. Overall Pass Rate Percentage
```dax
Pass Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(campus_insight_dataset), campus_insight_dataset[Is_Passed] = 1),
    COUNTROWS(campus_insight_dataset),
    0
) * 100
```

### 3. Average Total Marks
```dax
Subject Average Marks = AVERAGE(campus_insight_dataset[Total_Marks])
```

### 4. Average Internal (CIE) Marks
```dax
Avg CIE Marks = AVERAGE(campus_insight_dataset[Internal_Marks])
```

### 5. Average External (SEE) Marks
```dax
Avg SEE Marks = AVERAGE(campus_insight_dataset[External_Marks])
```

### 6. Weighted SGPA / CGPA
```dax
Weighted GPA = 
DIVIDE(
    SUMX(campus_insight_dataset, campus_insight_dataset[Grade_Points] * campus_insight_dataset[Credits]),
    SUM(campus_insight_dataset[Credits]),
    0
)
```

---

## 4. Building the Visualizations

### Visual 1: Executive KPI Cards (Top Banner)
- **Visual Type:** Card (New) or Multi-row Card
- **Fields:**
  - `[Pass Rate %]` (Format as `0.0%`)
  - `[Subject Average Marks]` (Format as `0.0 / 100`)
  - `[Weighted GPA]` (Format as `0.00 / 10.0`)
  - `[Total Assessments]`

### Visual 2: Grade Distribution
- **Visual Type:** Clustered Column Chart
- **X-axis:** `Grade` (Sort order: `O`, `A+`, `A`, `B+`, `B`, `C`, `P`, `F`)
- **Y-axis:** `Count of Student_ID`
- **Data Colors:** Accentuate `F` with Crimson/Red (`#EF4444`) and `O`/`A+` with Teal/Navy (`#0D9488`).

### Visual 3: Subject Performance & Pass-Rate Matrix
- **Visual Type:** Clustered Bar Chart or Matrix
- **Y-axis (Rows):** `Subject_Code`
- **X-axis (Values):** `[Subject Average Marks]`, `[Pass Rate %]`
- **Tooltip:** `Subject_Name`, `Avg CIE Marks`, `Avg SEE Marks`

### Visual 4: Semester-over-Semester Academic Trend
- **Visual Type:** Line Chart
- **X-axis:** `Semester`
- **Y-axis:** `[Weighted GPA]`, `[Pass Rate %]`
- **Legend:** `Department`

### Visual 5: CIE vs. SEE Assessment Correlation
- **Visual Type:** Scatter Chart
- **X-axis:** `Internal_Marks` (CIE)
- **Y-axis:** `External_Marks` (SEE)
- **Details:** `Student_ID`
- **Legend:** `Grade`

### Slicers
- Department Dropdown (`campus_insight_dataset[Department]`)
- Semester Buttons (`campus_insight_dataset[Semester]`)
- Section Slicer (`campus_insight_dataset[Section]`)
