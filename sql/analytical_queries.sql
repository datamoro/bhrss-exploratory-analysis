-- ================================================================
-- QUERIES ANALÍTICAS - BRFSS 2024 Health Data
-- Autor: Caio Moro
-- Descrição: Queries prontas para usar no Superset ou análises ad-hoc
-- ================================================================

-- ================================================================
-- 1. VISÃO GERAL DOS DADOS
-- ================================================================

-- Total de registros por estado
SELECT 
    state_code,
    COUNT(*) as total_records,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM public.brfss_health_data
GROUP BY state_code
ORDER BY total_records DESC;

-- Distribuição por faixa etária
SELECT 
    age_group,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct
FROM public.brfss_health_data
GROUP BY age_group
ORDER BY 
    CASE age_group
        WHEN '18-24' THEN 1
        WHEN '25-34' THEN 2
        WHEN '35-44' THEN 3
        WHEN '45-54' THEN 4
        WHEN '55-64' THEN 5
        WHEN '65+' THEN 6
        ELSE 7
    END;

-- ================================================================
-- 2. SAÚDE GERAL E DISPARIDADES
-- ================================================================

-- Saúde geral por nível de renda
SELECT 
    income_category,
    general_health,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY income_category), 2) as pct_within_income
FROM public.brfss_health_data
WHERE general_health NOT IN ('Unknown')
GROUP BY income_category, general_health
ORDER BY 
    CASE income_category
        WHEN '<$25,000' THEN 1
        WHEN '$25,000-$50,000' THEN 2
        WHEN '$50,000-$75,000' THEN 3
        WHEN '$75,000+' THEN 4
        ELSE 5
    END,
    CASE general_health
        WHEN 'Excellent' THEN 1
        WHEN 'Very good' THEN 2
        WHEN 'Good' THEN 3
        WHEN 'Fair' THEN 4
        WHEN 'Poor' THEN 5
    END;

-- Média de dias com saúde física ruim por educação
SELECT 
    education_level,
    COUNT(*) as n_respondents,
    ROUND(AVG(physical_health_bad_days), 2) as avg_bad_physical_days,
    ROUND(AVG(mental_health_bad_days), 2) as avg_bad_mental_days
FROM public.brfss_health_data
WHERE physical_health_bad_days IS NOT NULL
  AND mental_health_bad_days IS NOT NULL
GROUP BY education_level
ORDER BY 
    CASE education_level
        WHEN 'Did not graduate HS' THEN 1
        WHEN 'Graduated HS' THEN 2
        WHEN 'Some college' THEN 3
        WHEN 'College graduate' THEN 4
        ELSE 5
    END;

-- ================================================================
-- 3. ACESSO A CUIDADOS DE SAÚDE
-- ================================================================

-- Acesso a plano de saúde por demografia
SELECT 
    age_group,
    income_category,
    has_health_plan,
    COUNT(*) as count
FROM public.brfss_health_data
WHERE has_health_plan IN ('Yes', 'No')
GROUP BY age_group, income_category, has_health_plan
ORDER BY age_group, income_category;

-- Barreira de custo médico por raça e renda
SELECT 
    race,
    income_category,
    medical_cost_barrier,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY race, income_category), 2) as pct
FROM public.brfss_health_data
WHERE medical_cost_barrier IN ('Yes', 'No')
GROUP BY race, income_category, medical_cost_barrier
ORDER BY race, income_category;

-- ================================================================
-- 4. COMPORTAMENTOS DE SAÚDE
-- ================================================================

-- Status de exercício físico por faixa etária
SELECT 
    age_group,
    exercises,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY age_group), 2) as pct_within_age
FROM public.brfss_health_data
WHERE exercises IN ('Yes', 'No')
GROUP BY age_group, exercises
ORDER BY age_group;

-- Combinação de comportamentos de risco
SELECT 
    CASE 
        WHEN smoking_status IN ('Current smoker (daily)', 'Current smoker (some days)') THEN 'Smoker'
        ELSE 'Non-smoker'
    END as smoker_status,
    binge_drinking,
    exercises,
    bmi_category,
    COUNT(*) as count
FROM public.brfss_health_data
WHERE binge_drinking IN ('Yes', 'No')
  AND exercises IN ('Yes', 'No')
  AND bmi_category != 'Unknown'
GROUP BY smoker_status, binge_drinking, exercises, bmi_category
ORDER BY count DESC
LIMIT 20;

-- ================================================================
-- 5. CONDIÇÕES CRÔNICAS
-- ================================================================

-- Prevalência de condições crônicas
SELECT 
    'Diabetes' as condition,
    SUM(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END) as positive_cases,
    COUNT(*) as total,
    ROUND(SUM(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as prevalence_pct
FROM public.brfss_health_data
WHERE has_diabetes != 'Unknown'

UNION ALL

SELECT 
    'Stroke',
    SUM(CASE WHEN had_stroke = 'Yes' THEN 1 ELSE 0 END),
    COUNT(*),
    ROUND(SUM(CASE WHEN had_stroke = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM public.brfss_health_data
WHERE had_stroke != 'Unknown'

UNION ALL

SELECT 
    'Heart Attack',
    SUM(CASE WHEN had_heart_attack = 'Yes' THEN 1 ELSE 0 END),
    COUNT(*),
    ROUND(SUM(CASE WHEN had_heart_attack = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM public.brfss_health_data
WHERE had_heart_attack != 'Unknown'

UNION ALL

SELECT 
    'Depression',
    SUM(CASE WHEN had_depression = 'Yes' THEN 1 ELSE 0 END),
    COUNT(*),
    ROUND(SUM(CASE WHEN had_depression = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM public.brfss_health_data
WHERE had_depression != 'Unknown'

UNION ALL

SELECT 
    'Arthritis',
    SUM(CASE WHEN has_arthritis = 'Yes' THEN 1 ELSE 0 END),
    COUNT(*),
    ROUND(SUM(CASE WHEN has_arthritis = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM public.brfss_health_data
WHERE has_arthritis != 'Unknown';

-- Comorbidades: múltiplas condições crônicas
SELECT 
    (CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END +
     CASE WHEN had_stroke = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN had_heart_attack = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN had_depression = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN has_arthritis = 'Yes' THEN 1 ELSE 0 END) as num_chronic_conditions,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct
FROM public.brfss_health_data
GROUP BY num_chronic_conditions
ORDER BY num_chronic_conditions;

-- ================================================================
-- 6. ANÁLISES MULTIDIMENSIONAIS
-- ================================================================

-- Diabetes por IMC e exercício
SELECT 
    bmi_category,
    exercises,
    COUNT(*) as total,
    SUM(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END) as diabetes_cases,
    ROUND(SUM(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as diabetes_pct
FROM public.brfss_health_data
WHERE bmi_category != 'Unknown'
  AND exercises IN ('Yes', 'No')
  AND has_diabetes != 'Unknown'
GROUP BY bmi_category, exercises
ORDER BY bmi_category, exercises;

-- Saúde mental por renda e acesso a cuidados
SELECT 
    income_category,
    has_health_plan,
    COUNT(*) as n,
    ROUND(AVG(mental_health_bad_days), 2) as avg_bad_mental_days,
    ROUND(AVG(CASE WHEN had_depression = 'Yes' THEN 1 ELSE 0 END), 3) as depression_rate
FROM public.brfss_health_data
WHERE mental_health_bad_days IS NOT NULL
  AND has_health_plan IN ('Yes', 'No')
  AND had_depression IN ('Yes', 'No')
GROUP BY income_category, has_health_plan
ORDER BY income_category, has_health_plan;

-- ================================================================
-- 7. MÉTRICAS DE QUALIDADE DOS DADOS
-- ================================================================

-- Completude dos dados por variável
SELECT 
    'age_group' as variable,
    COUNT(*) as total,
    SUM(CASE WHEN age_group = 'Unknown' THEN 1 ELSE 0 END) as missing,
    ROUND(SUM(CASE WHEN age_group != 'Unknown' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completeness_pct
FROM public.brfss_health_data

UNION ALL

SELECT 
    'general_health',
    COUNT(*),
    SUM(CASE WHEN general_health = 'Unknown' THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN general_health != 'Unknown' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM public.brfss_health_data

UNION ALL

SELECT 
    'physical_health_bad_days',
    COUNT(*),
    SUM(CASE WHEN physical_health_bad_days IS NULL THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN physical_health_bad_days IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM public.brfss_health_data;

-- ================================================================
-- 8. EXPORTS PARA ANÁLISES EXTERNAS (opcional)
-- ================================================================

-- Dataset agregado para dashboard principal
CREATE OR REPLACE VIEW public.dashboard_summary AS
SELECT 
    state_code,
    age_group,
    sex,
    income_category,
    COUNT(*) as n_respondents,
    
    -- Saúde geral
    ROUND(AVG(CASE WHEN general_health IN ('Excellent', 'Very good') THEN 1 ELSE 0 END), 3) as pct_good_health,
    ROUND(AVG(physical_health_bad_days), 2) as avg_bad_physical_days,
    ROUND(AVG(mental_health_bad_days), 2) as avg_bad_mental_days,
    
    -- Acesso
    ROUND(AVG(CASE WHEN has_health_plan = 'Yes' THEN 1 ELSE 0 END), 3) as pct_has_insurance,
    ROUND(AVG(CASE WHEN medical_cost_barrier = 'Yes' THEN 1 ELSE 0 END), 3) as pct_cost_barrier,
    
    -- Comportamentos
    ROUND(AVG(CASE WHEN exercises = 'Yes' THEN 1 ELSE 0 END), 3) as pct_exercises,
    ROUND(AVG(CASE WHEN smoking_status IN ('Current smoker (daily)', 'Current smoker (some days)') THEN 1 ELSE 0 END), 3) as pct_smoker,
    
    -- Condições
    ROUND(AVG(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END), 3) as pct_diabetes,
    ROUND(AVG(CASE WHEN had_depression = 'Yes' THEN 1 ELSE 0 END), 3) as pct_depression
    
FROM public.brfss_health_data
GROUP BY state_code, age_group, sex, income_category;

-- ================================================================
-- FIM DAS QUERIES
-- ================================================================
