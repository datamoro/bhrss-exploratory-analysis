# Script de Limpeza Completa e Diagnostico
# Execute este antes de tentar novamente

Write-Host "================================================================================"
Write-Host "LIMPEZA COMPLETA - DIAGNOSTICO E REMOCAO"
Write-Host "================================================================================"
Write-Host ""

# Diagnostico 1: Ver containers PostgreSQL
Write-Host "[DIAGNOSTICO 1] Containers PostgreSQL existentes:" -ForegroundColor Cyan
docker ps -a | Select-String "postgres"
Write-Host ""

# Diagnostico 2: Verificar portas em uso
Write-Host "[DIAGNOSTICO 2] Verificando portas:" -ForegroundColor Cyan
$port5432 = netstat -ano | findstr ":5432 "
$port5433 = netstat -ano | findstr ":5433 "
$port5434 = netstat -ano | findstr ":5434 "

if ($port5432) {
    Write-Host "  Porta 5432: EM USO" -ForegroundColor Yellow
    Write-Host "  $port5432"
} else {
    Write-Host "  Porta 5432: LIVRE" -ForegroundColor Green
}

if ($port5433) {
    Write-Host "  Porta 5433: EM USO" -ForegroundColor Yellow
    Write-Host "  $port5433"
} else {
    Write-Host "  Porta 5433: LIVRE" -ForegroundColor Green
}

if ($port5434) {
    Write-Host "  Porta 5434: EM USO" -ForegroundColor Yellow
    Write-Host "  $port5434"
} else {
    Write-Host "  Porta 5434: LIVRE" -ForegroundColor Green
}
Write-Host ""

# Diagnostico 3: Ver logs do PostgreSQL (se existir)
Write-Host "[DIAGNOSTICO 3] Logs do PostgreSQL:" -ForegroundColor Cyan
$logs = docker logs health_postgres_new 2>&1
if ($logs) {
    Write-Host $logs | Select-Object -Last 20
} else {
    Write-Host "  Container nao existe ainda" -ForegroundColor Yellow
}
Write-Host ""

# Limpeza
Write-Host "================================================================================"
Write-Host "INICIANDO LIMPEZA COMPLETA"
Write-Host "================================================================================"
Write-Host ""

Write-Host "[1/6] Parando TODOS os containers health_*..." -ForegroundColor Cyan
docker stop health_postgres_new health_superset_new 2>$null
docker stop health-data-postgres health-data-superset 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

Write-Host "[2/6] Removendo containers..." -ForegroundColor Cyan
docker rm health_postgres_new health_superset_new 2>$null
docker rm health-data-postgres health-data-superset 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

Write-Host "[3/6] Removendo volumes..." -ForegroundColor Cyan
docker volume rm health_postgres_data_new health_superset_data_new 2>$null
docker volume rm superset-health-data-pipeline_postgres_data 2>$null
docker volume rm superset-health-data-pipeline_superset_data 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Removendo redes..." -ForegroundColor Cyan
docker network rm health_pipeline_network 2>$null
docker network rm superset-health-data-pipeline_health-network 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

Write-Host "[5/6] Limpando imagens antigas..." -ForegroundColor Cyan
docker rmi superset-health-data-pipeline-superset 2>$null
docker rmi superset-health-data-pipeline_health_superset 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Limpando cache do Docker..." -ForegroundColor Cyan
docker system prune -f 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

Write-Host "================================================================================"
Write-Host "LIMPEZA CONCLUIDA!"
Write-Host "================================================================================"
Write-Host ""
Write-Host "Status final:" -ForegroundColor Cyan
Write-Host "  Containers health_*:" -ForegroundColor Yellow
docker ps -a | Select-String "health" | Out-String
if (-not (docker ps -a | Select-String "health")) {
    Write-Host "  Nenhum container health_* encontrado (OK!)" -ForegroundColor Green
}
Write-Host ""

Write-Host "================================================================================"
Write-Host "PROXIMOS PASSOS:"
Write-Host "================================================================================"
Write-Host ""
Write-Host "1. Baixe o docker-compose.new.yml ATUALIZADO (porta 5434)"
Write-Host "2. Execute novamente: .\deploy-new.ps1"
Write-Host ""
Write-Host "Se persistir o erro:"
Write-Host "  - Me envie o output COMPLETO deste script"
Write-Host "  - Execute: docker logs health_postgres_new"
Write-Host "================================================================================"