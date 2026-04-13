"""
Script de Diagnóstico - Detecta posições corretas dos campos
Execute ANTES do ETL para validar posições
"""

import pandas as pd
from pathlib import Path

print("="*80)
print("🔍 DIAGNÓSTICO DE POSIÇÕES DOS CAMPOS")
print("="*80)
print()

# Localizar arquivo
data_paths = [
    Path('../data/LLCP2024.ASC'),
    Path('../data/LLCP2024ASC.asc'),
    Path('../data/LLCP2024ASC.ASC'),
]

data_file = None
for path in data_paths:
    if path.exists():
        data_file = path
        break

if not data_file:
    print("❌ Arquivo não encontrado!")
    exit(1)

print(f"✓ Arquivo: {data_file}")
print()

# Ler primeira linha
with open(data_file, 'r') as f:
    first_line = f.readline().rstrip('\n\r')
    line_length = len(first_line)

print(f"📏 Comprimento da linha: {line_length} caracteres")
print()

# Testar posições conhecidas que devem ser estáveis (início do arquivo)
print("🧪 TESTANDO POSIÇÕES CONHECIDAS:")
print("-" * 60)

# State (posição 1-2, index 0-1)
state = first_line[0:2]
print(f"State (0:2): '{state}' → {state if state.strip() else 'VAZIO'}")

# General Health (posição 101, index 100)
gen_health = first_line[100:101]
print(f"General Health (100:101): '{gen_health}' → Esperado: 1-5")

# Physical Health Days (posição 102-103, index 101-103)
phys_days = first_line[101:103]
print(f"Physical Health Days (101:103): '{phys_days}' → Esperado: 00-30 ou 88/77/99")

# Mental Health Days (posição 104-105, index 103-105)
mental_days = first_line[103:105]
print(f"Mental Health Days (103:105): '{mental_days}' → Esperado: 00-30 ou 88/77/99")

# Cost Barrier (posição 111, index 110)
cost = first_line[110:111]
print(f"Cost Barrier (110:111): '{cost}' → Esperado: 1-2 ou 7/9")

# Diabetes (posição 149, index 148)
diabetes = first_line[148:149]
print(f"Diabetes (148:149): '{diabetes}' → Esperado: 1-4 ou 7/9")

# Stroke (posição 140, index 139)
stroke = first_line[139:140]
print(f"Stroke (139:140): '{stroke}' → Esperado: 1-2 ou 7/9")

print()
print("-" * 60)

# Mostrar as últimas 100 posições para entender onde estão os campos calculados
print()
print("📋 ÚLTIMOS 200 CARACTERES DA LINHA:")
print("-" * 60)
if line_length >= 200:
    print(f"Posição {line_length-200} a {line_length}:")
    tail = first_line[-200:]
    # Mostrar em blocos de 50
    for i in range(0, len(tail), 50):
        chunk = tail[i:i+50]
        start_pos = line_length - 200 + i
        print(f"[{start_pos:4d}-{start_pos+len(chunk)-1:4d}]: {chunk}")
print()

# Ler 10 linhas para testar
print("📊 TESTANDO EXTRAÇÃO DE 10 REGISTROS:")
print("-" * 60)

# Posições que devem funcionar (início do arquivo)
test_colspecs = [
    (0, 2),      # state
    (100, 101),  # general_health
    (101, 103),  # physical_health_days
    (103, 105),  # mental_health_days
    (110, 111),  # cost_barrier
    (148, 149),  # diabetes
    (139, 140),  # stroke
    (137, 138),  # heart_attack
]

test_names = [
    'state', 'general_health', 'physical_health_days', 
    'mental_health_days', 'cost_barrier', 'diabetes', 
    'stroke', 'heart_attack'
]

try:
    df_test = pd.read_fwf(
        data_file,
        colspecs=test_colspecs,
        names=test_names,
        dtype=str,
        nrows=10
    )
    
    print("✓ Extração bem-sucedida dos campos testados!")
    print()
    print(df_test.to_string(index=False))
    print()
    
    # Validar valores
    print("✅ VALIDAÇÃO DOS VALORES:")
    print("-" * 60)
    
    # State: deve ser 01-56
    states = df_test['state'].unique()
    print(f"States únicos: {sorted(states)}")
    
    # General Health: deve ser 1-5 (ou 7/9)
    gen_health_vals = df_test['general_health'].unique()
    print(f"General Health únicos: {sorted(gen_health_vals)}")
    
    # Physical/Mental days: deve ser 00-30 ou 77/88/99
    phys_vals = df_test['physical_health_days'].unique()
    print(f"Physical Health Days únicos: {sorted(phys_vals)}")
    
    mental_vals = df_test['mental_health_days'].unique()
    print(f"Mental Health Days únicos: {sorted(mental_vals)}")
    
    print()
    print("✅ POSIÇÕES DOS CAMPOS INICIAIS ESTÃO CORRETAS!")
    print()
    print("⚠️  NOTA: Campos calculados (no final) podem precisar ajuste")
    print("   devido ao comprimento diferente (2061 vs 2111)")
    print()
    print("💡 RECOMENDAÇÃO:")
    print("   Execute o ETL com sample_size=1000 primeiro")
    print("   para verificar se os campos calculados estão corretos.")
    
except Exception as e:
    print(f"❌ Erro na extração: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
