Write-Host "INICIANDO EJECUCION"

Write-Host "Esperando a que Firehose termine..."
Start-Sleep -Seconds 60
Write-Host "Ejecutando crawler durante 90 segundos..."

aws glue start-crawler --name energy-raw-crawler

Start-Sleep -Seconds 90

Write-Host "Ejecutando AWS Glue Jobs..."
aws glue start-job-run --job-name energy-daily-aggregation
aws glue start-job-run --job-name energy-monthly-aggregation

Write-Host "EJECUCION COMPLETADA"
