mport json

def lambda_handler(event, context):
    for record in event['Records']:
        body = record.get('body')
        message_body = json.loads(body)
        s3_record = message_body['Records'][0]
        s3_event = s3_record['s3']
        

        bucket_name = s3_event['bucket']['name']
        object_key = s3_event['object']['key']

        print(f"Bucket Name: {bucket_name}")
        print(f"Object Key: {object_key}")

