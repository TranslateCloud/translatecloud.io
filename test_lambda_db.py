"""
Test database schema by invoking Lambda function
Since RDS is in a VPC, we can't connect directly from local machine
"""
import boto3
import json

lambda_client = boto3.client('lambda', region_name='eu-west-1')

# Create a test payload to invoke Lambda
payload = {
    "httpMethod": "GET",
    "path": "/api/test/db-schema",
    "headers": {},
    "body": ""
}

print("Invoking Lambda function to check database schema...")
print("This will execute inside the VPC where RDS is accessible\n")

try:
    response = lambda_client.invoke(
        FunctionName='translatecloud-api',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    # Parse response
    response_payload = json.loads(response['Payload'].read())

    print("Lambda Response:")
    print(json.dumps(response_payload, indent=2))

    if response.get('FunctionError'):
        print(f"\n[ERROR] Lambda function error: {response.get('FunctionError')}")

except Exception as e:
    print(f"[ERROR] Failed to invoke Lambda: {e}")
