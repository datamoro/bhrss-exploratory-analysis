# Superset Dashboard Guide — BRFSS 2024

## Objective

This guide provides instructions for creating analytical dashboards in Apache Superset that explore **social determinants of health** using BRFSS 2024 data. The dashboards are designed to reveal health disparities — a core concern in health informatics and public health policy.

---

## Dashboard Structure

### Dashboard 1: Health Overview
**Goal**: High-level view of population health status

### Dashboard 2: Socioeconomic Impact
**Goal**: Show how income and education affect health outcomes

### Dashboard 3: Behaviors and Health
**Goal**: Correlate lifestyle factors with chronic disease prevalence

### Dashboard 4: Mental Health
**Goal**: Deep dive into mental health and associated risk factors

---

## Dashboard 1: Health Overview

### Chart 1.1: Health Score by State

**Type**: Choropleth Map or Table

**Query**:
```sql
SELECT
    state,
    COUNT(*) as total_respondents,
    ROUND(AVG(CASE
        WHEN general_health IN ('1') THEN 100
        WHEN general_health IN ('2') THEN 75
        WHEN general_health IN ('3') THEN 50
        WHEN general_health IN ('4') THEN 25
        WHEN general_health IN ('5') THEN 0
        ELSE NULL
    END), 2) as health_score
FROM brfss_health_data_simple
WHERE general_health IS NOT NULL
GROUP BY state
ORDER BY health_score DESC;
```

---

### Chart 1.2: General Health Distribution

**Type**: Horizontal Bar Chart

**Query**:
```sql
SELECT
    CASE general_health
        WHEN '1' THEN 'Excellent'
        WHEN '2' THEN 'Very Good'
        WHEN '3' THEN 'Good'
        WHEN '4' THEN 'Fair'
        WHEN '5' THEN 'Poor'
    END as health_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM brfss_health_data_simple
WHERE general_health IS NOT NULL
GROUP BY general_health
ORDER BY general_health;
```

---

### Chart 1.3: Chronic Condition Prevalence

**Type**: Bar Chart

**Query**:
```sql
SELECT 'Diabetes' as condition,
       ROUND(SUM(CASE WHEN diabetes IN ('1','3') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as prevalence_pct
FROM brfss_health_data_simple WHERE diabetes IS NOT NULL

UNION ALL

SELECT 'Depression',
       ROUND(SUM(CASE WHEN depression = '1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM brfss_health_data_simple WHERE depression IS NOT NULL

UNION ALL

SELECT 'Arthritis',
       ROUND(SUM(CASE WHEN arthritis = '1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM brfss_health_data_simple WHERE arthritis IS NOT NULL

UNION ALL

SELECT 'Stroke',
       ROUND(SUM(CASE WHEN stroke = '1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM brfss_health_data_simple WHERE stroke IS NOT NULL

UNION ALL

SELECT 'Heart Attack',
       ROUND(SUM(CASE WHEN heart_attack = '1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM brfss_health_data_simple WHERE heart_attack IS NOT NULL

ORDER BY prevalence_pct DESC;
```

---

### Chart 1.4: Key KPIs

**Type**: Big Number

Sample queries:
```sql
-- % with cost barrier
SELECT ROUND(SUM(CASE WHEN cost_barrier = '1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct
FROM brfss_health_data_simple
WHERE cost_barrier IN ('1', '2');

-- % who exercise
SELECT ROUND(SUM(CASE WHEN exercise = '1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct
FROM brfss_health_data_simple
WHERE exercise IN ('1', '2');
```

---

## Dashboard 2: Socioeconomic Impact

### Chart 2.1: General Health by Income

**Type**: Stacked Bar Chart (100%)

```sql
SELECT
    income,
    general_health,
    COUNT(*) as count
FROM brfss_health_data_simple
WHERE general_health IS NOT NULL
  AND income IS NOT NULL
GROUP BY income, general_health
ORDER BY income, general_health;
```

**Expected insight**: Higher income correlates with better self-reported health.

---

### Chart 2.2: Cost Barrier by Income and Education

**Type**: Heatmap

```sql
SELECT
    income,
    education,
    ROUND(SUM(CASE WHEN cost_barrier = '1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct_cost_barrier
FROM brfss_health_data_simple
WHERE cost_barrier IN ('1', '2')
  AND income IS NOT NULL
  AND education IS NOT NULL
GROUP BY income, education;
```

---

### Chart 2.3: Poor Health Days by Education Level

**Type**: Bar Chart

```sql
SELECT
    education,
    COUNT(*) as n_respondents,
    ROUND(AVG(physical_health_days), 2) as avg_bad_physical_days,
    ROUND(AVG(mental_health_days), 2) as avg_bad_mental_days
FROM brfss_health_data_simple
WHERE physical_health_days IS NOT NULL
  AND mental_health_days IS NOT NULL
  AND education IS NOT NULL
GROUP BY education
ORDER BY education;
```

---

## Dashboard 3: Behaviors and Health

### Chart 3.1: Exercise vs. Chronic Conditions

**Type**: Grouped Bar Chart

```sql
SELECT
    exercise,
    ROUND(AVG(CASE WHEN diabetes IN ('1','3') THEN 1 ELSE 0 END) * 100, 2) as diabetes_pct,
    ROUND(AVG(CASE WHEN heart_attack = '1' THEN 1 ELSE 0 END) * 100, 2) as heart_attack_pct,
    ROUND(AVG(CASE WHEN stroke = '1' THEN 1 ELSE 0 END) * 100, 2) as stroke_pct
FROM brfss_health_data_simple
WHERE exercise IN ('1', '2')
  AND diabetes IS NOT NULL
  AND heart_attack IS NOT NULL
  AND stroke IS NOT NULL
GROUP BY exercise;
```

---

### Chart 3.2: Diabetes Prevalence by BMI Category

**Type**: Bar Chart

```sql
-- Note: BMI category is available in the main ETL (etl_brfss.py), not the simple pipeline.
-- Use the appropriate table depending on which ETL was run.
SELECT
    bmi_category,
    COUNT(*) as total,
    ROUND(SUM(CASE WHEN diabetes IN ('1','3') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as diabetes_pct
FROM brfss_health_data
WHERE bmi_category IS NOT NULL
  AND diabetes IS NOT NULL
GROUP BY bmi_category
ORDER BY bmi_category;
```

---

## Dashboard 4: Mental Health

### Chart 4.1: Distribution of Poor Mental Health Days

**Type**: Histogram

```sql
SELECT
    CASE
        WHEN mental_health_days = 0 THEN '0 days'
        WHEN mental_health_days BETWEEN 1 AND 7 THEN '1-7 days'
        WHEN mental_health_days BETWEEN 8 AND 14 THEN '8-14 days'
        WHEN mental_health_days BETWEEN 15 AND 21 THEN '15-21 days'
        WHEN mental_health_days BETWEEN 22 AND 30 THEN '22-30 days'
    END as days_range,
    COUNT(*) as count
FROM brfss_health_data_simple
WHERE mental_health_days IS NOT NULL
GROUP BY days_range
ORDER BY
    CASE days_range
        WHEN '0 days' THEN 1
        WHEN '1-7 days' THEN 2
        WHEN '8-14 days' THEN 3
        WHEN '15-21 days' THEN 4
        WHEN '22-30 days' THEN 5
    END;
```

---

### Chart 4.2: Depression by Income

**Type**: Grouped Bar Chart

```sql
SELECT
    income,
    ROUND(AVG(CASE WHEN depression = '1' THEN 1 ELSE 0 END) * 100, 2) as depression_pct
FROM brfss_health_data_simple
WHERE depression IN ('1', '2')
  AND income IS NOT NULL
GROUP BY income
ORDER BY income;
```

---

### Chart 4.3: Physical vs. Mental Health Correlation

**Type**: Scatter Plot

```sql
SELECT
    physical_health_days as x,
    mental_health_days as y,
    COUNT(*) as bubble_size
FROM brfss_health_data_simple
WHERE physical_health_days IS NOT NULL
  AND mental_health_days IS NOT NULL
GROUP BY physical_health_days, mental_health_days;
```

---

## Design Guidelines

### Color Palette

**Health Status**:
- Excellent: `#2ecc71` (green)
- Very Good: `#95e1d3`
- Good: `#f9ca24` (yellow)
- Fair: `#f39c12` (orange)
- Poor: `#e74c3c` (red)

**Behaviors**:
- Positive (exercise): `#3498db` (blue)
- Negative (smoking): `#e67e22` (orange)

### Layout

1. Use Markdown boxes for titles and narrative context
2. Place KPIs at the top for at-a-glance insights
3. Organize top-to-bottom: overview then detail
4. Leave whitespace between charts

### Interactivity

- Add filters for: State, Age Group, Income
- Enable drill-downs where applicable
- Configure cross-filtering between related charts

---

## Dashboard Checklist

- [ ] Clear, descriptive title
- [ ] Key KPIs at the top
- [ ] Consistent, meaningful color scheme
- [ ] Informative labels and tooltips
- [ ] Relevant filters available
- [ ] BRFSS source cited
- [ ] Acceptable loading time (<5s)

---

## Creation Workflow

1. Create Dataset in Superset pointing to the table
2. Validate queries in SQL Lab
3. Create individual Charts and save each
4. Assemble the Dashboard by dragging charts in
5. Configure global Filters
6. Test Cross-filtering
7. Adjust Layout for readability
8. Publish

---

Developed by Caio Moreira | 2024
