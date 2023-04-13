from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.functions import current_timestamp
import os
import logging
logging.getLogger("py4j").setLevel(logging.ERROR)
from datetime import timedelta
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *
from pyspark.sql.functions import sum
import requests
from config import *

with open("output.txt", "w") as f:
    f.write("")

spark_version = '3.2.3'
#os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.apache.kafka:kafka-clients:3.2.3 --conf spark.driver.extraJavaOptions=-Dlog4jspark.root.logger=ERROR tw-spark.py' 
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:{} spark-coin.py'.format(spark_version)

spark = SparkSession.builder.appName("KafkaStream")\
        .getOrCreate()

spark.sparkContext.setLogLevel('ERROR')

schema = StructType([
    StructField("name", StringType(), True),
    # StructField("timestart", IntegerType(), True),
    # StructField("price", DoubleType(), True),
    StructField("volume", DoubleType(), True)
    # StructField("num", IntegerType(), True)
])

schema = StructType([
  StructField("name", StringType(), True),
  StructField("volume", DoubleType(), True)
])


kafka_server = "localhost:9092"
input_topic = "coin"

def send_data(tags: dict) -> None:
    url = f'{URL}:{FLASK_PORT}/updateData'
    response = requests.post(url, json = tags)

def process_row(row):
    tags = row.asDict()
    print(tags)
    send_data(tags)

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "localhost:9092") \
  .option("subscribe", input_topic) \
  .option("startingOffsets", "latest") \
  .load() \
  .selectExpr("CAST(value AS STRING)") \
  .select(from_json("value", schema).alias("data")) \
  .select("data.*")

df.printSchema()

result = df \
  .groupBy("name") \
  .agg(sum("volume").alias("total_volume"))



query = result \
  .writeStream \
  .foreach(process_row) \
  .outputMode("Update") \
  .start()

query.awaitTermination()


spark.stop()
