"""AWS Glue Spark ETL: Bronze JSON -> validated, deduplicated Silver Parquet."""

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, row_number, to_date, to_timestamp, when
from pyspark.sql.window import Window

args = getResolvedOptions(sys.argv, ["JOB_NAME", "SOURCE_PATH", "TARGET_PATH"])
context = GlueContext(SparkContext.getOrCreate())
job = Job(context)
job.init(args["JOB_NAME"], args)

raw = context.spark_session.read.json(args["SOURCE_PATH"])
typed = raw.withColumn("event_timestamp", to_timestamp("timestamp"))
window = Window.partitionBy("event_id").orderBy(col("event_timestamp").asc_nulls_last())
silver = (
    typed.withColumn("event_rank", row_number().over(window))
    .filter(col("event_rank") == 1)
    .withColumn("event_date", to_date("event_timestamp"))
    .withColumn(
        "data_quality_flag",
        when((col("battery_soc") < 0) | (col("battery_soc") > 100), "INVALID_BATTERY_SOC")
        .when(col("speed_kph") < 0, "INVALID_SPEED")
        .when(col("event_timestamp").isNull(), "INVALID_TIMESTAMP")
        .otherwise("VALID"),
    )
    .withColumn(
        "warning_latency_ms",
        (
            col("warning_displayed_at").cast("timestamp").cast("double")
            - col("warning_generated_at").cast("timestamp").cast("double")
        )
        * 1000,
    )
    .withColumn(
        "connection_stability_score",
        when(col("connection_state") == "CONNECTED", 100)
        .when(col("connection_state") == "DEGRADED", 55)
        .otherwise(0),
    )
)
silver.write.mode("append").partitionBy("event_date").parquet(args["TARGET_PATH"])
job.commit()
