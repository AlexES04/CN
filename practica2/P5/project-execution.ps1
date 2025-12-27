aws glue start-crawler --name energy-raw-crawler

Start-Sleep -Seconds 90

Write-host "Ejecutando los trabajos de AWS GLUE..."
aws glue start-job-run --job-name energy-daily-aggregation
aws glue start-job-run --job-name energy-monthly-aggregation