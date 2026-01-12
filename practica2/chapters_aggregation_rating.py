import sys
import logging
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.sql.functions import col, avg, round, regexp_extract
from awsglue.dynamicframe import DynamicFrame

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Mantenemos los mismos argumentos
    args = getResolvedOptions(sys.argv, ['database', 'table', 'output_path'])
    database = args['database']
    table = args['table']
    output_path = args['output_path']
    
    logger.info(f"Initializing One Piece Ratings Job. DB: {database}, Table: {table}, Output: {output_path}")
    
    sc = SparkContext()
    glueContext = GlueContext(sc)
    
    # 1. Leer desde Glue Catalog
    dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
        database=database,
        table_name=table
    )
    
    # 2. Convertir a Spark DataFrame
    df = dynamic_frame.toDF()
    logger.info(f"Read registers: {df.count()}")
    
    # Tomar primeros 4 caracteres de la fecha (año)
    df = df.withColumn("year", regexp_extract(col("release").cast("string"), r"(\d{4})", 1))
    df = df.filter(col("year").isNotNull())

    
    df = df.withColumn("rating_double", col("rating").cast("double"))

    # Agrupar por año y calcular la media de valoración.
    annual_ratings_df = df.groupBy("year") \
        .agg(
            avg("rating_double").alias("avg_rating")
        ) \
        .withColumn("avg_rating", round(col("avg_rating"), 2)) \
        .orderBy("year")
    
    output_dynamic_frame = DynamicFrame.fromDF(annual_ratings_df, glueContext, "output")
    
    logger.info(f"Processed years: {output_dynamic_frame.count()}")
    
    # 5. Escribir resultado en S3 (Parquet/Snappy)
    glueContext.write_dynamic_frame.from_options(
        frame=output_dynamic_frame,
        connection_type="s3",
        connection_options={
            "path": output_path,
            "partitionKeys": ["year"]
        },
        format="parquet",
        format_options={"compression": "snappy"}
    )
    
    logger.info(f"Completed. Number of registers: {annual_ratings_df.count()}")

if __name__ == "__main__":
    main()