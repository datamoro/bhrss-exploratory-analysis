# Quick Start Guide — Health Data Pipeline

## Setup (10 minutes)

### 1. Verify Prerequisites

```bash
docker --version
# Expected: Docker version 20.x.x or higher

docker-compose --version
# Expected: docker-compose version 1.29.x or higher

python --version
# Expected: Python 3.9.x or higher
```

### 2. Project Structure

Ensure your directory looks like this:

```
bhrss-exploratory-analysis/
+-- data/
|   +-- LLCP2024ASC.ASC          <-- Your data file here
+-- etl/
|   +-- etl_pipeline_simple.py
+-- sql/
|   +-- init_db.sql
|   +-- analytical_queries.sql
+-- docker-compose.simple.yml
+-- requirements.txt
+-- README.md
+-- .gitignore
```

### 3. Start Infrastructure

```bash
# Start containers
docker-compose -f docker-compose.simple.yml up -d

# Wait ~2 minutes and verify status
docker-compose -f docker-compose.simple.yml ps
```

Expected result:
```
NAME                      STATUS    PORTS
health_postgres_simple    Up        0.0.0.0:5434->5432/tcp
health_superset_simple    Up        0.0.0.0:8089->8088/tcp
```

### 4. Install Python Dependencies

```bash
python -m venv venv
.\venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 5. Run the ETL Pipeline

```bash
cd etl
python etl_pipeline_simple.py
```

Estimated time: 3-5 minutes for the full 457K records.

Expected output:
```
INICIANDO PIPELINE ETL SIMPLIFICADO BRFSS 2024
FASE 1: EXTRACAO DE DADOS
[OK] Extracao concluida com sucesso!
FASE 2: TRANSFORMACAO DE DADOS
Transformacao completa. Contagem final: ~457,000
FASE 3: CARGA DE DADOS
[OK] Carga de dados concluida com sucesso!
[OK] PIPELINE ETL CONCLUIDO COM SUCESSO!
```

### 6. Validate Loaded Data

```bash
docker exec -it health_postgres_simple psql -U dataengineer -d health_data

# Inside psql:
SELECT COUNT(*) FROM brfss_health_data_simple;
-- Expected: ~457,670

SELECT * FROM brfss_health_data_simple LIMIT 5;

\q
```

### 7. Access Apache Superset

1. Open browser: http://localhost:8089
2. Login:
   - **Username**: admin
   - **Password**: admin

### 8. Configure Database in Superset

1. In Superset: **Settings > Database Connections > + Database**
2. Select: **PostgreSQL**
3. Connection string:
   ```
   postgresql://dataengineer:SecurePass123!@health_postgres:5432/health_data
   ```
4. Click **Test Connection**
5. If successful, click **Connect**

### 9. Create Your First Query

1. **SQL Lab > SQL Editor**
2. Select database: `BRFSS Health Data`
3. Run a test query:
   ```sql
   SELECT
       general_health,
       COUNT(*) as count
   FROM brfss_health_data_simple
   GROUP BY general_health
   ORDER BY count DESC;
   ```

---

## Troubleshooting

### Container won't start

```bash
docker-compose -f docker-compose.simple.yml logs health_postgres
docker-compose -f docker-compose.simple.yml logs health_superset
docker-compose -f docker-compose.simple.yml restart
```

### Port already in use

```bash
netstat -ano | findstr :5434
# Stop the conflicting process or change the port in docker-compose.simple.yml
```

### ETL fails with "connection refused"

```bash
docker-compose -f docker-compose.simple.yml ps
# If postgres is not running:
docker-compose -f docker-compose.simple.yml up -d health_postgres
# Wait 30 seconds and retry
```

### Superset won't load

- Wait 2-3 minutes after `docker-compose up` (first-time init is slow)
- Check logs: `docker-compose -f docker-compose.simple.yml logs health_superset`

---

## Success Checklist

- [ ] Docker containers running (postgres + superset)
- [ ] ETL executed successfully
- [ ] ~457,000 records loaded
- [ ] Superset accessible at localhost:8089
- [ ] Database connection configured
- [ ] First query executed successfully

---

## Next Steps

See the [README.md](../README.md) for:
- Analytical dashboard examples
- Health informatics context
- Full documentation

See [lessons_learned.md](../docs/lessons_learned.md) for:
- Technical insights from development
- Domain knowledge acquired
- Design decisions and trade-offs

---

Developed by Caio Moreira | 2024
