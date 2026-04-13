"""
Export PostgreSQL data to CSV
Gera arquivos CSV para usar em ferramentas de visualização alternativas
"""

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime

print("="*80)
print("EXPORTADOR DE DADOS - PostgreSQL para CSV")
print("="*80)
print()

# Load environment variables
load_dotenv('../.env')

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'health_data')
DB_USER = os.getenv('POSTGRES_USER', 'dataengineer')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

try:
    # Connect to database
    print("Conectando ao PostgreSQL...")
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    # Check which table to export
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'brfss%'
        """))
        tables = [row[0] for row in result]
    
    print(f"Tabelas encontradas: {tables}")
    print()
    
    if not tables:
        print("[ERRO] Nenhuma tabela BRFSS encontrada!")
        print("Execute o ETL primeiro.")
        exit(1)
    
    # Export each table
    output_dir = '../data/exports'
    os.makedirs(output_dir, exist_ok=True)
    
    for table_name in tables:
        print(f"Exportando tabela: {table_name}")
        
        # Read data
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        
        print(f"  Registros: {len(df):,}")
        print(f"  Colunas: {len(df.columns)}")
        
        # Export to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{table_name}_{timestamp}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        print(f"  [OK] Exportado para: {csv_path}")
        
        # Also create a sample (first 1000 rows)
        if len(df) > 1000:
            sample_filename = f"{table_name}_sample_1000_{timestamp}.csv"
            sample_path = os.path.join(output_dir, sample_filename)
            df.head(1000).to_csv(sample_path, index=False, encoding='utf-8')
            print(f"  [OK] Amostra exportada: {sample_path}")
        
        print()
    
    # Export with aggregations for faster loading
    print("Criando datasets agregados para visualizacao...")
    
    # 1. Aggregated by state
    query_state = """
    SELECT 
        state,
        COUNT(*) as total_records,
        AVG(CASE WHEN general_health IN ('1', '2') THEN 1.0 ELSE 0.0 END) * 100 as good_health_pct,
        AVG(physical_health_days::numeric) as avg_physical_health_days,
        AVG(mental_health_days::numeric) as avg_mental_health_days,
        AVG(CASE WHEN diabetes = '1' THEN 1.0 ELSE 0.0 END) * 100 as diabetes_pct,
        AVG(CASE WHEN depression = '1' THEN 1.0 ELSE 0.0 END) * 100 as depression_pct,
        AVG(CASE WHEN exercise = '1' THEN 1.0 ELSE 0.0 END) * 100 as exercise_pct
    FROM brfss_health_data_simple
    WHERE state IS NOT NULL
    GROUP BY state
    ORDER BY state
    """
    
    df_state = pd.read_sql(query_state, engine)
    state_path = os.path.join(output_dir, f'aggregated_by_state_{timestamp}.csv')
    df_state.to_csv(state_path, index=False, encoding='utf-8')
    print(f"  [OK] Agregado por estado: {state_path}")
    
    # 2. Aggregated by income
    query_income = """
    SELECT 
        income,
        COUNT(*) as total_records,
        AVG(CASE WHEN general_health IN ('1', '2') THEN 1.0 ELSE 0.0 END) * 100 as good_health_pct,
        AVG(physical_health_days::numeric) as avg_physical_health_days,
        AVG(mental_health_days::numeric) as avg_mental_health_days
    FROM brfss_health_data_simple
    WHERE income IS NOT NULL
    GROUP BY income
    ORDER BY income
    """
    
    df_income = pd.read_sql(query_income, engine)
    income_path = os.path.join(output_dir, f'aggregated_by_income_{timestamp}.csv')
    df_income.to_csv(income_path, index=False, encoding='utf-8')
    print(f"  [OK] Agregado por renda: {income_path}")
    
    # 3. Chronic conditions summary
    query_chronic = """
    SELECT 
        SUM(CASE WHEN diabetes = '1' THEN 1 ELSE 0 END) as diabetes_count,
        SUM(CASE WHEN stroke = '1' THEN 1 ELSE 0 END) as stroke_count,
        SUM(CASE WHEN heart_attack = '1' THEN 1 ELSE 0 END) as heart_attack_count,
        SUM(CASE WHEN depression = '1' THEN 1 ELSE 0 END) as depression_count,
        SUM(CASE WHEN arthritis = '1' THEN 1 ELSE 0 END) as arthritis_count,
        COUNT(*) as total_records
    FROM brfss_health_data_simple
    """
    
    df_chronic = pd.read_sql(query_chronic, engine)
    chronic_path = os.path.join(output_dir, f'chronic_conditions_summary_{timestamp}.csv')
    df_chronic.to_csv(chronic_path, index=False, encoding='utf-8')
    print(f"  [OK] Resumo de condicoes cronicas: {chronic_path}")
    
    print()
    print("="*80)
    print("[OK] EXPORTACAO CONCLUIDA!")
    print("="*80)
    print()
    print(f"Arquivos salvos em: {os.path.abspath(output_dir)}")
    print()
    print("Voce pode usar esses CSVs em:")
    print("  - Excel / Google Sheets")
    print("  - Power BI")
    print("  - Tableau")
    print("  - Python (pandas)")
    print("  - R")
    print("  - Qualquer ferramenta de BI")
    print()
    
    engine.dispose()

except Exception as e:
    print(f"\n[ERRO] Falha na exportacao: {str(e)}")
    import traceback
    traceback.print_exc()


