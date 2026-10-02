from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, sum as Fsum, approx_count_distinct, window
from pyspark.sql.types import StructType,StructField,StringType,LongType,IntegerType,DoubleType,TimestampType

spark=SparkSession.builder.appName("gaming-stream").getOrCreate()
schema=(StructType()
 .add("event_id",StringType()).add("event_time",TimestampType())
 .add("player_id",LongType()).add("property_id",IntegerType())
 .add("coin_in",DoubleType()).add("theo_win",DoubleType()).add("free_play",DoubleType()))

raw=(spark.readStream.format("kafka")
 .option("kafka.bootstrap.servers","localhost:9092")
 .option("subscribe","gaming-events").option("startingOffsets","latest").load())

events=(raw.select(from_json(col("value").cast("string"),schema).alias("e")).select("e.*")
 .withWatermark("event_time","10 minutes"))

metrics=(events.groupBy(window(col("event_time"),"5 minutes"),col("property_id"))
 .agg(Fsum("coin_in").alias("coin_in"),
      Fsum("theo_win").alias("theo_win"),
      Fsum("free_play").alias("free_play"),
      approx_count_distinct("player_id").alias("active_players")))

(metrics.writeStream.outputMode("append").format("parquet")
 .option("path","./output/property_metrics")
 .option("checkpointLocation","./checkpoints/property_metrics")
 .start().awaitTermination())
