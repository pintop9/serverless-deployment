import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    print("Full event:", json.dumps(event))
    
    path_params = event.get("pathParameters") or {}
    group_id = path_params.get("group-id")
    
    if not group_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing group-id"})
        }
    
    raw_body = event.get("body")
    if not raw_body:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing body"})
        }
    
    try:
        body = json.loads(raw_body)
        email = body.get("email", "").strip()
        if not email:
            raise ValueError
    except:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Valid email required"})
        }
    
    username = email.split('#')[1].split('@')[0]
    
    response = table.query(
        KeyConditionExpression=Key('PK').eq(group_id) & Key('SK').begins_with(f"USER#{username}")
    )
    
    if response['Count'] == 0:
        table.put_item(
            Item={
                "PK": f"{group_id}",
                "SK": f"{email}",
            }
        )
        table.put_item(
            Item={
                "PK": f"USER#{username}@mail.com",
                "SK": f"{group_id}",
            }
        )
        return {
        "statusCode": 200, 
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*", 
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps({
        "message": f"User {username} added to group successfully",
        "group_id": group_id
    }
    else:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": f"User {username} is already in this group",
                "group_id": group_id
            })
        }
