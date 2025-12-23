# Exportar información necesaria, como ID de cuenta y ARN de rol. HACER AWS CONFIGURE ANTES.
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ROLE_ARN=$(aws iam get-role --role-name LabRole --query Role.Arn --output text)

# Declarar variables globales.
$env:AWS_REGION="us-east-1"
$env:ACCOUNT_ID="339713111309"
$env:BUCKET_NAME="datalake-consumo-energetico-339713111309"
$env:ROLE_ARN="arn:aws:iam::339713111309:role/LabRole"

# $env:ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
# $env:ROLE_ARN=$(aws iam get-role --role-name LabRole --query 'Role.Arn' --output text)

# Crear un nuevo bucket.
aws s3 mb s3://$env:BUCKET_NAME

# Crear carpetas dentro del bucket (objetos vacíos con / al final).
aws s3api put-object --bucket $env:BUCKET_NAME --key raw/
aws s3api put-object --bucket $env:BUCKET_NAME --key raw/energy_consumption_five_minutes/
aws s3api put-object --bucket $env:BUCKET_NAME --key processed/
aws s3api put-object --bucket $env:BUCKET_NAME --key config/
aws s3api put-object --bucket $env:BUCKET_NAME --key queries/
aws s3api put-object --bucket $env:BUCKET_NAME --key errors/
aws s3api put-object --bucket $env:BUCKET_NAME --key scripts/

---------

# Se va a borrar el data Stream después de cada sesión, porque es caro.
# Crear el Kinesis Data Stream.
aws kinesis create-stream --stream-name energy-stream --shard-count 1

--------

# Crear recurso de Firehose. 
# Se le da un nombre, una fuente de datos (Kinesis Stream en este caso). Luego se le indica el ARN del Kinesis de donde vienen los datos y el rol con el que se puede leer.
# Se le indica un bucket a donde va a enviar los dato y a qué prefijo de ese bucket
# Por último, cuando pasan 60s o ya se acumula 1MB de mensajes, envía los datos.

aws firehose create-delivery-stream `
    --delivery-stream-name energy-delivery-stream `
    --delivery-stream-type KinesisStreamAsSource `
    --kinesis-stream-source-configuration "KinesisStreamARN=arn:aws:kinesis:$AWS_REGION:$ACCOUNT_ID:stream/energy-stream,RoleARN=$ROLE_ARN" `
    --extended-s3-destination-configuration "BucketARN=arn:aws:s3:::$BUCKET_NAME,RoleARN=$ROLE_ARN,Prefix=raw/energy_consumption_five_minutes/,ErrorOutputPrefix=errors/,BufferingHints={SizeInMBs=1,IntervalInSeconds=60}"

# En Windows hay que hardcodear las variables de entorno.

aws firehose create-delivery-stream `
    --delivery-stream-name energy-delivery-stream `
    --delivery-stream-type KinesisStreamAsSource `
    --kinesis-stream-source-configuration "KinesisStreamARN=arn:aws:kinesis:us-east-1:339713111309:stream/energy-stream,RoleARN=arn:aws:iam::339713111309:role/LabRole" `
    --extended-s3-destination-configuration "BucketARN=arn:aws:s3:::datalake-consumo-energetico-339713111309,RoleARN=arn:aws:iam::339713111309:role/LabRole,Prefix=raw/energy_consumption_five_minutes/,ErrorOutputPrefix=errors/,BufferingHints={SizeInMBs=1,IntervalInSeconds=60}"

# Firehose mandará los datos que lleguen a Kinesis a partir del lanzamiento de Firehose, no los anteriores a él.
# Crear base de datos en AWS Glue.
aws glue create-database --database-input "{\"Name\":\"energy_db\"}"
# Crear crawler.
aws glue create-crawler `
    --name energy-raw-crawler `
    --role $ROLE_ARN `
    --database-name energy_db `
    --targets "{\"S3Targets\": [{\"Path\": \"s3://$BUCKET_NAME/raw/energy_consumption_five_minutes/\"}]}" 

# Para crear la DB en AWS Glue y el Crawler desde la interfaz se hará de la siguiente forma:
# Se crea AWS Glue. Esto permite mantener bases de datos y tablas, y leerlas.
# Primero se crea una Base de datos en AWS Glue - Data Catalog - Databases.
# Luego se añade una tabla (usando un crawler). Indicando de dónde sacan los datos (S3) y el prefijo. Luego, se 
# Se especifica el rol de IAM.
# Y la base de datos a la que se va a mandar la tabla.
# Y la frecuencia con la que se ejecuta el crawler.


#En Athena en Configuración de consultas, se da a Administrar y se añade el prefijo queries/ del S3.
# En Editor, se escoge la tabla que se requiera.

# Se elimina la Kinesis Data Stream, Firehose y la base de datos de AWS Glue.


# ÚLTIMA PARTE DE LA PRÁCTICA

zip firehose.zip firehose.py

# Crear lambda

# Código para actualizar código de la lambda ya creada

