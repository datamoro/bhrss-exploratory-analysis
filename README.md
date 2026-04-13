# 🏥 Health Data Pipeline — BRFSS 2024

An **end-to-end data engineering pipeline** that extracts, transforms, and loads U.S. public health survey data (BRFSS 2024) into PostgreSQL, with interactive dashboards powered by Apache Superset — all running in Docker.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Superset](https://img.shields.io/badge/Apache%20Superset-BI-EF6C00?logo=apache&logoColor=white)

---

## 📖 About

This project demonstrates a complete **data engineering workflow** using real-world public health data from the **Behavioral Risk Factor Surveillance System (BRFSS) 2024** — the largest continuously conducted health survey in the world, managed by the U.S. CDC.

### 🎯 Objectives

- **Extract** 457,670 records from an ASCII fixed-width format file
- **Transform** raw survey codes into analysis-ready structured data
- **Load** cleaned data into PostgreSQL with proper indexing
- **Visualize** health insights through Apache Superset dashboards
- **Document** the entire process as a portfolio piece

### 📊 The Data Story

> **"Social Determinants of Health and Quality of Life in the USA"**

This pipeline analyzes:
- How socioeconomic factors influence health outcomes
- Relationship between lifestyle behaviors and chronic conditions
- Impact of healthcare access on population well-being
- Health disparities across demographic groups

---

## 🏗️ Architecture

```
┌──────────────────┐
│  BRFSS Raw Data  │
│ (ASCII Fixed-W.) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Python ETL     │
│  ┌────────────┐  │
│  │  Extract   │  │
│  │  Transform │  │
│  │  Load      │  │
│  └────────────┘  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   PostgreSQL 15  │
│   (Database)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Apache Superset  │
│  (BI / Viz)      │
└──────────────────┘

   🐳 Fully Dockerized
```

---

## 🛠️ Tech Stack

| Component         | Technology       | Version |
|--------------------|-----------------|---------|
| **Containerization** | Docker Compose | 3.8     |
| **Database**        | PostgreSQL      | 15      |
| **ETL**             | Python (pandas) | 3.9+    |
| **Visualization**   | Apache Superset | Latest  |
| **Libraries**       | pandas, sqlalchemy, psycopg2, tqdm | — |

---

## 📦 Project Structure

```
superset-health-data-pipeline/
│
├── data/                          # Raw BRFSS data (not versioned)
│   ├── LLCP2024ASC.ASC           # ASCII fixed-width file (~900 MB)
│   └── exports/                   # Exported CSV datasets
│
├── etl/                           # ETL scripts
│   ├── etl_brfss.py              # Main ETL pipeline
│   ├── etl_pipeline_simple.py    # Simplified pipeline (raw fields only)
│   ├── export_to_csv.py          # Data export utility
│   ├── diagnose_positions.py     # Field position debugger
│   └── test_setup.py             # Environment test script
│
├── sql/                           # SQL scripts
│   ├── init_db.sql               # Database schema + indexes
│   ├── 01_create_tables.sql      # Table creation DDL
│   └── analytical_queries.sql    # Ready-to-use analytical queries
│
├── docker/                        # Docker configuration
│   ├── Dockerfile.superset       # Custom Superset image
│   ├── superset_config.py        # Superset Python config
│   └── superset_init.sh          # Superset bootstrap script
│
├── docs/                          # Documentation & logs
│   ├── lessons_learned.md        # Development insights (PT-BR)
│   └── etl_log_*.log            # ETL execution logs
│
├── docker-compose.yml             # Primary Docker orchestration
├── docker-compose.simple.yml      # Simplified deployment (no build)
├── Dockerfile                     # Superset + psycopg2 image
├── deploy-simple.ps1              # Windows deployment script
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** installed and running
- **Python 3.9+** (for running ETL locally)
- **8 GB RAM** available (recommended)
- **~2 GB disk** space (excluding raw data)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/datamoro/superset-health-data-pipeline.git
cd superset-health-data-pipeline
```

### Step 2 — Download BRFSS Data

1. Go to: https://www.cdc.gov/brfss/annual_data/annual_2024.html
2. Download `LLCP2024ASC.ZIP`
3. Extract the `.ASC` file into the `data/` directory

### Step 3 — Start Infrastructure

```bash
# Start PostgreSQL and Superset containers
docker-compose up -d

# Check container status
docker-compose ps
```

> ⏳ Wait ~2–3 minutes for services to fully initialize.

### Step 4 — Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Step 5 — Run the ETL Pipeline

```bash
cd etl
python etl_brfss.py
```

> ⏱️ **Estimated time**: 3–5 minutes for the full dataset (~457K records).

### Step 6 — Access Apache Superset

1. Open your browser: **http://localhost:8088**
2. Login: `admin` / `admin`

### Step 7 — Connect to the Database in Superset

In Superset:
1. Go to **Settings → Database Connections → + Database**
2. Select **PostgreSQL**
3. Fill in:
   ```
   Host: host.docker.internal
   Port: 5432
   Database: health_data
   Username: admin
   Password: admin123
   ```
4. Click **Test Connection**, then **Connect**

---

## 📊 Selected Variables (20 of 262)

### Demographics (6 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| State | `_STATE` | U.S. state FIPS code |
| Age Group | `_AGE_G` | Age category (6 groups) |
| Sex | `_SEX` | Biological sex |
| Race/Ethnicity | `_RACE` | Race/ethnicity category |
| Education | `_EDUCAG` | Education level |
| Income | `_INCOMG1` | Household income bracket |

### General Health & Access (5 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| General Health | `GENHLTH` | Self-reported health (Excellent → Poor) |
| Physical Health Days | `PHYSHLTH` | Days of poor physical health (0–30) |
| Mental Health Days | `MENTHLTH` | Days of poor mental health (0–30) |
| Health Plan | `_HLTHPL2` | Has health insurance coverage |
| Cost Barrier | `MEDCOST1` | Could not see doctor due to cost |

### Behavioral Risk Factors (4 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| Physical Activity | `_TOTINDA` | Any exercise in past 30 days |
| Smoking Status | `_SMOKER3` | Current/former/never smoker |
| Binge Drinking | `_RFBING6` | Binge drinking behavior |
| BMI Category | `_BMI5CAT` | Underweight → Obese |

### Chronic Conditions (5 vars)
| Variable | BRFSS Code | Description |
|----------|-----------|-------------|
| Diabetes | `DIABETE4` | Ever told has diabetes |
| Stroke | `CVDSTRK3` | Ever had a stroke |
| Heart Attack | `CVDINFR4` | Ever had a heart attack |
| Depression | `ADDEPEV3` | Ever told has depression |
| Arthritis | `HAVARTH4` | Ever told has arthritis |

---

## 📈 Suggested Dashboards

### Dashboard 1: Health Overview
- General health distribution by state
- Chronic condition prevalence
- Health insurance coverage rates

### Dashboard 2: Socioeconomic Determinants
- Health outcomes vs. education level
- Health outcomes vs. income bracket
- Medical cost barriers by demographics

### Dashboard 3: Behaviors & Health
- Exercise vs. chronic conditions
- Smoking status vs. general health
- BMI category vs. diabetes/heart disease

### Dashboard 4: Mental Health
- Distribution of poor mental health days
- Depression rates by socioeconomic factors
- Physical vs. mental health correlation

---

## 🔧 Troubleshooting

### Containers won't start
```bash
docker-compose logs postgres
docker-compose logs superset
docker-compose restart
```

### ETL connection error
```bash
# Verify PostgreSQL is running
docker-compose ps

# Test connection directly
docker exec -it health-data-postgres psql -U admin -d health_data
```

### Superset not loading
- Wait 2–3 minutes after `docker-compose up`
- Check logs: `docker-compose logs superset`

---

## 🧹 Cleanup

```bash
# Stop containers
docker-compose down

# Remove volumes (WARNING: deletes all data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## 📚 Resources

- **BRFSS Data**: https://www.cdc.gov/brfss/
- **Codebook 2024**: https://www.cdc.gov/brfss/annual_data/2024/pdf/codebook24_llcp-v2-508.pdf
- **Apache Superset Docs**: https://superset.apache.org/docs/intro
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## 🎓 Lessons Learned

See the full write-up in [docs/lessons_learned.md](docs/lessons_learned.md) — covering:
- Working with legacy fixed-width data formats
- Strategic variable curation (20 out of 262 available)
- Docker containerization on Windows
- ETL design patterns and performance optimization
- Data quality handling (BRFSS missing/refused codes)
- Data storytelling for public health insights

---

## ⭐ Future Improvements

- [ ] Add Apache Airflow for scheduling and orchestration
- [ ] Implement data quality checks with Great Expectations
- [ ] Add unit tests with pytest
- [ ] Build a REST API for data access
- [ ] Deploy to cloud (AWS / GCP)
- [ ] Add CI/CD pipeline with GitHub Actions

---

## 👤 Author

**Caio Moreira** — Data Engineer  
🔗 [GitHub](https://github.com/datamoro)

---

## 📝 License

This project is for educational and portfolio purposes. The underlying data belongs to the CDC / BRFSS.
