# Real-Time Gaming Event Streaming

A portfolio project showing a production-style streaming design with **synthetic events**.

## Architecture
Python Event Producer -> Kafka -> Spark Structured Streaming -> Parquet/Delta-style analytical layer

## Engineering concepts
- Event-driven architecture
- JSON event contracts
- Kafka topics and consumer groups
- Spark Structured Streaming
- Event-time windows
- Streaming aggregations
- Checkpointing design

## Example business metrics
- Coin-In by property in 5-minute windows
- Active players
- Theo Win
- Free Play usage
- Event throughput

This repository intentionally contains no proprietary schemas, credentials, or customer/player records.
