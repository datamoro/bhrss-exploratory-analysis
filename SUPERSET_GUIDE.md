# 📊 Superset Dashboard Guide - BRFSS 2024

## 🎯 Objetivo

Este guia fornece instruções detalhadas para criar dashboards impactantes no Apache Superset, contando a história dos "Determinantes Sociais de Saúde nos EUA".

---

## 🏗️ Estrutura de Dashboards Recomendada

### Dashboard 1: 🏥 Panorama Geral de Saúde
**Objetivo**: Visão de alto nível da saúde da população

### Dashboard 2: 💰 Impacto Socioeconômico
**Objetivo**: Mostrar como renda e educação afetam saúde

### Dashboard 3: 🏃 Comportamentos e Saúde
**Objetivo**: Correlação entre lifestyle e condições crônicas

### Dashboard 4: 🧠 Saúde Mental
**Objetivo**: Deep dive em saúde mental e fatores associados

---

## 📊 Dashboard 1: Panorama Geral de Saúde

### Chart 1.1: Mapa de Saúde Geral por Estado

**Tipo**: Choropleth Map (se disponível) ou Table

**Query**:
```sql
SELECT 
    state_code,
    COUNT(*) as total_respondents,
    ROUND(AVG(CASE 
        WHEN general_health IN ('Excellent', 'Very good') THEN 100
        WHEN general_health = 'Good' THEN 60
        WHEN general_health = 'Fair' THEN 30
        WHEN general_health = 'Poor' THEN 0
        ELSE NULL
    END), 2) as health_score
FROM public.brfss_health_data
WHERE general_health != 'Unknown'
GROUP BY state_code
ORDER BY health_score DESC;
```

**Configuração**:
- Color Scale: Verde (bom) → Amarelo → Vermelho (ruim)
- Tooltip: Mostrar score e total de respondentes

---

### Chart 1.2: Distribuição de Saúde Geral

**Tipo**: Bar Chart (Horizontal)

**Query**:
```sql
SELECT 
    general_health,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM public.brfss_health_data
WHERE general_health != 'Unknown'
GROUP BY general_health
ORDER BY 
    CASE general_health
        WHEN 'Excellent' THEN 1
        WHEN 'Very good' THEN 2
        WHEN 'Good' THEN 3
        WHEN 'Fair' THEN 4
        WHEN 'Poor' THEN 5
    END;
```

**Configuração**:
- Cores: Gradient de verde a vermelho
- Label: Mostrar percentage
- Sort: Excellent → Poor

---

### Chart 1.3: Top 5 Condições Crônicas

**Tipo**: Bar Chart

**Query**:
```sql
SELECT 
    condition,
    prevalence_pct
FROM (
    SELECT 'Diabetes' as condition, 
           ROUND(SUM(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as prevalence_pct
    FROM public.brfss_health_data WHERE has_diabetes != 'Unknown'
    
    UNION ALL
    
    SELECT 'Arthritis',
           ROUND(SUM(CASE WHEN has_arthritis = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
    FROM public.brfss_health_data WHERE has_arthritis != 'Unknown'
    
    UNION ALL
    
    SELECT 'Depression',
           ROUND(SUM(CASE WHEN had_depression = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
    FROM public.brfss_health_data WHERE had_depression != 'Unknown'
    
    UNION ALL
    
    SELECT 'Stroke',
           ROUND(SUM(CASE WHEN had_stroke = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
    FROM public.brfss_health_data WHERE had_stroke != 'Unknown'
    
    UNION ALL
    
    SELECT 'Heart Attack',
           ROUND(SUM(CASE WHEN had_heart_attack = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
    FROM public.brfss_health_data WHERE had_heart_attack != 'Unknown'
) subq
ORDER BY prevalence_pct DESC;
```

---

### Chart 1.4: KPIs Principais

**Tipo**: Big Number with Trendline (ou Metric)

**Query para % com Plano de Saúde**:
```sql
SELECT 
    ROUND(SUM(CASE WHEN has_health_plan = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct
FROM public.brfss_health_data
WHERE has_health_plan IN ('Yes', 'No');
```

**Outros KPIs**:
- % que faz exercício
- % com barreira de custo médico
- Média de dias com saúde mental ruim
- Média de dias com saúde física ruim

---

## 📊 Dashboard 2: Impacto Socioeconômico

### Chart 2.1: Saúde Geral por Renda

**Tipo**: Stacked Bar Chart (100%)

**Query**:
```sql
SELECT 
    income_category,
    general_health,
    COUNT(*) as count
FROM public.brfss_health_data
WHERE general_health != 'Unknown'
  AND income_category != 'Unknown'
GROUP BY income_category, general_health
ORDER BY 
    CASE income_category
        WHEN '<$25,000' THEN 1
        WHEN '$25,000-$50,000' THEN 2
        WHEN '$50,000-$75,000' THEN 3
        WHEN '$75,000+' THEN 4
    END;
```

**Insight esperado**: Maior renda = melhor saúde

---

### Chart 2.2: Acesso a Plano de Saúde por Renda

**Tipo**: Line Chart

**Query**:
```sql
SELECT 
    income_category,
    ROUND(SUM(CASE WHEN has_health_plan = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct_with_insurance
FROM public.brfss_health_data
WHERE has_health_plan IN ('Yes', 'No')
  AND income_category != 'Unknown'
GROUP BY income_category
ORDER BY 
    CASE income_category
        WHEN '<$25,000' THEN 1
        WHEN '$25,000-$50,000' THEN 2
        WHEN '$50,000-$75,000' THEN 3
        WHEN '$75,000+' THEN 4
    END;
```

---

### Chart 2.3: Barreira de Custo por Demografia

**Tipo**: Heatmap

**Query**:
```sql
SELECT 
    income_category,
    education_level,
    ROUND(SUM(CASE WHEN medical_cost_barrier = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct_cost_barrier
FROM public.brfss_health_data
WHERE medical_cost_barrier IN ('Yes', 'No')
  AND income_category != 'Unknown'
  AND education_level != 'Unknown'
GROUP BY income_category, education_level;
```

---

### Chart 2.4: Dias com Saúde Ruim por Educação

**Tipo**: Box Plot ou Bar Chart

**Query**:
```sql
SELECT 
    education_level,
    ROUND(AVG(physical_health_bad_days), 2) as avg_bad_physical_days,
    ROUND(AVG(mental_health_bad_days), 2) as avg_bad_mental_days
FROM public.brfss_health_data
WHERE physical_health_bad_days IS NOT NULL
  AND mental_health_bad_days IS NOT NULL
  AND education_level != 'Unknown'
GROUP BY education_level
ORDER BY 
    CASE education_level
        WHEN 'Did not graduate HS' THEN 1
        WHEN 'Graduated HS' THEN 2
        WHEN 'Some college' THEN 3
        WHEN 'College graduate' THEN 4
    END;
```

---

## 📊 Dashboard 3: Comportamentos e Saúde

### Chart 3.1: Exercício vs Condições Crônicas

**Tipo**: Grouped Bar Chart

**Query**:
```sql
SELECT 
    exercises,
    ROUND(AVG(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END) * 100, 2) as diabetes_pct,
    ROUND(AVG(CASE WHEN had_heart_attack = 'Yes' THEN 1 ELSE 0 END) * 100, 2) as heart_attack_pct,
    ROUND(AVG(CASE WHEN had_stroke = 'Yes' THEN 1 ELSE 0 END) * 100, 2) as stroke_pct
FROM public.brfss_health_data
WHERE exercises IN ('Yes', 'No')
  AND has_diabetes != 'Unknown'
  AND had_heart_attack != 'Unknown'
  AND had_stroke != 'Unknown'
GROUP BY exercises;
```

---

### Chart 3.2: IMC vs Diabetes

**Tipo**: Bar Chart

**Query**:
```sql
SELECT 
    bmi_category,
    COUNT(*) as total,
    ROUND(SUM(CASE WHEN has_diabetes IN ('Yes', 'Yes (pregnancy)') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as diabetes_pct
FROM public.brfss_health_data
WHERE bmi_category != 'Unknown'
  AND has_diabetes != 'Unknown'
GROUP BY bmi_category
ORDER BY 
    CASE bmi_category
        WHEN 'Underweight' THEN 1
        WHEN 'Normal weight' THEN 2
        WHEN 'Overweight' THEN 3
        WHEN 'Obese' THEN 4
    END;
```

---

### Chart 3.3: Comportamentos de Risco Combinados

**Tipo**: Sunburst Chart ou Sankey Diagram

**Query**:
```sql
SELECT 
    CASE 
        WHEN smoking_status IN ('Current smoker (daily)', 'Current smoker (some days)') THEN 'Smoker'
        ELSE 'Non-smoker'
    END as smoker,
    exercises,
    bmi_category,
    COUNT(*) as count
FROM public.brfss_health_data
WHERE exercises IN ('Yes', 'No')
  AND bmi_category != 'Unknown'
GROUP BY smoker, exercises, bmi_category
ORDER BY count DESC
LIMIT 20;
```

---

## 📊 Dashboard 4: Saúde Mental

### Chart 4.1: Distribuição de Dias com Saúde Mental Ruim

**Tipo**: Histogram

**Query**:
```sql
SELECT 
    CASE 
        WHEN mental_health_bad_days = 0 THEN '0 days'
        WHEN mental_health_bad_days BETWEEN 1 AND 7 THEN '1-7 days'
        WHEN mental_health_bad_days BETWEEN 8 AND 14 THEN '8-14 days'
        WHEN mental_health_bad_days BETWEEN 15 AND 21 THEN '15-21 days'
        WHEN mental_health_bad_days BETWEEN 22 AND 30 THEN '22-30 days'
    END as days_range,
    COUNT(*) as count
FROM public.brfss_health_data
WHERE mental_health_bad_days IS NOT NULL
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

### Chart 4.2: Depressão por Fatores Socioeconômicos

**Tipo**: Grouped Bar Chart

**Query**:
```sql
SELECT 
    income_category,
    education_level,
    ROUND(AVG(CASE WHEN had_depression = 'Yes' THEN 1 ELSE 0 END) * 100, 2) as depression_pct
FROM public.brfss_health_data
WHERE had_depression IN ('Yes', 'No')
  AND income_category != 'Unknown'
  AND education_level != 'Unknown'
GROUP BY income_category, education_level
ORDER BY depression_pct DESC;
```

---

### Chart 4.3: Correlação Saúde Física vs Mental

**Tipo**: Scatter Plot

**Query**:
```sql
SELECT 
    physical_health_bad_days as x,
    mental_health_bad_days as y,
    COUNT(*) as bubble_size
FROM public.brfss_health_data
WHERE physical_health_bad_days IS NOT NULL
  AND mental_health_bad_days IS NOT NULL
GROUP BY physical_health_bad_days, mental_health_bad_days;
```

---

## 🎨 Dicas de Design

### Paleta de Cores Recomendada

**Saúde Geral**:
- Excellent: `#2ecc71` (verde)
- Very Good: `#95e1d3`
- Good: `#f9ca24` (amarelo)
- Fair: `#f39c12` (laranja)
- Poor: `#e74c3c` (vermelho)

**Comportamentos**:
- Positive (exercício): `#3498db` (azul)
- Negative (fumo): `#e67e22` (laranja)

**Demografia**:
- Use cores neutras e distintas

### Layout

1. **Headers**: Use Markdown boxes para títulos e contexto
2. **KPIs**: Coloque no topo para quick insights
3. **Flow**: Organize de cima para baixo, geral → específico
4. **Whitespace**: Deixe espaço entre charts

### Interatividade

- Use **filters** para: Estado, Faixa Etária, Renda
- Adicione **drill-downs** onde faz sentido
- Configure **cross-filtering** entre charts relacionados

---

## 📝 Checklist de Dashboard

Para cada dashboard, certifique-se:

- [ ] Título claro e descritivo
- [ ] KPIs principais no topo
- [ ] Cores consistentes e significativas
- [ ] Labels e tooltips informativos
- [ ] Filtros relevantes disponíveis
- [ ] Fontes e referências ao BRFSS
- [ ] Mobile-friendly (se aplicável)
- [ ] Tempo de loading aceitável (<5s)

---

## 🚀 Workflow de Criação

1. **Crie o Dataset** no Superset apontando para a tabela
2. **Explore no SQL Lab** para validar queries
3. **Crie Charts individuais** salvando cada um
4. **Monte o Dashboard** arrastando charts
5. **Configure Filters** globais
6. **Teste Cross-filtering**
7. **Ajuste Layout** para responsividade
8. **Publique** e compartilhe!

---

## 💡 Insights Esperados

Seus dashboards devem revelar:

✓ **Desigualdades**: Renda e educação afetam drasticamente a saúde
✓ **Acesso**: Barreiras econômicas impactam cuidados preventivos
✓ **Comportamentos**: Exercício e peso são fortemente correlacionados com saúde
✓ **Mental Health**: Saúde mental muitas vezes negligenciada mas crítica
✓ **Comorbidades**: Condições crônicas frequentemente co-ocorrem

---

**Boa visualização! 📊✨**

*Desenvolvido por Caio Moreira | 2024*
