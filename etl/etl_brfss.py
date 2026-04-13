"""
ETL Pipeline for BRFSS 2024 Health Data
Author: Data Engineering Portfolio Project
Description: Extracts health survey data from ASCII fixed-width format,
             transforms selected variables, and loads into PostgreSQL.
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from tqdm import tqdm
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'../docs/etl_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5434')
DB_NAME = os.getenv('POSTGRES_DB', 'health_data')
DB_USER = os.getenv('POSTGRES_USER', 'dataengineer')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

# Field specifications for fixed-width ASCII file
# Format: (field_name, start_position, length)
# Note: positions are 0-indexed in Python (subtract 1 from codebook positions)
FIELD_SPECS = [
    # Demographics
    ('state', 0, 2),                    # _STATE: col 1
    ('age_group', 1981, 1),             # _AGE_G: col 1982
    ('sex', 1975, 1),                   # _SEX: col 1976
    ('race', 1971, 1),                  # _RACE: col 1972
    ('education', 2000, 1),             # _EDUCAG: col 2001
    ('income', 2001, 1),                # _INCOMG1: col 2002
    
    # General Health & Access
    ('general_health', 100, 1),         # GENHLTH: col 101
    ('physical_health_days', 101, 2),   # PHYSHLTH: col 102
    ('mental_health_days', 103, 2),     # MENTHLTH: col 104
    ('has_health_plan', 1899, 1),       # _HLTHPL2: col 1900
    ('cost_barrier', 110, 1),           # MEDCOST1: col 111
    
    # Behavioral Risk Factors
    ('physical_activity', 1901, 1),     # _TOTINDA: col 1902
    ('smoking_status', 2018, 1),        # _SMOKER3: col 2019
    ('binge_drinking', 2052, 1),        # _RFBING6: col 2053
    ('bmi_category', 1997, 1),          # _BMI5CAT: col 1998
    
    # Chronic Conditions
    ('diabetes', 148, 1),               # DIABETE4: col 149
    ('stroke', 139, 1),                 # CVDSTRK3: col 140
    ('heart_attack', 137, 1),           # CVDINFR4: col 138
    ('depression', 145, 1),             # ADDEPEV3: col 146
    ('arthritis', 147, 1),              # HAVARTH4: col 148
]


def create_colspecs():
    """
    Convert field specifications to pandas read_fwf colspecs format.
    Returns list of tuples (start, end) for each field.
    """
    colspecs = []
    for field_name, start, length in FIELD_SPECS:
        # read_fwf uses (start, end) where end is exclusive
        colspecs.append((start, start + length))
    return colspecs


def get_field_names():
    """Extract field names from FIELD_SPECS."""
    return [field[0] for field in FIELD_SPECS]


def extract_data(file_path, sample_size=None):
    """
    Extract data from ASCII fixed-width format file.
    
    Args:
        file_path (str): Path to the .asc file
        sample_size (int, optional): Number of rows to read for testing. None = all rows.
    
    Returns:
        pd.DataFrame: Extracted data
    """
    logger.info(f"Iniciando extração de dados de: {file_path}")
    
    try:
        colspecs = create_colspecs()
        names = get_field_names()
        
        logger.info(f"  Campos a extrair: {len(names)}")
        logger.info(f"  Tamanho da amostra: {'COMPLETO (todos os registros)' if sample_size is None else f'{sample_size:,} registros'}")
        
        # Read the fixed-width format file
        # Using dtype=str to preserve leading zeros and handle missing values
        df = pd.read_fwf(
            file_path,
            colspecs=colspecs,
            names=names,
            dtype=str,
            nrows=sample_size
        )
        
        logger.info(f"✓ Extração concluída com sucesso!")
        logger.info(f"  Registros extraídos: {len(df):,}")
        logger.info(f"  Colunas extraídas: {list(df.columns)}")
        
        # Show sample of first few records
        logger.info("\n📋 Amostra dos primeiros registros:")
        logger.info(f"\n{df.head(3).to_string()}")
        
        return df
    
    except FileNotFoundError:
        logger.error(f"✗ Arquivo não encontrado: {file_path}")
        logger.error("Verifique se o arquivo foi baixado e está no diretório correto")
        raise
    except Exception as e:
        logger.error(f"✗ Erro durante extração: {str(e)}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        raise


def transform_data(df):
    """
    Transform extracted data:
    - Handle missing values (BRFSS uses 7, 9, 77, 88, 99, blank for missing/refused/don't know)
    - Convert numeric fields
    - Data quality checks
    
    Args:
        df (pd.DataFrame): Raw extracted data
    
    Returns:
        pd.DataFrame: Transformed data
    """
    logger.info("Iniciando transformação de dados...")
    
    df_transformed = df.copy()
    
    # BRFSS missing/refused/don't know codes - EXPANDED
    # Single digit: 7=Don't know, 9=Refused
    # Two digit: 77=Don't know, 88=None/Not applicable, 99=Refused
    # Blank=Missing
    missing_codes = ['7', '9', '77', '88', '99', ' ', '', 'BLANK']
    
    # Replace missing codes with NaN for ALL columns first
    for col in df_transformed.columns:
        df_transformed[col] = df_transformed[col].replace(missing_codes, np.nan)
        # Also strip whitespace
        if df_transformed[col].dtype == 'object':
            df_transformed[col] = df_transformed[col].str.strip()
            # Replace empty strings with NaN
            df_transformed[col] = df_transformed[col].replace('', np.nan)
    
    # Convert numeric fields to integers where appropriate
    # Use nullable integer type to handle NaN properly
    numeric_fields = ['physical_health_days', 'mental_health_days']
    
    for field in numeric_fields:
        logger.info(f"Converting {field} to numeric...")
        
        # First, replace any remaining non-numeric values
        df_transformed[field] = df_transformed[field].replace(missing_codes, np.nan)
        
        # Convert to numeric, coercing errors to NaN
        df_transformed[field] = pd.to_numeric(df_transformed[field], errors='coerce')
        
        # Cap at valid range (0-30 days for BRFSS)
        # But first, check if there are values outside expected range
        if df_transformed[field].notna().any():
            min_val = df_transformed[field].min()
            max_val = df_transformed[field].max()
            logger.info(f"  {field} range before clipping: {min_val} to {max_val}")
            
            # Clip to valid range
            df_transformed[field] = df_transformed[field].clip(lower=0, upper=30)
        
        # Convert to nullable integer type (Int64 instead of int64)
        # This allows NaN values without converting to float
        df_transformed[field] = df_transformed[field].astype('Int64')
    
    # Log missing data summary
    logger.info("\nResumo de dados faltantes:")
    missing_summary = df_transformed.isnull().sum()
    for col, count in missing_summary.items():
        if count > 0:  # Only show columns with missing data
            pct = (count / len(df_transformed)) * 100
            logger.info(f"  {col}: {count:,} ({pct:.2f}%)")
    
    # Remove rows where all key demographic fields are missing
    key_fields = ['state', 'age_group', 'sex']
    before_count = len(df_transformed)
    df_transformed = df_transformed.dropna(subset=key_fields, how='all')
    after_count = len(df_transformed)
    
    if before_count > after_count:
        logger.warning(f"Removidas {before_count - after_count:,} linhas com demografia-chave faltando")
    
    logger.info(f"Transformação completa. Contagem final de registros: {len(df_transformed):,}")
    
    return df_transformed


def load_data(df, table_name='brfss_health_data', if_exists='append'):
    """
    Load transformed data into PostgreSQL.
    
    Args:
        df (pd.DataFrame): Transformed data to load
        table_name (str): Target table name
        if_exists (str): How to behave if table exists ('fail', 'replace', 'append')
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Iniciando carga de dados no PostgreSQL...")
    logger.info(f"  Tabela destino: {table_name}")
    logger.info(f"  Registros a carregar: {len(df):,}")
    
    try:
        # Create database connection string
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        # Create SQLAlchemy engine
        engine = create_engine(connection_string)
        
        # Convert nullable integers (Int64) to regular integers for PostgreSQL
        # PostgreSQL will handle NULLs properly
        for col in df.columns:
            if df[col].dtype == 'Int64':
                # Convert Int64 to float first (to preserve NaN), then will be handled by to_sql
                df[col] = df[col].astype('float64')
        
        # Load data in chunks for better memory management
        chunk_size = 10000
        total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
        
        logger.info(f"Carregando em {total_chunks} chunks de {chunk_size:,} registros cada")
        
        with tqdm(total=len(df), desc="Carregando dados") as pbar:
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                chunk.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists=if_exists if i == 0 else 'append',
                    index=False,
                    method='multi'
                )
                pbar.update(len(chunk))
        
        # Verify load
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.fetchone()[0]
            logger.info(f"✓ Verificação: {count:,} registros na tabela do banco de dados")
        
        logger.info("✓ Carga de dados concluída com sucesso!")
        engine.dispose()
        return True
    
    except Exception as e:
        logger.error(f"✗ Erro durante carga de dados: {str(e)}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        return False


def main():
    """Main ETL pipeline execution."""
    start_time = datetime.now()
    logger.info("="*80)
    logger.info("INICIANDO PIPELINE ETL BRFSS 2024")
    logger.info("="*80)
    
    try:
        # Configuration
        data_file = '../data/LLCP2024.ASC'  # Nome padrão do arquivo
        
        # Check if file exists
        if not os.path.exists(data_file):
            # Try alternative names
            alternatives = ['../data/LLCP2024ASC.asc', '../data/llcp2024.asc']
            for alt in alternatives:
                if os.path.exists(alt):
                    data_file = alt
                    logger.info(f"Arquivo encontrado: {data_file}")
                    break
            else:
                logger.error(f"Arquivo de dados não encontrado: {data_file}")
                logger.error("Procurei também: " + ", ".join(alternatives))
                logger.error("Por favor, baixe o arquivo de https://www.cdc.gov/brfss/annual_data/annual_2024.html")
                return False
        
        # For testing, you can set sample_size to a small number (e.g., 1000)
        # For production run, set to None to process all records
        sample_size = None  # Change to 10000 for quick testing
        
        if sample_size:
            logger.warning(f"⚠️  MODO DE TESTE: Processando apenas {sample_size:,} registros")
        
        # EXTRACT
        logger.info("\n" + "="*60)
        logger.info("FASE 1: EXTRAÇÃO DE DADOS")
        logger.info("="*60)
        df_raw = extract_data(data_file, sample_size=sample_size)
        
        # TRANSFORM
        logger.info("\n" + "="*60)
        logger.info("FASE 2: TRANSFORMAÇÃO DE DADOS")
        logger.info("="*60)
        df_clean = transform_data(df_raw)
        
        # Quick data check before loading
        logger.info("\n📊 Verificação rápida antes da carga:")
        logger.info(f"  Tipos de dados:")
        for col in df_clean.columns:
            logger.info(f"    {col}: {df_clean[col].dtype}")
        
        # LOAD
        logger.info("\n" + "="*60)
        logger.info("FASE 3: CARGA DE DADOS")
        logger.info("="*60)
        success = load_data(df_clean, if_exists='replace')
        
        if success:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info("\n" + "="*80)
            logger.info("✓ PIPELINE ETL CONCLUÍDO COM SUCESSO!")
            logger.info(f"✓ Tempo total: {duration:.2f} segundos ({duration/60:.2f} minutos)")
            logger.info(f"✓ Registros processados: {len(df_clean):,}")
            logger.info(f"✓ Taxa de processamento: {len(df_clean)/duration:.0f} registros/segundo")
            logger.info("="*80)
            return True
        else:
            logger.error("\n✗ PIPELINE ETL FALHOU")
            return False
            
    except Exception as e:
        logger.error(f"\n✗ Pipeline falhou: {str(e)}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        return False
    finally:
        logger.info("Conexão com banco de dados encerrada")


if __name__ == "__main__":
    main()