// Exportar información necesaria, como ID de cuenta y ARN de rol. HACER AWS CONFIGURE ANTES.
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ROLE_ARN=$(aws iam get-role --role-name LabRole --query Role.Arn --output text)

// Declarar variables globales.
$env:AWS_REGION="us-east-1"
$env:ACCOUNT_ID="339713111309"
$env:BUCKET_NAME="datalake-prueba-339713111309"
$env:ROLE_ARN="arn:aws:iam::339713111309:role/LabRole"

// Crear un nuevo bucket.
aws s3 mb s3://$env:BUCKET_NAME

// Crear carpetas dentro del bucket.
aws s3api put-object --bucket $env:BUCKET_NAME --key raw/
aws s3api put-object --bucket $env:BUCKET_NAME --key processed/
aws s3api put-object --bucket $env:BUCKET_NAME --key config/
aws s3api put-object --bucket $env:BUCKET_NAME --key scripts/

---------

// Se va a borrar el data Stream después de cada sesión, porque es caro.

aws kinesis create-stream --stream-name energy-stream --shard-count 1