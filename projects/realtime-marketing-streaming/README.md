# Real-Time Marketing Event Streaming (Demo)

Synthetic streaming project that models click, impression, signup, and conversion events.

## Stack
- Apache Kafka
- Apache Spark Structured Streaming
- Python
- Docker
- Parquet

## Architecture
Synthetic event producer -> Kafka topic -> Spark Structured Streaming -> validation/deduplication -> partitioned Parquet output.

The project demonstrates event-time processing, schema handling, watermarking, deduplication, and streaming transformations. All data is synthetic and contains no company information.
