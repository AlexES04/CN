Write-Host "INICIANDO EJECUCION"

Write-Host "Esperando a que Firehose termine durante 1 minuto..."
Start-Sleep -Seconds 60
Write-Host "Ejecutando crawler durante 2 minutos..."

aws glue start-crawler --name chapters-raw-crawler

Start-Sleep -Seconds 120

Write-Host "Ejecutando AWS Glue Jobs..."
aws glue start-job-run --job-name chapters-aggregation

Write-Host "EJECUCION COMPLETADA"
