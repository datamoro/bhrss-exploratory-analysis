# Health Data Pipeline — BRFSS 2024

An **end-to-end data engineering pipeline** that extracts, transforms, and loads U.S. public health survey data (BRFSS 2024) into PostgreSQL, with interactive dashboards powered by Apache Superset — all running in Docker.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Superset](https://img.shields.io/badge/Apache%20Superset-BI-EF6C00?logo=apache&logoColor=white)

---

## About

This project is part of a deliberate **career transition from e-commerce data engineering into health informatics**. Rather than building another generic ETL demo, I chose to immerse myself in a real-world public health dataset — the **Behavioral Risk Factor Surveillance System (BRFSS) 2024** — the largest continuously conducted health survey in the world, managed by the U.S. Centers for Disease Control and Prevention (CDC).

The goal was not only to demonstrate technical proficiency but also to **develop domain fluency** in health data: understanding survey methodology, clinical variable semantics (ICD-adjacent coding), social determinants of health (SDOH), and the analytical questions that matter to public health stakeholders.

### Objectives

- **Extract** 457,670 survey records from an ASCII fixed-width format file
- **Transform** raw BRFSS codes into analysis-ready structured data, handling domain-specific missing value conventions
- **Load** cleaned data into PostgreSQL with indexing strategies informed by analytical use cases
- **Visualize** health disparities through Apache Superset dashboards
- **Build domain knowledge** in health informatics through hands-on work with real CDC data

### The Data Story

**"Social Determinants of Health and Quality of Life in the USA"**

This pipeline analyzes:
- How socioeconomic factors (income, education) drive health outcomes
- Relationship between lifestyle behaviors and chronic disease prevalence
- Impact of healthcare access barriers on population well-being
- Health disparities across demographic groups — a core concern in health equity research

---

## Architecture

```
+------------------+
|  BRFSS Raw Data  |
| (ASCII Fixed-W.) |
+--------+---------+
         |
         v
+------------------+
|   Python ETL     |
|  +------------+  |
|  |  Extract   |  |
|  |  Transform |  |
|  |  Load      |  |
|  +------------+  |
+--------+---------+
         |
         v
+------------------+
|   PostgreSQL 15  |
|   (Database)     |
+--------+---------+
         |
         v
+------------------+
| Apache Superset  |
|  (BI / Viz)      |
+------------------+

   Fully Dockerized
```

---

## Tech Stack

| Component          | Technology       | Version |
|--------------------|-----------------|---------|
| Containerization   | Docker Compose  | 3.8     |
| Database           | PostgreSQL      | 15      |
| ETL                | Python (pandas) | 3.9+    |
| Visualization      | Apache Superset | Latest  |
| Libraries          | pandas, sqlalchemy, psycopg2, tqdm | — |

---

## Project Structure

```
superset-health-data-pipeline/
|
+-- data/                          # Raw BRFSS data (not versioned)
|   +-- LLCP2024ASC.ASC           # ASCII fixed-width file (~900 MB)
|   +-- exports/                   # Exported CSV datasets
|
+-- etl/                           # ETL scripts
|   +-- etl_brfss.py              # Main ETL pipeline
|   +-- etl_pipeline_simple.py    # Simplified pipeline (raw fields only)
|   +-- export_to_csv.py          # Data export utility
|   +-- diagnose_positions.py     # Field position debugger
|   +-- test_setup.py             # Environment test script
|
+-- sql/                           # SQL scripts
|   +-- init_db.sql               # Database schema + indexes
|   +-- 01_create_tables.sql      # Table creation DDL
|   +-- analytical_queries.sql    # Ready-to-use analytical queries
|
+-- docker/                        # Docker configuration
|   +-- Dockerfile.superset       # Custom Superset image
|   +-- superset_config.py        # Superset Python config
|   +-- superset_init.sh          # Superset bootstrap script
|
+-- docs/                          # Documentation and logs
|   +-- lessons_learned.md        # Development insights
|   +-- etl_log_*.log            # ETL execution logs
|
+-- docker-compose.yml             # Primary Docker orchestration
+-- docker-compose.simple.yml      # Simplified deployment (no build)
+-- Dockerfile                     # Superset + psycopg2 image
+-- deploy-simple.ps1              # Windows deployment script
+-- requirements.txt               # Python dependencies
+-- .env                           # Environment variables
+-- .gitignore                     # Git ignore rules
+-- README.md                      # This file
```

---

## Quick Start

### Prerequisites

- **Docker Desktop** installed and running
- **Python 3.9+** (for running ETL locally)
- **8 GB RAM** available (recommended)
- **~2 GB disk** space (excluding raw data)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/datamoro/bhrss-exploratory-analysis.git
cd bhrss-exploratory-analysis
```

### Step 2 — Download BRFSS Data

1. Go to: https://www.cdc.gov/brfss/annual_data/annual_2024.html
2. Download `LLCP2024ASC.ZIP`
3. Extract the `.ASC` file into the `data/` directory

### Step 3 — Start Infrastructure

```bash
docker-compose -f docker-compose.simple.yml up -d
docker-compose -f docker-compose.simple.yml ps
```

Wait 2-3 minutes for services to fully initialize.

### Step 4 — Install Python Dependencies

```bash
python -m venv venv
.\venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### Step 5 — Run the ETL Pipeline

```bash
cd etl
python etl_pipeline_simple.py
```

Estimated time: 3-5 minutes for the full dataset (~457K records).

### Step 6 — Access Apache Superset

1. Open your browser: **http://localhost:8089**
2. Login: `admin` / `admin`

### Step 7 — Connect to the Database in Superset

In Superset:
1. Go to **Settings > Database Connections > + Database**
2. Select **PostgreSQL**
3. Use connection string:
   ```
   postgresql://dataengineer:SecurePass123!@health_postgres:5432/health_data
   ```
4. Click **Test Connection**, then **Connect**

---

## Selected Variables (20 of 262)

A key part of this project was **clinical variable curation** — selecting the right variables from 262 available in the BRFSS codebook to build a coherent analytical narrative around social determinants of health.

### Demographics (6 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| State | `_STATE` | U.S. state FIPS code |
| Age Group | `_AGE_G` | Age category (6 groups) |
| Sex | `_SEX` | Biological sex |
| Race/Ethnicity | `_RACE` | Race/ethnicity category |
| Education | `_EDUCAG` | Education level |
| Income | `_INCOMG1` | Household income bracket |

### General Health and Access (5 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| General Health | `GENHLTH` | Self-reported health (Excellent to Poor) |
| Physical Health Days | `PHYSHLTH` | Days of poor physical health (0-30) |
| Mental Health Days | `MENTHLTH` | Days of poor mental health (0-30) |
| Health Plan | `_HLTHPL2` | Has health insurance coverage |
| Cost Barrier | `MEDCOST1` | Could not see doctor due to cost |

### Behavioral Risk Factors (4 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| Physical Activity | `_TOTINDA` | Any exercise in past 30 days |
| Smoking Status | `_SMOKER3` | Current/former/never smoker |
| Binge Drinking | `_RFBING6` | Binge drinking behavior |
| BMI Category | `_BMI5CAT` | Underweight to Obese |

### Chronic Conditions (5 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| Diabetes | `DIABETE4` | Ever told has diabetes |
| Stroke | `CVDSTRK3` | Ever had a stroke |
| Heart Attack | `CVDINFR4` | Ever had a heart attack |
| Depression | `ADDEPEV3` | Ever told has depression |
| Arthritis | `HAVARTH4` | Ever told has arthritis |

---

## Dashboard Highlights

### Dashboard: Unequal Health — Social Inequality and Health in the U.S.

**Tab 1 — Access and Barriers to Care**
- KPI: % Delaying Care Due to Cost (9.47%)
- KPI: Avg Mentally Unhealthy Days (11)
- KPI: Avg Physically Unhealthy Days (11.5)
- KPI: Long Overdue Checkups (4.68%)
- KPI: Lack of Regular Activity (23.29%)
- Cost Barriers to Health Care by Income Level

**Tab 2 — Chronic Disease Inequality**
- Chronic condition prevalence by socioeconomic group
- Comorbidity patterns across demographics

---

## Health Informatics Context

This project was designed as a **domain immersion exercise**, not just a technical demo. Key health informatics concepts explored:

- **BRFSS Methodology**: Understanding how the CDC designs and weights population-level telephone surveys across all 50 states
- **Social Determinants of Health (SDOH)**: Analyzing how income, education, and access to care drive health outcomes — a framework central to modern public health policy
- **Health Equity Analytics**: Building dashboards that reveal disparities, not just averages
- **Clinical Coding Conventions**: Working with BRFSS special codes (7=Don't know, 9=Refused, 77/88/99) that parallel conventions in clinical data systems
- **Population Health Metrics**: Self-reported health status, chronic disease prevalence, behavioral risk factors — the building blocks of population health management

---

## Troubleshooting

### Containers won't start
```bash
docker-compose -f docker-compose.simple.yml logs health_postgres
docker-compose -f docker-compose.simple.yml logs health_superset
docker-compose -f docker-compose.simple.yml restart
```

### ETL connection error
```bash
docker-compose -f docker-compose.simple.yml ps
docker exec -it health_postgres_simple psql -U dataengineer -d health_data
```

### Superset not loading
- Wait 2-3 minutes after `docker-compose up`
- Check logs: `docker-compose -f docker-compose.simple.yml logs health_superset`

---

## Cleanup

```bash
# Stop containers
docker-compose -f docker-compose.simple.yml down

# Remove volumes (deletes all data)
docker-compose -f docker-compose.simple.yml down -v
```

---

## Resources

- **BRFSS Data**: https://www.cdc.gov/brfss/
- **Codebook 2024**: https://www.cdc.gov/brfss/annual_data/2024/pdf/codebook24_llcp-v2-508.pdf
- **Apache Superset Docs**: https://superset.apache.org/docs/intro
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## Lessons Learned

See the full write-up in [docs/lessons_learned.md](docs/lessons_learned.md) — covering:
- Working with legacy fixed-width health data formats
- Strategic variable curation for SDOH analysis
- Docker containerization on Windows
- ETL design patterns and performance trade-offs
- Health data quality handling (BRFSS missing/refused codes)

---

## Future Improvements

- [ ] Add Apache Airflow for scheduling and orchestration
- [ ] Implement data quality checks with Great Expectations
- [ ] Add unit tests with pytest
- [ ] Incorporate BRFSS survey weights for statistically valid estimates
- [ ] Integrate ICD-10 mapping for chronic condition codes
- [ ] Deploy to cloud (AWS / GCP)
- [ ] Add CI/CD pipeline with GitHub Actions

---

## Author

**Caio Moreira** — Data Engineer transitioning into Health Informatics
GitHub: [datamoro](https://github.com/datamoro)

---

## License

This project is for educational and portfolio purposes. The underlying data belongs to the CDC / BRFSS.
