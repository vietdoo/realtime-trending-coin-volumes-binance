from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.functions import current_timestamp
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *
from pyspark.sql.functions import sum

import logging
logging.getLogger("py4j").setLevel(logging.ERROR)

import os
import time
import datetime 
from datetime import timedelta

import requests
from config import *

spark_version = '3.2.3' 
os.environ['PYSPARK_SUBMIT_ARGS'] = f'--packages org.apache.spark:spark-sql-kafka-0-10_2.12:{spark_version} streaming.py'

spark = SparkSession.builder.appName("KafkaStream")\
        .getOrCreate()

spark.sparkContext.setLogLevel('ERROR')

schema = StructType([
    StructField("name", StringType(), True),
    StructField("timestart", IntegerType(), True),
    # StructField("price", DoubleType(), True),
    StructField("volume", DoubleType(), True)
    # StructField("num", IntegerType(), True)
])

time.sleep(10)

kafka_server = "localhost:9094"
kafka_server = 'kafka:9092'
input_topic = "coin"

print(kafka_server)

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_server) \
  .option("subscribe", input_topic) \
  .option("startingOffsets", "latest") \
  .load() \
  .selectExpr("CAST(value AS STRING)") \
  .select(from_json("value", schema).alias("data")) \
  .select("data.*")

def send_data(tags: dict) -> None:
    # HOST = 'http://20.219.197.245'
    # url = f'{HOST}:{FLASK_PORT}/updateData'
    # #url = f'{URL}:{FLASK_PORT}/updateData'
    # print(url)
    # try:
    #   response = requests.post(url, json = tags)
      
    # except Exception as e:
    #   print(e)


    # HOST = 'http://localhost'
    # url = f'{HOST}:{FLASK_PORT}/updateData'
    # print(url)
    # try:
    #   response = requests.post(url, json = tags)
      
    # except Exception as e:
    #   print(e)


    HOST = 'http://flask'
    url = f'{HOST}:{FLASK_PORT}/updateData'
    print(url)
    try:
      response = requests.post(url, json = tags)
      
    except Exception as e:
      print(e)

def process_row(row):
    tags = row.asDict()
    print(tags)
    send_data(tags)


print('=> ', df.schema)
df = df.filter(df.timestart  >= (int(datetime.datetime.now().timestamp()) - 30))

result = df \
  .groupBy("name") \
  .agg(sum("volume").alias("total_volume"))

query = result \
  .writeStream \
  .foreach(process_row) \
  .outputMode("Complete") \
  .start()
  

def process_batch(df_batch, batch_id):
    df_batch.show(truncate=False)
    
query.awaitTermination()
spark.stop()
