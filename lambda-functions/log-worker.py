import json

import boto3

import time

import re

from datetime import datetime

from decimal import Decimal

# Initialize DynamoDB client

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('tenant_logs')

def lambda_handler(event, context):

    """

    Worker function that processes logs from SQS

    Simulates heavy processing and stores in DynamoDB

    """

    

    # Process each message from SQS

    for record in event.get('Records', []):

        try:

            # Parse the message

            message = json.loads(record['body'])

            

            tenant_id = message['tenant_id']

            log_id = message['log_id']

            text_content = message['text']

            source_type = message['source']

            

            # Simulate heavy processing (0.05s per character)

            processing_time = len(text_content) * 0.05

            print(f"Processing log {log_id} for tenant {tenant_id}")

            print(f"Text length: {len(text_content)} chars, sleeping for {processing_time}s")

            

            # Sleep to simulate CPU-intensive work

            time.sleep(processing_time)

            

            # Modify the data (example: redact phone numbers)

            modified_text = redact_sensitive_data(text_content)

            

            # Store in DynamoDB with proper tenant isolation

            # Convert float to Decimal for DynamoDB compatibility

            table.put_item(

                Item={

                    'tenant_id': tenant_id,  # Partition key

                    'log_id': log_id,        # Sort key

                    'source': source_type,

                    'original_text': text_content,

                    'modified_data': modified_text,

                    'processed_at': datetime.now().isoformat(),

                    'processing_time_seconds': Decimal(str(processing_time))  # Convert to Decimal

                }

            )

            

            print(f"Successfully processed and stored log {log_id} for tenant {tenant_id}")

            

        except Exception as e:

            print(f"Error processing message: {str(e)}")

            # In production, you might want to send this to a DLQ (Dead Letter Queue)

            raise e

    

    return {

        'statusCode': 200,

        'body': json.dumps('Processing complete')

    }

def redact_sensitive_data(text):

    """

    Example function to modify data - redacts phone numbers

    """

    # Simple phone number pattern (US format)

    phone_pattern = r'\b\d{3}-\d{4}\b|\b\d{3}-\d{3}-\d{4}\b'

    modified_text = re.sub(phone_pattern, '[REDACTED]', text)

    

    # You can add more redaction patterns here

    # Email pattern example:

    # email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # modified_text = re.sub(email_pattern, '[EMAIL_REDACTED]', modified_text)

    

    return modified_text
