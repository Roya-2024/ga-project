"""Spark Structured Streaming consumer for synthetic marketing events."""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder.appName("DemoMarketingStreaming").getOrCreate()

schema = StructType([
    StructField("event_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("campaign_id", StringType()),
    StructField("event_type", StringType()),
    StructField("event_ts", StringType()),
    StructField("value", DoubleType()),
])

raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "demo_marketing_events")
    .load()
)

events = (
    raw.select(from_json(col("value").cast("string"), schema).alias("e"))
    .select("e.*")
    .filter(col("customer_id").isNotNull() & col("campaign_id").isNotNull())
    .dropDuplicates(["event_id"])
)

query = (
    events.writeStream
    .format("parquet")
    .option("path", "output/marketing_events")
    .option("checkpointLocation", "output/checkpoints")
    .outputMode("append")
    .start()
)

query.awaitTermination()
