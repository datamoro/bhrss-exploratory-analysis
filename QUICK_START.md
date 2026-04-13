# 🚀 Quick Start Guide - Health Data Pipeline

## ⚡ Setup Rápido (10 minutos)

### 1️⃣ Verifique os Pré-requisitos

```bash
# Docker instalado?
docker --version
# Deve retornar: Docker version 20.x.x ou superior

# Docker Compose instalado?
docker-compose --version
# Deve retornar: docker-compose version 1.29.x ou superior

# Python instalado?
python --version
# Deve retornar: Python 3.9.x ou superior
```

### 2️⃣ Estrutura de Pastas

Certifique-se que sua estrutura está assim:

```
C:\Users\caiom\Documents\portfolio_pessoal\superset-health-data-pipeline\
├── data\
│   └── LLCP2024ASC.asc          ← Seu arquivo de dados aqui
├── etl\
│   └── etl_brfss.py
├── sql\
│   ├── init_db.sql
│   └── analytical_queries.sql
├── docs\
│   └── lessons_learned.md
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

### 3️⃣ Iniciar Infraestrutura

```bash
# Navegue até a pasta do projeto
cd C:\Users\caiom\Documents\portfolio_pessoal\superset-health-data-pipeline

# Suba os containers
docker-compose up -d

# Aguarde ~2 minutos e verifique status
docker-compose ps
```

✅ **Resultado esperado:**
```
NAME                      STATUS    PORTS
health-data-postgres      Up        0.0.0.0:5432->5432/tcp
health-data-superset      Up        0.0.0.0:8088->8088/tcp
```

### 4️⃣ Instalar Dependências Python

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\activate    # Windows
# ou
source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 5️⃣ Criar Schema do Banco de Dados

```bash
# Entrar no container PostgreSQL
docker exec -it health-data-postgres psql -U admin -d health_data

# Executar dentro do psql:
\i /docker-entrypoint-initdb.d/init_db.sql

# Verificar tabela criada
\dt

# Sair
\q
```

Ou simplesmente:
```bash
docker exec -i health-data-postgres psql -U admin -d health_data < sql/init_db.sql
```

### 6️⃣ Executar Pipeline ETL

```bash
cd etl
python etl_brfss.py
```

⏱️ **Tempo estimado**: 3-5 minutos para 50.000 registros

📊 **Progresso esperado:**
```
2024-11-13 10:00:00 - INFO - ============================================================
2024-11-13 10:00:00 - INFO - INICIANDO PIPELINE ETL BRFSS 2024
2024-11-13 10:00:00 - INFO - ============================================================
2024-11-13 10:00:01 - INFO - ✓ Conexão com PostgreSQL estabelecida com sucesso
2024-11-13 10:00:05 - INFO - ✓ Extraídos 50000 registros com 21 colunas
2024-11-13 10:00:08 - INFO - ✓ Transformação completa. 49234 registros válidos
2024-11-13 10:00:35 - INFO - ✓ 49234 registros carregados com sucesso no PostgreSQL
2024-11-13 10:00:35 - INFO - ============================================================
2024-11-13 10:00:35 - INFO - PIPELINE ETL CONCLUÍDO COM SUCESSO!
2024-11-13 10:00:35 - INFO - Tempo de execução: 35.23 segundos
2024-11-13 10:00:35 - INFO - Registros processados: 49234
2024-11-13 10:00:35 - INFO - ============================================================
```

### 7️⃣ Validar Dados Carregados

```bash
# Conectar ao PostgreSQL
docker exec -it health-data-postgres psql -U admin -d health_data

# Executar query de validação
SELECT COUNT(*) FROM public.brfss_health_data;
# Deve retornar ~49.000-50.000

# Ver amostra de dados
SELECT * FROM public.brfss_health_data LIMIT 10;

# Sair
\q
```

### 8️⃣ Acessar Apache Superset

1. Abra navegador: http://localhost:8088
2. Login:
   - **Username**: admin
   - **Password**: admin

### 9️⃣ Configurar Database no Superset

1. No Superset, vá em: **Settings** → **Database Connections** → **+ Database**
2. Selecione: **PostgreSQL**
3. Preencha:
   ```
   Display Name: BRFSS Health Data
   SQLAlchemy URI: postgresql://admin:admin123@host.docker.internal:5432/health_data
   ```
4. Clique em **Test Connection**
5. Se sucesso, clique em **Connect**

### 🔟 Criar Primeiro Dashboard

1. **SQL Lab** → **SQL Editor**
2. Selecione database: `BRFSS Health Data`
3. Execute query teste:
   ```sql
   SELECT 
       general_health,
       COUNT(*) as count
   FROM public.brfss_health_data
   GROUP BY general_health
   ORDER BY count DESC;
   ```
4. Explore os resultados!

---

## 🔍 Troubleshooting Rápido

### Problema: Container não inicia

```bash
# Ver logs detalhados
docker-compose logs postgres
docker-compose logs superset

# Reiniciar
docker-compose restart
```

### Problema: Porta já em uso

```bash
# Ver o que está usando a porta 5432
netstat -ano | findstr :5432

# Parar processo ou mudar porta no docker-compose.yml
```

### Problema: ETL falha com "connection refused"

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps

# Se não estiver, iniciar
docker-compose up -d postgres

# Aguardar 30 segundos e tentar novamente
```

### Problema: Superset não carrega

- Aguarde 2-3 minutos após `docker-compose up`
- Superset leva tempo para inicializar na primeira vez
- Verifique logs: `docker-compose logs superset`

---

## 📝 Checklist de Sucesso

- [ ] Docker containers rodando (postgres + superset)
- [ ] Tabela criada no PostgreSQL
- [ ] ETL executado com sucesso
- [ ] ~50.000 registros carregados
- [ ] Superset acessível em localhost:8088
- [ ] Database connection configurada
- [ ] Primeira query executada com sucesso

---

## 🎉 Pronto!

Seu pipeline está funcionando! Agora você pode:

1. Explorar queries em `sql/analytical_queries.sql`
2. Criar dashboards no Superset
3. Adicionar mais dados (aumentar `max_records` no ETL)
4. Customizar análises

---

## 📞 Próximos Passos

Consulte o [README.md](../README.md) principal para:
- Análises sugeridas
- Melhorias futuras
- Documentação completa

Consulte [lessons_learned.md](../docs/lessons_learned.md) para:
- Insights do desenvolvimento
- Decisões técnicas
- Aprendizados

---

**Desenvolvido por Caio Moreira | 2024**
