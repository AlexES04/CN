# daily_aggregation.py
import sys
import logging
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.sql.functions import col, count, substring
from awsglue.dynamicframe import DynamicFrame

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    args = getResolvedOptions(sys.argv, ['database', 'table', 'output_path'])
    database = args['database']
    table = args['table']
    output_path = args['output_path']
    
    logger.info(f"Initializing One Piece AWS Glue Job. DB: {database}, Table: {table}, Output: {output_path}")
    
    sc = SparkContext()
    glueContext = GlueContext(sc)
    
    # Leer desde Glue Catalog usando GlueContext
    dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
        database=database,
        table_name=table
    )
    
    # Convertir a Spark DataFrame
    df = dynamic_frame.toDF()
    # df.printSchema()
    logger.info(f"Read registers: {df.count()}")
    
    df = df.withColumn("year", substring(col("Release"), -4, 4))
    
    daily_df = df.groupBy("year") \
        .agg(
            count("Chapter").alias("total_chapters"),
        ) \
        .orderBy("year")
    
    output_dynamic_frame = DynamicFrame.fromDF(daily_df, glueContext, "output")
    
    logger.info(f"Processed years: {output_dynamic_frame.count()}")
    
    # Escribir usando GlueContext
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
    
    logger.info(f"Completed. Number of registers: {daily_df.count()}")

if __name__ == "__main__":
    main()