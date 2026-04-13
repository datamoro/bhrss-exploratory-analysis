"""
ETL Pipeline SIMPLIFICADO - BRFSS 2024
Versao WINDOWS - Sem caracteres Unicode
Usa apenas campos RAW (do inicio do arquivo)
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from tqdm import tqdm
import logging
from datetime import datetime

# Configure logging - WINDOWS COMPATIBLE
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'../docs/etl_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../.env')

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5434')
DB_NAME = os.getenv('POSTGRES_DB', 'health_data')
DB_USER = os.getenv('POSTGRES_USER', 'dataengineer')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

# SIMPLIFIED Field specifications - APENAS campos raw do inicio do arquivo
FIELD_SPECS = [
    # Raw Demographics (STABLE - inicio do arquivo)
    ('state', 0, 2),                    # _STATE: col 1-2
    
    # Raw Health Status (STABLE - posicoes 100-200)
    ('general_health', 100, 1),         # GENHLTH: col 101
    ('physical_health_days', 101, 2),   # PHYSHLTH: col 102-103
    ('mental_health_days', 103, 2),     # MENTHLTH: col 104-105
    ('cost_barrier', 110, 1),           # MEDCOST1: col 111
    ('checkup', 111, 1),                # CHECKUP1: col 112
    ('exercise', 112, 1),               # EXERANY2: col 113
    
    # Raw Chronic Conditions (STABLE - posicoes 137-150)
    ('heart_attack', 137, 1),           # CVDINFR4: col 138
    ('coronary_heart', 138, 1),         # CVDCRHD4: col 139
    ('stroke', 139, 1),                 # CVDSTRK3: col 140
    ('asthma', 140, 1),                 # ASTHMA3: col 141
    ('asthma_current', 141, 1),         # ASTHNOW: col 142
    ('copd', 144, 1),                   # CHCCOPD3: col 145
    ('depression', 145, 1),             # ADDEPEV3: col 146
    ('kidney', 146, 1),                 # CHCKDNY2: col 147
    ('arthritis', 147, 1),              # HAVARTH4: col 148
    ('diabetes', 148, 1),               # DIABETE4: col 149
    
    # Raw Demographics continued (STABLE - posicoes 185-210)
    ('marital', 185, 1),                # MARITAL: col 186
    ('education', 186, 1),              # EDUCA: col 187
    ('employment', 200, 1),             # EMPLOY1: col 201
    ('income', 203, 2),                 # INCOME3: col 204-205
    ('sex', 87, 1),                     # SEXVAR: col 88
]


def create_colspecs():
    """Convert field specifications to pandas read_fwf colspecs format."""
    colspecs = []
    for field_name, start, length in FIELD_SPECS:
        colspecs.append((start, start + length))
    return colspecs


def get_field_names():
    """Extract field names from FIELD_SPECS."""
    return [field[0] for field in FIELD_SPECS]


def extract_data(file_path, sample_size=None):
    """Extract data from ASCII fixed-width format file."""
    logger.info(f"Iniciando extracao de dados de: {file_path}")
    
    try:
        colspecs = create_colspecs()
        names = get_field_names()
        
        logger.info(f"  Campos a extrair: {len(names)}")
        sample_text = 'COMPLETO' if sample_size is None else f'{sample_size:,}'
        logger.info(f"  Tamanho da amostra: {sample_text}")
        
        df = pd.read_fwf(
            file_path,
            colspecs=colspecs,
            names=names,
            dtype=str,
            nrows=sample_size
        )
        
        logger.info(f"[OK] Extracao concluida com sucesso!")
        logger.info(f"  Registros extraidos: {len(df):,}")
        logger.info(f"\nAmostra dos primeiros 3 registros:")
        logger.info(f"\n{df.head(3).to_string()}")
        
        return df
    
    except FileNotFoundError:
        logger.error(f"[ERRO] Arquivo nao encontrado: {file_path}")
        raise
    except Exception as e:
        logger.error(f"[ERRO] Erro durante extracao: {str(e)}")
        raise


def transform_data(df):
    """Transform extracted data."""
    logger.info("Iniciando transformacao de dados...")
    
    df_transformed = df.copy()
    
    # BRFSS missing codes
    missing_codes = ['7', '9', '77', '88', '99', ' ', '', 'BLANK']
    
    # Replace missing codes with NaN for ALL columns
    for col in df_transformed.columns:
        df_transformed[col] = df_transformed[col].replace(missing_codes, np.nan)
        if df_transformed[col].dtype == 'object':
            df_transformed[col] = df_transformed[col].str.strip()
            df_transformed[col] = df_transformed[col].replace('', np.nan)
    
    # Convert numeric fields
    numeric_fields = ['physical_health_days', 'mental_health_days']
    
    for field in numeric_fields:
        logger.info(f"Convertendo {field} para numerico...")
        df_transformed[field] = df_transformed[field].replace(missing_codes, np.nan)
        df_transformed[field] = pd.to_numeric(df_transformed[field], errors='coerce')
        
        if df_transformed[field].notna().any():
            min_val = df_transformed[field].min()
            max_val = df_transformed[field].max()
            logger.info(f"  {field} range antes do clip: {min_val} a {max_val}")
            df_transformed[field] = df_transformed[field].clip(lower=0, upper=30)
        
        df_transformed[field] = df_transformed[field].astype('Int64')
    
    # Log missing data
    logger.info("\nResumo de dados faltantes:")
    missing_summary = df_transformed.isnull().sum()
    for col, count in missing_summary.items():
        if count > 0:
            pct = (count / len(df_transformed)) * 100
            logger.info(f"  {col}: {count:,} ({pct:.2f}%)")
    
    # Remove rows with all key fields missing
    key_fields = ['state', 'general_health']
    before_count = len(df_transformed)
    df_transformed = df_transformed.dropna(subset=key_fields, how='all')
    after_count = len(df_transformed)
    
    if before_count > after_count:
        logger.warning(f"Removidas {before_count - after_count:,} linhas com campos-chave faltando")
    
    logger.info(f"Transformacao completa. Contagem final: {len(df_transformed):,}")
    
    return df_transformed


def load_data(df, table_name='brfss_health_data_simple', if_exists='append'):
    """Load transformed data into PostgreSQL."""
    logger.info(f"Iniciando carga de dados no PostgreSQL...")
    logger.info(f"  Tabela destino: {table_name}")
    logger.info(f"  Registros a carregar: {len(df):,}")
    
    try:
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        
        # Convert Int64 to float64 for PostgreSQL
        for col in df.columns:
            if df[col].dtype == 'Int64':
                df[col] = df[col].astype('float64')
        
        chunk_size = 100000
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
            logger.info(f"[OK] Verificacao: {count:,} registros na tabela do banco de dados")
        
        logger.info("[OK] Carga de dados concluida com sucesso!")
        engine.dispose()
        return True
    
    except Exception as e:
        logger.error(f"[ERRO] Erro durante carga de dados: {str(e)}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        return False


def main():
    """Main ETL pipeline execution."""
    start_time = datetime.now()
    logger.info("="*80)
    logger.info("INICIANDO PIPELINE ETL SIMPLIFICADO BRFSS 2024")
    logger.info("="*80)
    
    try:
        # Configuration
        data_file = '../data/LLCP2024.ASC'
        
        # Check if file exists
        if not os.path.exists(data_file):
            alternatives = ['../data/LLCP2024ASC.asc', '../data/LLCP2024ASC.ASC']
            for alt in alternatives:
                if os.path.exists(alt):
                    data_file = alt
                    logger.info(f"Arquivo encontrado: {data_file}")
                    break
            else:
                logger.error(f"Arquivo de dados nao encontrado")
                return False
        
        # Sample size for testing (set to None for full run)
        sample_size = 1000  # START WITH SMALL SAMPLE!
        
        if sample_size:
            logger.warning(f"[AVISO] MODO DE TESTE: Processando apenas {sample_size:,} registros")
        
        # EXTRACT
        logger.info("\n" + "="*60)
        logger.info("FASE 1: EXTRACAO DE DADOS")
        logger.info("="*60)
        df_raw = extract_data(data_file, sample_size=sample_size)
        
        # TRANSFORM
        logger.info("\n" + "="*60)
        logger.info("FASE 2: TRANSFORMACAO DE DADOS")
        logger.info("="*60)
        df_clean = transform_data(df_raw)
        
        # LOAD
        logger.info("\n" + "="*60)
        logger.info("FASE 3: CARGA DE DADOS")
        logger.info("="*60)
        success = load_data(df_clean, if_exists='replace')
        
        if success:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info("\n" + "="*80)
            logger.info("[OK] PIPELINE ETL CONCLUIDO COM SUCESSO!")
            logger.info(f"[OK] Tempo total: {duration:.2f} segundos ({duration/60:.2f} minutos)")
            logger.info(f"[OK] Registros processados: {len(df_clean):,}")
            logger.info("="*80)
            return True
        else:
            logger.error("\n[ERRO] PIPELINE ETL FALHOU")
            return False
            
    except Exception as e:
        logger.error(f"\n[ERRO] Pipeline falhou: {str(e)}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        return False
    finally:
        logger.info("Conexao com banco de dados encerrada")


if __name__ == "__main__":
    main()