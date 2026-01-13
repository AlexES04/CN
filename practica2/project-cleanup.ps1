############################################
####        VARIABLES GLOBALES          ####
############################################
$ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
$BUCKET_NAME="datalake-one-piece-chapters-$ACCOUNT_ID"
$DATABASE="chapters_db"

Write-HOST "INICIANDO LIMPIEZA DE RECURSOS"

###############################################
###              AWS GLUE                   ###
###############################################
Write-Host "Eliminando Glue Jobs..."
aws glue delete-job --job-name chapters-aggregation 2> $null
aws glue delete-job --job-name rating-aggregation 2> $null

Write-Host "Eliminando Glue Crawler..."
aws glue delete-crawler --name chapters-raw-crawler 2> $null
aws glue delete-crawler --name chapters-processed-crawler 2> $null


Write-Host "Eliminando Glue Database..."
aws glue delete-database --name $DATABASE 2> $null

###############################################
###               FIREHOSE                  ###
###############################################
Write-Host "Eliminando Kinesis Firehose..."
aws firehose delete-delivery-stream --delivery-stream-name chapters-delivery-stream 2> $null


###############################################
###                 LAMBDA                  ###
###############################################
Write-Host "Eliminando Lambda Function..."
aws lambda delete-function --function-name chapters-firehose-lambda 2> $null

# Limpieza de archivos locales generados
if (Test-Path "firehose.zip") { 
    Write-Host "Eliminando archivo local firehose.zip..."
    Remove-Item "firehose.zip"
}

if (Test-Path "config_firehose.json") { 
    Write-Host "Eliminando archivo de configuracion de Firehose..."
    Remove-Item "config_firehose.json"
}

###############################################
###          KINESIS DATA STREAM            ###
###############################################
Write-Host "Eliminando Kinesis Data Stream..."
aws kinesis delete-stream --stream-name chapters-stream 2> $null

###############################################
###               BUCKET S3                 ###
###############################################
Write-Host "Vaciando y eliminando Bucket S3 ($BUCKET_NAME)..."
aws s3 rb s3://$BUCKET_NAME --force 2> $null

Write-Host "Esperando a eliminacion completa..."
Start-Sleep -Seconds 20

Write-Host "LIMPIEZA DE RECURSOS COMPLETADA"
