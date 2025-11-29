# aws-log-processor

# Log Processing Pipeline

## Architecture Overview

This project implements a serverless, multi-tenant log processing pipeline on AWS.

```
[Client] → [API Gateway] → [Lambda (API)] → [SQS Queue] → [Lambda (Worker)] → [DynamoDB]
```

## Components

### 1. API Gateway
- **Endpoint**: `POST /ingest`
- **Purpose**: Public HTTP endpoint for receiving logs
- **Response**: 202 Accepted (async processing)

### 2. Lambda Function: ingest-api
- **Purpose**: Validates and normalizes incoming data
- **Accepts**: 
  - JSON with `Content-Type: application/json`
  - Plain text with `Content-Type: text/plain` and `X-Tenant-ID` header
- **Output**: Publishes normalized message to SQS

### 3. SQS Queue: log-processing-queue
- **Type**: Standard queue
- **Purpose**: Decouples API from processing, ensures reliability
- **Benefit**: Handles traffic spikes and worker failures gracefully

### 4. Lambda Function: log-worker
- **Purpose**: Processes logs asynchronously
- **Processing**: 
  - Simulates heavy work (0.05s per character)
  - Redacts sensitive information (phone numbers)
- **Trigger**: SQS messages (automatic)

### 5. DynamoDB Table: tenant_logs
- **Partition Key**: `tenant_id` (ensures data isolation)
- **Sort Key**: `log_id` (unique identifier per log)
- **Multi-tenancy**: Each tenant's data is physically separated by partition key

## Multi-Tenant Architecture

The system ensures complete data isolation between tenants:

1. **At API Level**: Tenant ID extracted from payload or headers
2. **At Queue Level**: Messages include tenant context
3. **At Database Level**: DynamoDB partition key separates data physically

Example data structure:
```
tenants/
  ├── acme_corp/
  │   ├── log_001
  │   ├── log_002
  │   └── log_003
  └── beta_inc/
      ├── log_001
      └── log_002
```

## API Usage

### JSON Request
```bash
curl -X POST https://YOUR-API-ENDPOINT/ingest \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"acme","log_id":"123","text":"User data here"}'
```

### Plain Text Request
```bash
curl -X POST https://YOUR-API-ENDPOINT/ingest \
  -H "Content-Type: text/plain" \
  -H "X-Tenant-ID: acme" \
  -d "Raw log text here"
```

## Scalability Features

1. **Serverless Architecture**: Auto-scales with demand, scales to zero when idle
2. **Async Processing**: API returns immediately, processing happens in background
3. **Queue-based**: SQS handles bursts, retries, and failure recovery
4. **Managed Services**: No servers to maintain, automatic scaling

## Testing

Run the included `test_api.py` script to verify:
- JSON and text ingestion
- Multi-tenant isolation
- Load handling (1000+ RPM capable)
- Data processing and storage

## Cost Optimization

All services used are within AWS Free Tier:
- Lambda: 1M requests/month free
- SQS: 1M requests/month free
- DynamoDB: 25GB storage free
- API Gateway: 1M requests/month free

## Error Handling

- **Invalid requests**: Return 400 with error message
- **Missing tenant ID**: Request rejected
- **Worker failures**: SQS retries automatically
- **Processing errors**: Logged to CloudWatch

## Monitoring

View metrics in AWS Console:
- API Gateway: Request count, latency, errors
- Lambda: Invocations, duration, errors
- SQS: Messages in queue, age of oldest message
- DynamoDB: Read/write capacity, throttles