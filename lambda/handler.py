import json
import os
import boto3
import urllib.request
import datetime
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Get environment variables
    slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    ddb_table_name = os.environ['DDB_TABLE_NAME']
    
    # Initialize AWS clients
    sns = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ddb_table_name)
    
    # Validate event
    if 'Records' not in event or not event['Records']:
        logger.error("No records found in the event")
        return {
            'statusCode': 400,
            'body': json.dumps('No records to process')
        }

    # Process the S3 event
    for record in event['Records']:
        try:
            # Extract S3 information
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            size = record['s3']['object']['size']
            event_time = record['eventTime']
        except KeyError as e:
            logger.error(f"Missing expected key in event record: {e}")
            continue

        # Format message
        message = f"""New file uploaded to S3!
Bucket: {bucket}
File: {key}
Size: {size} bytes
Time: {event_time}"""

        # Send Slack notification
        slack_data = {
            "text": message,
            "username": "AWS S3 Alert",
            "icon_emoji": ":aws:"
        }
        slack_message = json.dumps(slack_data).encode('utf-8')

        req = urllib.request.Request(
            slack_webhook_url,
            data=slack_message,
            headers={'Content-Type': 'application/json'}
        )

        try:
            response = urllib.request.urlopen(req)
            logger.info(f"Slack notification sent: {response.status}")
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")

        # Publish to SNS
        try:
            sns_response = sns.publish(
                TopicArn=sns_topic_arn,
                Subject=f"S3 Upload Alert: {key}",
                Message=message
            )
            logger.info(f"SNS notification sent: {sns_response}")
        except Exception as e:
            logger.error(f"Error publishing to SNS: {e}")

        # Store metadata in DynamoDB
        current_time = datetime.datetime.now().isoformat()
        try:
            ddb_response = table.put_item(
                Item={
                    'fileName': key,
                    'uploadTimestamp': current_time,
                    'bucket': bucket,
                    'size': size,
                    'eventTime': event_time
                }
            )
            logger.info(f"DynamoDB item created: {ddb_response}")
        except Exception as e:
            logger.error(f"Error creating DynamoDB item: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete!')
    }

