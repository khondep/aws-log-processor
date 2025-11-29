# Deployment Guide

## Prerequisites
- AWS Account (Free Tier)
- Python 3.11+
- AWS CLI (optional)

## AWS Services Used
- API Gateway (HTTP API)
- Lambda Functions (x2)
- SQS (Standard Queue)
- DynamoDB (NoSQL Database)

## Step-by-Step Deployment

### 1. DynamoDB Setup
1. Create table named `tenant_logs`
2. Partition key: `tenant_id` (String)
3. Sort key: `log_id` (String)

### 2. SQS Setup
1. Create Standard Queue named `log-processing-queue`
2. Set Visibility timeout to 360 seconds
3. Copy the Queue URL

### 3. Lambda Functions

#### API Function (ingest-api)
1. Create Lambda function with Python 3.11
2. Copy code from `lambda-functions/ingest-api.py`
3. Set environment variable:
   - `QUEUE_URL`: Your SQS Queue URL
4. Set timeout to 30 seconds
5. Add IAM policy: `AmazonSQSFullAccess`

#### Worker Function (log-worker)
1. Create Lambda function with Python 3.11
2. Copy code from `lambda-functions/log-worker.py`
3. Set timeout to 5 minutes (300 seconds)
4. Add IAM policies:
   - `AmazonSQSFullAccess`
   - `AmazonDynamoDBFullAccess`
5. Add SQS trigger:
   - Source: `log-processing-queue`
   - Batch size: 1

### 4. API Gateway Setup
1. Create HTTP API
2. Add integration: Lambda → `ingest-api`
3. Configure route: `POST /ingest`
4. Deploy to stage `$default`
5. Copy Invoke URL

## Testing

### Test Endpoints
```bash
# JSON Format
curl -X POST https://YOUR-API-URL/ingest \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"test","log_id":"001","text":"Test message"}'

# Text Format  
curl -X POST https://YOUR-API-URL/ingest \
  -H "Content-Type: text/plain" \
  -H "X-Tenant-ID: test" \
  -d "Raw log text"
```

### Run Test Suite
```bash
cd tests
pip install requests
# Update API_ENDPOINT in test_api.py
python test_api.py
```

## Monitoring
- CloudWatch Logs: Check Lambda function logs
- SQS Console: Monitor message queue
- DynamoDB: Verify data storage

## Architecture


## Cost
All services used are within AWS Free Tier:
- Lambda: 1M requests/month free
- SQS: 1M requests/month free
- DynamoDB: 25GB storage free
- API Gateway: 1M requests/month free
