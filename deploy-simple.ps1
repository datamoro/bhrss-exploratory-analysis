# Deploy Simplificado - SEM BUILD CUSTOMIZADO
# Usa imagem oficial do Superset (mais rapido e confiavel)

Write-Host "================================================================================"
Write-Host "DEPLOY SIMPLIFICADO - SUPERSET + POSTGRESQL"
Write-Host "================================================================================"
Write-Host ""

Write-Host "[INFO] Esta versao usa a imagem oficial do Superset" -ForegroundColor Cyan
Write-Host "[INFO] Mais rapido (sem build) e mais confiavel" -ForegroundColor Cyan
Write-Host ""

# Limpeza rapida
Write-Host "[1/4] Limpando instalacao anterior..." -ForegroundColor Cyan
docker stop health_postgres_simple health_superset_simple 2>$null
docker rm health_postgres_simple health_superset_simple 2>$null
docker volume rm health_postgres_simple health_superset_simple 2>$null
docker network rm health_network_simple 2>$null
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

# Iniciar
Write-Host "[2/4] Iniciando servicos..." -ForegroundColor Cyan
docker-compose -f docker-compose.simple.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERRO ao iniciar!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ver logs:" -ForegroundColor Yellow
    Write-Host "  docker logs health_postgres_simple"
    Write-Host "  docker logs health_superset_simple"
    exit 1
}
Write-Host "      OK - Containers iniciados" -ForegroundColor Green
Write-Host ""

# Aguardar PostgreSQL
Write-Host "[3/4] Aguardando PostgreSQL ficar pronto..." -ForegroundColor Cyan
$maxRetries = 30
$retry = 0
$pgReady = $false

while ($retry -lt $maxRetries -and -not $pgReady) {
    $health = docker inspect health_postgres_simple --format='{{.State.Health.Status}}' 2>$null
    if ($health -eq "healthy") {
        $pgReady = $true
        Write-Host "      OK - PostgreSQL pronto!" -ForegroundColor Green
    } else {
        Write-Host -NoNewline "`r      Aguardando... ($retry/$maxRetries)"
        Start-Sleep -Seconds 2
        $retry++
    }
}

if (-not $pgReady) {
    Write-Host ""
    Write-Host "      AVISO: PostgreSQL demorou para iniciar" -ForegroundColor Yellow
    Write-Host "      Ver logs: docker logs health_postgres_simple" -ForegroundColor Yellow
}
Write-Host ""

# Aguardar Superset
Write-Host "[4/4] Aguardando Superset inicializar (60-90 segundos)..." -ForegroundColor Cyan
Write-Host "      Superset precisa:" -ForegroundColor Gray
Write-Host "        - Instalar driver PostgreSQL" -ForegroundColor Gray
Write-Host "        - Criar banco de dados interno" -ForegroundColor Gray
Write-Host "        - Criar usuario admin" -ForegroundColor Gray
Write-Host "        - Inicializar aplicacao" -ForegroundColor Gray
Write-Host ""

for ($i = 90; $i -gt 0; $i--) {
    Write-Host -NoNewline "`r      Aguarde: $i segundos restantes..."
    Start-Sleep -Seconds 1
}
Write-Host ""
Write-Host "      OK" -ForegroundColor Green
Write-Host ""

# Status final
Write-Host "================================================================================"
Write-Host "VERIFICANDO STATUS"
Write-Host "================================================================================"
Write-Host ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "health"
Write-Host ""

# Testar conectividade
Write-Host "Testando conectividade PostgreSQL..." -ForegroundColor Cyan
$testConn = docker exec -it health_postgres_simple pg_isready -U dataengineer 2>&1
if ($testConn -match "accepting connections") {
    Write-Host "  OK - PostgreSQL aceita conexoes" -ForegroundColor Green
} else {
    Write-Host "  AVISO - PostgreSQL pode nao estar pronto ainda" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "================================================================================"
Write-Host "DEPLOY CONCLUIDO!"
Write-Host "================================================================================"
Write-Host ""
Write-Host "ACESSO:" -ForegroundColor Cyan
Write-Host "  Superset: http://localhost:8089"
Write-Host "  Login: admin / admin"
Write-Host ""
Write-Host "CONEXAO POSTGRESQL:" -ForegroundColor Green
Write-Host "  postgresql://dataengineer:SecurePass123!@health_postgres:5432/health_data"
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "  1. Acesse http://localhost:8089"
Write-Host "  2. Faca login (admin/admin)"
Write-Host "  3. Data > Databases > + Database > PostgreSQL"
Write-Host "  4. Cole a string de conexao acima"
Write-Host "  5. Test Connection!"
Write-Host ""
Write-Host "================================================================================"
Write-Host ""
Write-Host "Ver logs em tempo real:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.simple.yml logs -f"
Write-Host ""