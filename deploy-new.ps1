# Script de Deploy - Health Data Pipeline com Superset
# Versao LIMPA - Sem interferencias

Write-Host "================================================================================"
Write-Host "DEPLOY LIMPO - HEALTH DATA PIPELINE COM SUPERSET"
Write-Host "================================================================================"
Write-Host ""

# Step 1: Parar containers antigos
Write-Host "[1/7] Parando containers antigos..."
docker stop health-data-superset health-data-postgres 2>$null
docker stop health_superset_new health_postgres_new 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

# Step 2: Remover containers antigos
Write-Host "[2/7] Removendo containers antigos..."
docker rm health-data-superset health-data-postgres 2>$null
docker rm health_superset_new health_postgres_new 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

# Step 3: Limpar volumes
Write-Host "[3/7] Limpando volumes antigos..."
docker volume rm health_postgres_data_new health_superset_data_new 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

# Step 4: Build
Write-Host "[4/7] Construindo imagem do Superset..."
Write-Host "      (Pode demorar alguns minutos na primeira vez)"
docker-compose -f docker-compose.new.yml build --no-cache
if ($LASTEXITCODE -eq 0) {
    Write-Host "      OK" -ForegroundColor Green
} else {
    Write-Host "      ERRO ao construir!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 5: Iniciar
Write-Host "[5/7] Iniciando servicos..."
docker-compose -f docker-compose.new.yml up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "      OK" -ForegroundColor Green
} else {
    Write-Host "      ERRO ao iniciar!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Aguardar
Write-Host "[6/7] Aguardando inicializacao (90 segundos)..."
for ($i = 90; $i -gt 0; $i--) {
    Write-Host -NoNewline "`r      Aguarde: $i segundos..."
    Start-Sleep -Seconds 1
}
Write-Host ""
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

# Step 7: Verificar
Write-Host "[7/7] Verificando status..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "health"
Write-Host ""

Write-Host "================================================================================"
Write-Host "DEPLOY CONCLUIDO!"
Write-Host "================================================================================"
Write-Host ""
Write-Host "ACESSO:" -ForegroundColor Cyan
Write-Host "  Superset: http://localhost:8089"
Write-Host "  Login: admin / admin"
Write-Host ""
Write-Host "CONEXAO POSTGRESQL:" -ForegroundColor Cyan
Write-Host "  postgresql://dataengineer:SecurePass123!@health_postgres:5432/health_data"
Write-Host ""
Write-Host "================================================================================"