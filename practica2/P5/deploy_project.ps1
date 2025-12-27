############################################
####        VARIABLES GLOBALES          ####
############################################
$AWS_REGION="us-east-1"
$ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
$BUCKET_NAME="datalake-consumo-energetico-$ACCOUNT_ID"
$ROLE_ARN=$(aws iam get-role --role-name LabRole --query 'Role.Arn' --output text)

$DATABASE="energy_db"
$TABLE="energy_consumption_five_minutes"
$DAILY_OUTPUT="s3://$BUCKET_NAME/processed/energy_consumption_daily/"
$DAILY_SCRIPT="s3://$BUCKET_NAME/scripts/energy_aggregation_daily.py"
$MONTHLY_SCRIPT="s3://$BUCKET_NAME/scripts/energy_aggregation_monthly.py"
$MONTHLY_OUTPUT="s3://$BUCKET_NAME/processed/energy_consumption_monthly/"

###############################################
###                BUCKET S3                ###
###############################################
Write-host "Creando bucket S3..."
# Creación de un nuevo bucket de s3.
aws s3 mb s3://$BUCKET_NAME

# Creación de carpetas dentro del bucket creado.
aws s3api put-object --bucket $BUCKET_NAME --key raw/
aws s3api put-object --bucket $BUCKET_NAME --key raw/energy_consumption_five_minutes/
aws s3api put-object --bucket $BUCKET_NAME --key processed/
aws s3api put-object --bucket $BUCKET_NAME --key config/
aws s3api put-object --bucket $BUCKET_NAME --key queries/
aws s3api put-object --bucket $BUCKET_NAME --key errors/
aws s3api put-object --bucket $BUCKET_NAME --key scripts/

###############################################
###          KINESIS DATA STREAM            ###
###############################################

Write-host "Creando Kinesis Data Stream..."
# Creación del Kinesis Data Stream.
aws kinesis create-stream --stream-name energy-stream --shard-count 1


###############################################
###                 LAMBDA                  ###
###############################################
# Compresión del fichero de la función de firehose.
if (Test-Path "firehose.zip") { Remove-Item "firehose.zip" }
Compress-Archive -Path firehose.py -DestinationPath firehose.zip

Write-host "Creando Lambda..."
# Creación de lambda.
aws lambda create-function `
    --function-name energy-firehose-lambda `
    --runtime python3.12 `
    --role $ROLE_ARN `
    --handler firehose.lambda_handler `
    --zip-file fileb://firehose.zip `
    --timeout 60 `
    --memory-size 128

$LAMBDA_ARN=$(aws lambda get-function --function-name energy-firehose-lambda --query 'Configuration.FunctionArn' --output text)

###############################################
###                FIREHOSE                 ###
###############################################
# Creación del recurso de Firehose.
# Se le da un nombre, una fuente de datos (Kinesis Stream en este caso). Luego se le indica el ARN del Kinesis de donde vienen los datos y el rol con el que se puede leer.
# Se le indica un bucket a donde va a enviar los dato y a qué prefijo de ese bucket
# Por último, cuando pasan 60s o ya se acumula 1MB de mensajes, envía los datos.

$firehoseConfig = @"
{
    "BucketARN": "arn:aws:s3:::$BUCKET_NAME",
    "RoleARN": "$ROLE_ARN",
    "Prefix": "raw/energy_consumption_five_minutes/processing_date=!{partitionKeyFromLambda:processing_date}/",
    "ErrorOutputPrefix": "errors/!{firehose:error-output-type}/",
    "BufferingHints": {
        "SizeInMBs": 64,
        "IntervalInSeconds": 60
    },
    "DynamicPartitioningConfiguration": {
        "Enabled": true,
        "RetryOptions": {
            "DurationInSeconds": 300
        }
    },
    "ProcessingConfiguration": {
        "Enabled": true,
        "Processors": [
            {
                "Type": "Lambda",
                "Parameters": [
                    { "ParameterName": "LambdaArn", "ParameterValue": "$LAMBDA_ARN" },
                    { "ParameterName": "BufferSizeInMBs", "ParameterValue": "1" },
                    { "ParameterName": "BufferIntervalInSeconds", "ParameterValue": "60" }
                ]
            }
        ]
    }
}
"@

$firehoseConfig | Out-File "config_firehose.json" -Encoding ASCII

Write-host "Creando recurso de Firehose..."
aws firehose create-delivery-stream `
    --delivery-stream-name energy-delivery-stream `
    --delivery-stream-type KinesisStreamAsSource `
    --kinesis-stream-source-configuration "KinesisStreamARN=arn:aws:kinesis:${AWS_REGION}:${ACCOUNT_ID}:stream/energy-stream,RoleARN=$ROLE_ARN" `
    --extended-s3-destination-configuration file://config_firehose.json

# Firehose mandará los datos que lleguen a Kinesis a partir del lanzamiento de Firehose, no los anteriores a él.

###############################################
###            AWS GLUE Y CRAWLER           ###
###############################################
# Creación de la base de datos en AWS Glue.
Write-host "Creando base de datos..."
aws glue create-database --database-input "Name=$DATABASE"

$crawlerTargets = @"
    {"S3Targets": [{"Path": "s3://$BUCKET_NAME/raw/energy_consumption_five_minutes/"}]}
"@

Write-host "Creando crawler..."
# Creación del crawler.
aws glue create-crawler `
    --name energy-raw-crawler `
    --role $ROLE_ARN `
    --database-name energy_db `
    --targets ($crawlerTargets.Replace('"', '\"'))

aws glue start-crawler --name energy-raw-crawler

Start-Sleep -Seconds 90
# Para crear la DB en AWS Glue y el Crawler desde la interfaz se hará de la siguiente forma:
# Se crea AWS Glue. Esto permite mantener bases de datos y tablas, y leerlas.
# Primero se crea una Base de datos en AWS Glue - Data Catalog - Databases.
# Luego se añade una tabla (usando un crawler). Indicando de dónde sacan los datos (S3) y el prefijo. Luego, se 
# Se especifica el rol de IAM.
# Y la base de datos a la que se va a mandar la tabla.
# Y la frecuencia con la que se ejecuta el crawler.


#En Athena en Configuración de consultas, se da a Administrar y se añade el prefijo queries/ del S3.
# En Editor, se escoge la tabla que se requiera.





###############################################
###              AWS GLUE ETL               ###
###############################################

Write-host "Copiando scripts de agregación al bucket S3..."
aws s3 cp energy_aggregation_daily.py s3://$BUCKET_NAME/scripts/
aws s3 cp energy_aggregation_monthly.py s3://$BUCKET_NAME/scripts/


$TABLE="energy_consumption_five_minutes"
$DAILY_OUTPUT="s3://$BUCKET_NAME/processed/energy_consumption_daily/"
$DAILY_SCRIPT="s3://$BUCKET_NAME/scripts/energy_aggregation_daily.py"
$MONTHLY_SCRIPT="s3://$BUCKET_NAME/scripts/energy_aggregation_monthly.py"
$MONTHLY_OUTPUT="s3://$BUCKET_NAME/processed/energy_consumption_monthly/"

$monthlyCMD = @"
    {
        "Name": "glueetl",
        "ScriptLocation": "$MONTHLY_SCRIPT",
        "PythonVersion": "3"
    }
"@

$monthlyArgs = @"
    {
        "--database": "$DATABASE",
        "--table": "$TABLE",
        "--output_path": "$MONTHLY_OUTPUT",
        "--enable-continuous-cloudwatch-log": "true",
        "--spark-event-logs-path": "s3://$BUCKET_NAME/logs/"
    }
"@

# Creación de trabajos o tareas.
Write-host "Creando los trabajos de AWS GLUE..."
aws glue create-job `
    --name energy-monthly-aggregation `
    --role $ROLE_ARN `
    --command ($monthlyCMD.Replace('"', '\"')) `
    --default-arguments ($monthlyArgs.Replace('"', '\"')) `
    --glue-version "4.0" `
    --number-of-workers 2 `
    --worker-type "G.1X"

$dailyCMD = @"
    {
        "Name": "glueetl",
        "ScriptLocation": "$DAILY_SCRIPT",
        "PythonVersion": "3"
    }
"@

$dailyArgs = @"
    {
        "--database": "$DATABASE",
        "--table": "$TABLE",
        "--output_path": "$DAILY_OUTPUT",
        "--enable-continuous-cloudwatch-log": "true",
        "--spark-event-logs-path": "s3://$BUCKET_NAME/logs/"
    }
"@

aws glue create-job `
    --name energy-daily-aggregation `
    --role $ROLE_ARN `
    --command ($dailyCMD.Replace('"', '\"')) `
    --default-arguments ($dailyArgs.Replace('"', '\"')) `
    --glue-version "4.0" `
    --number-of-workers 2 `
    --worker-type "G.1X"

Write-host "Ejecutando los trabajos de AWS GLUE..."
aws glue start-job-run --job-name energy-daily-aggregation
aws glue start-job-run --job-name energy-monthly-aggregation

Write-host "Obteniendo nombres de los trabajos..."

aws glue get-job-runs --job-name energy-daily-aggregation --max-items 1
aws glue get-job-runs --job-name energy-monthly-aggregation --max-items 1

# Se elimina la Kinesis Data Stream, Firehose y la base de datos de AWS Glue.
Write-host "Despliegue finalizado correctamente."