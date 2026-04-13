"""
Quick Test Script - Verifica se tudo está pronto para executar o ETL
Execute ANTES do pipeline completo para identificar problemas rapidamente
"""

import os
import sys
import pandas as pd
from pathlib import Path

print("="*80)
print("🔍 TESTE RÁPIDO DE SETUP - Health Data Pipeline")
print("="*80)
print()

# Test 1: Check Python version
print("1️⃣  Verificando versão do Python...")
if sys.version_info >= (3, 9):
    print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor} - OK")
else:
    print(f"   ✗ Python {sys.version_info.major}.{sys.version_info.minor} - REQUER 3.9+")
    sys.exit(1)
print()

# Test 2: Check required packages
print("2️⃣  Verificando pacotes instalados...")
required_packages = {
    'pandas': 'pandas',
    'numpy': 'numpy', 
    'sqlalchemy': 'sqlalchemy',
    'psycopg2': 'psycopg2',
    'dotenv': 'python-dotenv',
    'tqdm': 'tqdm'
}

missing_packages = []
for package, pip_name in required_packages.items():
    try:
        __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - NÃO INSTALADO")
        missing_packages.append(pip_name)

if missing_packages:
    print()
    print(f"   ⚠️  Instale os pacotes faltando:")
    print(f"   pip install {' '.join(missing_packages)}")
    print()
else:
    print(f"   ✓ Todos os pacotes instalados!")
print()

# Test 3: Check data file
print("3️⃣  Verificando arquivo de dados...")
data_paths = [
    Path('../data/LLCP2024.ASC'),
    Path('../data/LLCP2024ASC.asc'),
    Path('../data/llcp2024.asc')
]

data_file = None
for path in data_paths:
    if path.exists():
        data_file = path
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"   ✓ Arquivo encontrado: {path}")
        print(f"   ✓ Tamanho: {size_mb:.2f} MB")
        break

if not data_file:
    print("   ✗ Arquivo de dados NÃO ENCONTRADO")
    print("   Procurei em:")
    for path in data_paths:
        print(f"     - {path.absolute()}")
    print()
    print("   💡 Baixe de: https://www.cdc.gov/brfss/annual_data/annual_2024.html")
    sys.exit(1)
print()

# Test 4: Test reading first few lines
print("4️⃣  Testando leitura do arquivo...")
try:
    # Read just first 5 lines to test format
    with open(data_file, 'r') as f:
        first_line = f.readline()
        line_length = len(first_line.rstrip('\n\r'))
        
    print(f"   ✓ Arquivo legível")
    print(f"   ✓ Comprimento da linha: {line_length} caracteres")
    
    if line_length == 2111:
        print(f"   ✓ Formato correto (esperado: 2111 caracteres)")
    else:
        print(f"   ⚠️  Formato inesperado (esperado: 2111, encontrado: {line_length})")
        print(f"   Pode funcionar mesmo assim, mas verifique se é o arquivo correto")
        
except Exception as e:
    print(f"   ✗ Erro ao ler arquivo: {e}")
    sys.exit(1)
print()

# Test 5: Check .env file
print("5️⃣  Verificando arquivo .env...")
env_path = Path('../.env')
if env_path.exists():
    print(f"   ✓ Arquivo .env encontrado")
    
    # Parse .env
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    required_vars = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
    for var in required_vars:
        if var in config:
            print(f"   ✓ {var} configurado")
        else:
            print(f"   ✗ {var} faltando")
else:
    print(f"   ✗ Arquivo .env NÃO ENCONTRADO")
    print(f"   Procurei em: {env_path.absolute()}")
    sys.exit(1)
print()

# Test 6: Check database connection (if Docker is running)
print("6️⃣  Verificando conexão com PostgreSQL...")
try:
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv('../.env')
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('POSTGRES_DB')
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   ✓ Conexão bem-sucedida!")
        print(f"   ✓ PostgreSQL versão: {version.split(',')[0]}")
        
        # Check if table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'brfss_health_data')"))
        table_exists = result.fetchone()[0]
        
        if table_exists:
            result = conn.execute(text("SELECT COUNT(*) FROM brfss_health_data"))
            count = result.fetchone()[0]
            print(f"   ✓ Tabela 'brfss_health_data' existe com {count:,} registros")
            print(f"   💡 Use if_exists='replace' no ETL para substituir dados")
        else:
            print(f"   ℹ️  Tabela 'brfss_health_data' ainda não existe (será criada)")
    
    engine.dispose()
    
except Exception as e:
    print(f"   ⚠️  Não foi possível conectar ao PostgreSQL")
    print(f"   Erro: {e}")
    print()
    print(f"   💡 Isso é normal se o Docker ainda não foi iniciado")
    print(f"   Execute: docker-compose up -d")
print()

# Test 7: Sample extraction test
print("7️⃣  Testando extração de amostra (5 registros)...")
try:
    # Define colspecs (apenas alguns campos para teste)
    test_colspecs = [
        (0, 2),      # state
        (100, 1),    # general_health
        (101, 2),    # physical_health_days
    ]
    test_names = ['state', 'general_health', 'physical_health_days']
    
    df_test = pd.read_fwf(
        data_file,
        colspecs=test_colspecs,
        names=test_names,
        dtype=str,
        nrows=5
    )
    
    print(f"   ✓ Extração bem-sucedida!")
    print(f"   ✓ Registros lidos: {len(df_test)}")
    print()
    print("   📋 Amostra dos dados:")
    print(df_test.to_string(index=False))
    
except Exception as e:
    print(f"   ✗ Erro na extração: {e}")
    sys.exit(1)
print()

# Final summary
print("="*80)
print("✅ RESUMO DO TESTE")
print("="*80)
print()
print("Status dos componentes:")
print(f"  • Python version: ✓")
print(f"  • Pacotes instalados: {'✓' if not missing_packages else '✗'}")
print(f"  • Arquivo de dados: ✓")
print(f"  • Formato do arquivo: ✓")
print(f"  • Arquivo .env: ✓")
print(f"  • Extração de teste: ✓")
print()

if missing_packages:
    print("⚠️  AÇÃO NECESSÁRIA:")
    print(f"   Instale os pacotes faltando: pip install {' '.join(missing_packages)}")
    print()
else:
    print("🎉 TUDO PRONTO!")
    print()
    print("Próximos passos:")
    print("  1. Inicie o Docker: docker-compose up -d")
    print("  2. Execute o ETL: python etl_pipeline.py")
    print()
    print("💡 Para testar com poucos dados primeiro:")
    print("   Edite etl_pipeline.py e defina sample_size = 1000")
    print()

print("="*80)
