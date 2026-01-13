Write-Host "INICIANDO EJECUCION"

Write-Host "Esperando a que Firehose termine durante 1 minuto..."
Start-Sleep -Seconds 70

Write-Host "Ejecutando crawler durante 2 minutos..."
aws glue start-crawler --name chapters-raw-crawler
Start-Sleep -Seconds 120

Write-Host "Ejecutando AWS Glue Jobs chapters-aggregation..."
aws glue start-job-run --job-name chapters-aggregation
Start-Sleep -Seconds 120

Write-Host "Ejecutando AWS Glue Jobs rating-aggregation..."
aws glue start-job-run --job-name rating-aggregation
Start-Sleep -Seconds 120

Write-Host "Ejecutando crawler de datos procesados durante 2 minutos..."
aws glue start-crawler --name chapters-processed-crawler

Start-Sleep -Seconds 120

Write-Host "EJECUCION COMPLETADA"
