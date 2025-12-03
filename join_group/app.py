import json
import boto3
import os
from urllib.parse import unquote
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    print("Full event:", json.dumps(event))
    
    path_params = event.get("pathParameters") or {}
    group_id = path_params.get("group-id")
    
    # URL decode the group_id
    if group_id:
        group_id = unquote(group_id)
    
    print(f"Decoded group_id: {group_id}")
    
    if not group_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing group-id"})
        }
    
    # Add GROUP# prefix if not present
    if not group_id.startswith("GROUP#"):
        group_id = f"GROUP#{group_id}"
    
    raw_body = event.get("body")
    if not raw_body:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing body"})
        }
    
    try:
        body = json.loads(raw_body)
        raw_email = body.get("email", "").strip()
        if not raw_email:
            raise ValueError
    except:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Valid email required"})
        }
    
    # Extract username and create standardized email
    username = raw_email.split('@')[0]
    email = f"USER#{username}@m.io"
    
    response = table.query(
        KeyConditionExpression=Key('PK').eq(group_id) & Key('SK').begins_with(f"USER#{username}")
    )
    
    if response['Count'] == 0:
        table.put_item(
            Item={
                "PK": group_id,
                "SK": email,
            }
        )
        table.put_item(
            Item={
                "PK": f"USER#{username}@mail.com",
                "SK": group_id,
            }
        )
        return {
            "statusCode": 200, 
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*", 
                "Access-Control-Allow-Methods": "POST",
            },
            "body": json.dumps({
                "message": f"User {username} added successfully",
                "group_id": group_id
            })
        }
    else:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": f"User {username} is already in this group",
                "group_id": group_id
            })
        }
