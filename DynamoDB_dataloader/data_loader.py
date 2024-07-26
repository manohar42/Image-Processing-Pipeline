import boto3
import json

# Replace 'your_table_name' with the name of your DynamoDB table
table_name = 'student-academic-records'

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Read the JSON file
with open('student_data.json') as f:
    data = json.load(f)

# Get the DynamoDB table
table = dynamodb.Table(table_name)

# Upload each item in the JSON file to the DynamoDB table
with table.batch_writer() as batch:
    for item in data:
        batch.put_item(Item=item)
        print("Inserted item")
