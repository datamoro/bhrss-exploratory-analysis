# Lessons Learned — Health Data Pipeline

## Project Context

**Goal**: Build an end-to-end data pipeline in 4 hours to demonstrate data engineering capabilities — specifically in the context of transitioning from e-commerce into health informatics.

**Dataset**: BRFSS 2024 (457,670 records) — U.S. public health survey data in ASCII fixed-width format.

**Result**: A fully functional pipeline with extraction, transformation, loading, and visualization, demonstrating both technical proficiency and domain immersion in health data.

---

## Key Achievements

### 1. Working with Legacy Health Data Formats

#### The Challenge
The BRFSS data comes in an ASCII fixed-width format — 2,111 character positions per record, no delimiters. This is fundamentally different from the CSV/JSON/API data typical in e-commerce. Each field must be extracted by exact byte position, guided by the CDC's codebook.

#### The Solution
```python
colspecs = [(start, start + length) for _, start, length in self.column_specs]
df = pd.read_fwf(data_file, colspecs=colspecs, names=names)
```

#### Lesson Learned
**"Legacy data formats are not obstacles — they are opportunities to demonstrate versatility."**

Many healthcare organizations still run on systems that produce fixed-width, HL7, or other legacy formats. Being comfortable with these formats is a differentiator when entering health informatics from a modern-stack background.

---

### 2. Clinical Variable Curation

#### The Challenge
The BRFSS offers 262 variables. Processing all of them would be technically possible but analytically meaningless. The real challenge was **selecting the right variables to tell a coherent public health story** — a skill that requires domain understanding, not just engineering.

#### The Approach
I selected 20 variables strategically distributed across 4 analytical dimensions:
- Demographics (context)
- Health Status and Access (outcomes)
- Behavioral Risk Factors (modifiable factors)
- Chronic Conditions (impact)

This mirrors the **Social Determinants of Health (SDOH)** framework used in health informatics to understand how non-clinical factors drive health outcomes.

#### Lesson Learned
**"Big data is not about volume — it is about value. Selecting the right data is more important than processing all of it."**

In health informatics, understanding which variables matter — and why — is often more valuable than the engineering work itself. This is where domain knowledge pays off.

---

### 3. Containerization with Docker

#### Why Docker?
- **Reproducibility**: Anyone can run the project with a single command
- **Isolation**: No version conflicts between PostgreSQL, Superset, and local tools
- **Portability**: Works across operating systems

#### Windows-Specific Challenges
- File paths with `\` vs `/`
- Container-to-host communication requires `host.docker.internal`
- Docker Desktop performance quirks

#### The Solution
```yaml
# docker-compose.yml
networks:
  health_net:
    driver: bridge

volumes:
  health_postgres_data:  # Data persistence
```

#### Lesson Learned
**"Infrastructure as code is not optional — it is essential for reproducible analysis."**

Even in a portfolio project, using Docker shows professional maturity and makes it trivial for a reviewer to validate the work.

---

### 4. ETL Design Patterns

#### Pipeline Architecture

```
Extract --> Transform --> Load (Classic ETL)
    |           |           |
  Pandas     Mapping    PostgreSQL
```

#### Design Decisions

**Batch vs. Streaming**: Batch processing was the right choice because:
- BRFSS data is released annually (static dataset)
- Simplicity beats complexity for clear demonstration
- Focus on fundamentals over infrastructure overhead

**Error Handling**: Robust logging at every stage
```python
logging.basicConfig(
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
```

#### Lesson Learned
**"KISS (Keep It Simple) is especially relevant when time is constrained."**

It is tempting to reach for Spark, Airflow, or Kafka — but using the right tool for the right problem is more important than using the most complex tool. In healthcare, where data pipelines often need to be auditeable and maintainable by small teams, simplicity is a feature.

---

### 5. Health Data Quality and Transformation

#### Challenges Encountered

1. **BRFSS Special Codes**
   - 7 = Don't know
   - 9 = Refused
   - 77 = Don't know (two-digit fields)
   - 88 = None / Not applicable
   - 99 = Refused (two-digit fields)
   - Blank = Missing

   These parallel the conventions found in clinical data systems and EHR extracts. Understanding them is part of building health data literacy.

2. **Missing Data Strategy**
   ```python
   # Only drop rows where ALL key demographic fields are missing
   df = df.dropna(subset=['state', 'general_health'], how='all')
   ```
   Preserving as much data as possible is critical in population health — aggressive filtering can introduce selection bias.

3. **Code-to-Label Mapping**
   - Transforming '1' to 'Male', '2' to 'Female'
   - Creating dictionaries for each BRFSS variable based on the codebook

#### Lesson Learned
**"Dirty data is the norm, not the exception. In healthcare, understanding why data is dirty matters as much as cleaning it."**

The BRFSS coding conventions reflect real-world survey design trade-offs. Understanding these patterns — rather than just treating them as noise — is what separates a health data engineer from a generic one.

---

### 6. Performance Considerations

#### Optimizations Implemented

1. **Chunk-Based Loading**
   ```python
   chunk_size = 10000
   for i in range(0, len(df), chunk_size):
       chunk.to_sql(name=table_name, con=engine, if_exists='append', method='multi')
   ```
   Result: 457,670 records loaded in under 5 minutes.

2. **Strategic Indexing**
   ```sql
   CREATE INDEX idx_state ON brfss_health_data(state);
   CREATE INDEX idx_demographics ON brfss_health_data(state, age_group, sex, race);
   ```
   Indexes were chosen based on the analytical queries planned for the Superset dashboards.

3. **Incremental Development**
   - `sample_size` parameter allows testing with subsets during development
   - Avoids processing the full 457K records during iteration

#### Lesson Learned
**"Premature optimization is wasteful, but ignoring performance entirely is irresponsible."**

The balance: simple code with targeted optimizations that make a real difference, especially when working with datasets at the scale typical in population health.

---

### 7. Data Storytelling for Health

#### The Narrative
**"Social Determinants of Health and Quality of Life in the USA"**

#### Why This Story?

1. **Relevance to Health Informatics**: SDOH is a central framework in modern healthcare analytics and population health management
2. **Policy Impact**: Health equity analysis directly informs public health policy — this is the kind of work health informaticists do
3. **Analytical Depth**: Multiple dimensions allow for rich cross-tabulation and insight discovery
4. **Career Bridge**: Shows I can go beyond moving data from A to B and actually understand the domain I am entering

#### Lesson Learned
**"Data without narrative is just numbers. Transitioning into health informatics means thinking like both an engineer and a public health analyst."**

When entering a new domain, demonstrating that you understand the "why" behind the data — not just the "how" of the pipeline — signals genuine intent and readiness.

---

## Challenges and How I Overcame Them

### Challenge 1: Time Constraints (4 hours)

**Problem**: Scope was too ambitious for the available time.

**Solution**:
- Prioritized a functional MVP over advanced features
- Used 50K records for initial testing, then ran the full dataset
- Documented "future improvements" to show long-term vision

**Takeaway**: Time-boxing and prioritization are essential skills in any domain.

---

### Challenge 2: New Domain (Health Data)

**Problem**: No prior experience with health survey data or BRFSS.

**Solution**:
- Read the BRFSS documentation and codebook
- Selected variables with clear clinical/analytical relevance
- Grouped variables into the SDOH framework used in health informatics

**Takeaway**: Domain knowledge can be acquired rapidly through structured research. The key is knowing what questions to ask.

---

### Challenge 3: Docker on Windows

**Problem**: File paths and networking differ significantly from Linux.

**Solution**:
- Used `host.docker.internal` for container-to-host communication
- Adapted file paths in Python code
- Tested each component in isolation before integrating

**Takeaway**: Cross-platform skills are valuable, especially in healthcare orgs that often run mixed environments.

---

## Skills Demonstrated

### Technical
- [x] Python (pandas, sqlalchemy, psycopg2)
- [x] SQL (DDL, DML, Indexes, Analytical Queries)
- [x] Docker and Docker Compose
- [x] PostgreSQL
- [x] Apache Superset
- [x] ETL Design Patterns
- [x] Data Quality and Validation

### Domain (Health Informatics)
- [x] BRFSS survey methodology
- [x] Social Determinants of Health (SDOH) framework
- [x] Health data coding conventions
- [x] Population health metrics
- [x] Health equity analysis

### Soft Skills
- [x] Time Management
- [x] Prioritization
- [x] Technical Documentation
- [x] Data Storytelling
- [x] Rapid Domain Immersion

---

## What I Would Do Differently with More Time

### Technical

1. **Apache Airflow** — DAGs for orchestration, scheduling, and retry logic
2. **Data Quality Framework** — Great Expectations for automated validation
3. **Testing** — pytest for unit tests, integration tests
4. **BRFSS Survey Weights** — Apply CDC weighting for statistically valid population estimates
5. **ICD-10 Integration** — Map chronic conditions to standard clinical codes

### Domain Depth

1. **Expanded Variable Set** — Include behavioral health, preventive screening, and healthcare utilization variables
2. **Geographic Analysis** — State-level and county-level health disparity maps
3. **Longitudinal Comparison** — Compare BRFSS 2024 against 2020-2023 for trend analysis
4. **Health Equity Indexing** — Build composite indices for health equity scoring

### Infrastructure

1. **Cloud Deployment** — AWS/GCP with Terraform for IaC
2. **CI/CD** — GitHub Actions for automated testing and deployment
3. **Monitoring** — Pipeline metrics, failure alerting, data freshness tracking

---

## Reflections

### What Worked Well

1. **Upfront Planning**: Validating assumptions before coding saved significant time
2. **Simplicity**: KISS principle delivered a working product in 4 hours
3. **Parallel Documentation**: Writing docs while developing maintained quality
4. **Domain-First Thinking**: Starting with the analytical questions (SDOH) before building the pipeline ensured the engineering served the story

### What I Learned About Transitioning Domains

1. **Constraints are liberating**: 4 hours forced focus on what matters
2. **Portfolio is not production**: The goal is demonstrating capability and domain curiosity, not building a scalable system
3. **Storytelling matters**: A well-framed health analysis is worth more than a technically perfect but context-free pipeline
4. **Health data has its own language**: Learning BRFSS coding conventions, SDOH frameworks, and population health concepts was as valuable as the engineering work

---

## Project Metrics

| Metric | Value |
|--------|-------|
| Total Development Time | 4 hours |
| Records Processed | 457,670 |
| Variables Selected | 20 of 262 |
| Lines of Code | ~600 |
| Files Created | 8 |
| Docker Containers | 2 |
| Tables Created | 1 |
| Indexes Created | 4 |

---

Developed by Caio Moreira | 2024

*"Transitioning from e-commerce to health informatics — one pipeline at a time."*
