-- Create table for BRFSS Health Data
-- This table stores selected variables from the 2024 BRFSS dataset
-- Focus: Social Determinants of Health and Quality of Life

CREATE TABLE IF NOT EXISTS brfss_health_data (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Demographics (6 fields)
    state VARCHAR(2),                    -- State FIPS code
    age_group VARCHAR(1),                -- Age category
    sex VARCHAR(1),                      -- Sex (1=Male, 2=Female)
    race VARCHAR(1),                     -- Race/Ethnicity
    education VARCHAR(1),                -- Education level
    income VARCHAR(1),                   -- Income category
    
    -- General Health & Access (5 fields)
    general_health VARCHAR(1),           -- Self-reported general health (1=Excellent to 5=Poor)
    physical_health_days SMALLINT,       -- Days of poor physical health (0-30)
    mental_health_days SMALLINT,         -- Days of poor mental health (0-30)
    has_health_plan VARCHAR(1),          -- Has health coverage (1=Yes, 2=No)
    cost_barrier VARCHAR(1),             -- Could not see doctor due to cost (1=Yes, 2=No)
    
    -- Behavioral Risk Factors (4 fields)
    physical_activity VARCHAR(1),        -- Exercise in past 30 days (1=Yes, 2=No)
    smoking_status VARCHAR(1),           -- Smoking status (1=Current, 2=Former, 3=Never, 4=Never/Former, 9=Don't know)
    binge_drinking VARCHAR(1),           -- Binge drinking (1=No, 2=Yes)
    bmi_category VARCHAR(1),             -- BMI category (1=Underweight to 4=Obese)
    
    -- Chronic Conditions (5 fields)
    diabetes VARCHAR(1),                 -- Ever told has diabetes (1=Yes, 2=Yes/pregnancy, 3=No, 4=Prediabetes)
    stroke VARCHAR(1),                   -- Ever had stroke (1=Yes, 2=No)
    heart_attack VARCHAR(1),             -- Ever had heart attack (1=Yes, 2=No)
    depression VARCHAR(1),               -- Ever told has depression (1=Yes, 2=No)
    arthritis VARCHAR(1),                -- Ever told has arthritis (1=Yes, 2=No)
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_state ON brfss_health_data(state);
CREATE INDEX IF NOT EXISTS idx_age_group ON brfss_health_data(age_group);
CREATE INDEX IF NOT EXISTS idx_income ON brfss_health_data(income);
CREATE INDEX IF NOT EXISTS idx_education ON brfss_health_data(education);
CREATE INDEX IF NOT EXISTS idx_general_health ON brfss_health_data(general_health);
CREATE INDEX IF NOT EXISTS idx_created_at ON brfss_health_data(created_at);

-- Create composite index for demographic analysis
CREATE INDEX IF NOT EXISTS idx_demographics ON brfss_health_data(state, age_group, sex, race);

COMMENT ON TABLE brfss_health_data IS 'BRFSS 2024 Health Survey Data - Selected variables for social determinants analysis';
