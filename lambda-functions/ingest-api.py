import json
import boto3
import os
from datetime import datetime

# Initialize SQS client
sqs = boto3.client('sqs')
QUEUE_URL = os.environ.get('QUEUE_URL', '')  # We'll set this as environment variable

def lambda_handler(event, context):
    """
    Main handler for the ingestion API
    Processes both JSON and plain text inputs
    """
    try:
        # Get content type from headers
        headers = event.get('headers', {})
        content_type = headers.get('content-type', '').lower()
        
        # Initialize variables
        tenant_id = None
        log_id = None
        text_content = None
        source_type = None
        
        # Process based on content type
        if 'application/json' in content_type:
            # Handle JSON payload
            body = json.loads(event.get('body', '{}'))
            tenant_id = body.get('tenant_id')
            log_id = body.get('log_id', f"log_{datetime.now().timestamp()}")
            text_content = body.get('text', '')
            source_type = 'json_upload'
            
        elif 'text/plain' in content_type:
            # Handle plain text payload
            tenant_id = headers.get('x-tenant-id')
            log_id = f"log_{datetime.now().timestamp()}"
            text_content = event.get('body', '')
            source_type = 'text_upload'
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported content type'})
            }
        
        # Validate required fields
        if not tenant_id or not text_content:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing tenant_id or text content'})
            }
        
        # Prepare message for SQS
        message = {
            'tenant_id': tenant_id,
            'log_id': log_id,
            'text': text_content,
            'source': source_type,
            'received_at': datetime.now().isoformat()
        }
        
        # Send to SQS queue
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        
        # Return success response (202 Accepted for async processing)
        return {
            'statusCode': 202,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Log accepted for processing',
                'tenant_id': tenant_id,
                'log_id': log_id
            })
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
