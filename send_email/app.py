import json
import boto3
from boto3.dynamodb.conditions import Key
import os

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
ses = boto3.client("ses")
verified_email = os.environ["VERIFIED_EMAIL"]

def lambda_handler(event, context):
    for record in event['Records']:
        body = record.get('body')
        message_body = json.loads(body)
        s3_record = message_body['Records'][0]
        s3_event = s3_record['s3']
        
        bucket_name = s3_event['bucket']['name']
        object_key = s3_event['object']['key']
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()
        
        message = json.loads(file_content.decode('utf-8'))
        
        send_emails(group_id=message["group_id"], content=message["post"])
        
def send_emails(group_id: str, content: str):
    group_pk = f"GROUP#{group_id}"
    users_sk = "USER#"
    
    users_response = table.query(
        KeyConditionExpression=(Key('PK').eq(group_pk) & Key('SK').begins_with(users_sk))
    )
    
    users = users_response["Items"]
    print(f"Found {len(users)} users")
    
    # Build list of user emails
    user_list = []
    for user in users:
        email = user["SK"].split("#")[1]
        user_list.append(email)
        print(f"User: {email}")
    
    # Create HTML with users list
    users_html = "<h3>Group Members:</h3><ul>"
    for email in user_list:
        users_html += f"<li>{email}</li>"
    users_html += "</ul>"
    
    # Combine message content with users list
    full_content = f"{content}<hr>{users_html}"
    
    # Send single email
    email_message = {
        'Subject': {'Data': f"A new message from {group_id}"},
        'Body': {
            'Html': {'Data': full_content},
        }
    }
    
    try:
        response = ses.send_email(
            Source=verified_email,
            Destination={
                'ToAddresses': ['pintolearning@gmail.com'],
            },
            Message=email_message
        )
        
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
    
    except Exception as e:
        print(f"Error sending email: {e}")
