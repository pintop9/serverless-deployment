mport json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    group_id = path_params.get("group-id")
    if not group_id:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing group-id"})}

    raw_body = event.get("body")
    if not raw_body:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing body"})}

    try:
        body = json.loads(raw_body)
        user_email = body.get("email", "").strip()
        if not user_email:
            raise ValueError
    except:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Valid email required"})}

    table.put_item(
        Item={
            "PK": f"{group_id}",
            "SK": f"{user_email}",     # ← USER# prefix only here
        }
    )

    # 2. User → Group (user's group list)
    table.put_item(
        Item={
            "PK": f"{user_email}",
            "SK": f"{group_id}",      # ← GROUP# prefix only here
        }
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": "User joined group successfully",
            "group_id": group_id
        })
    }
