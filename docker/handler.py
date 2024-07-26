# Import necessary modules
from fileinput import filename
from boto3 import client as boto3_client
import face_recognition
import pickle
import urllib.parse
import boto3
# import botocore
import os
import ffmpeg
import csv
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

# Specify the directory paths
current_directory = os.getcwd()
video_directory =  "/tmp/video/"
images_directory = "/tmp/images/"

# Create the directories if they don't exist
os.makedirs(video_directory, exist_ok=True)
os.makedirs(images_directory, exist_ok=True)

# Initialize AWS services
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Set the DynamoDB table name
table_name = 'student-academic-records'
table = dynamodb.Table(table_name)


# Constants for your S3 bucket and object
output_bucket_name = 'cse546-paas-output-bucket-results'
encoding_file_path = current_directory + "/encoding.dat"

# Function to download the video from S3
def download_video_from_s3(bucket_name, object_key, destination_path):
    print("================================================================ start download_video_from_s3 ")
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        data = response['Body'].read()
        with open(destination_path + object_key, 'wb') as f:
            f.write(data)
        s3.delete_object(Bucket=bucket_name, Key=object_key)
        print("*************************************************************** done download_video_from_s3 ")
    except Exception as e:
        print(f'Error while downloading video from S3: {e}')

# Function to extract images from the video
def extract_images_from_video(video_path, image_output_path):
    print("================================================================ start extract_images_from_video ")
    try:
        os.system(f"ffmpeg -i {video_path} -r 1 {image_output_path}image-%3d.jpeg")
        print("*************************************************************** done extract_images_from_video ")
    except Exception as e:
        print(f'Error while extracting images: {e}')


# Process image and return result
def process_image(img_path):
    print("================================================================ start process_image ")
    image_files = face_recognition.load_image_file(img_path)
    image_file_encoding = face_recognition.face_encodings(image_files)[0]

    # get known face encodings from file
    with open(encoding_file_path, 'rb') as f: 
        face_names_and_encoding = pickle.load(f)
        known_names = face_names_and_encoding['name']
        known_face_encodings = face_names_and_encoding['encoding']
    # compare known face with unknown face encodings
    result = face_recognition.compare_faces(known_face_encodings, image_file_encoding)
    for ans in result:
        if ans:
            index = result.index(ans)
            print("*************************************************************** done process_image ")
            return (known_names[index])
    

# Function to retrieve data from DynamoDB
def get_target_from_dynamodb(name):
        print("================================================================ start get_target_from_dynamodb ")       
        try:
            response = table.scan(FilterExpression=Attr('name').eq(name))
            items = response.get('Items', [])
            if items:
                print("*************************************************************** done get_target_from_dynamodb ")
                return items[0]  # Assuming name is unique, so we return the first match
        except Exception as e:
            print(f"An error occurred while querying the table: {e}")
        return None

# Function to create a CSV file
def create_csv_file(object_key, record):
    print("================================================================ start create_csv_file ")
    print("creating csv file")
    print(record)
    # Define the CSV file path
    print(record["name"])
    filename = object_key +"_"+ record["name"] + ".csv"
    filepath =  '/tmp/' + object_key + filename

    # Write data to the CSV file
    with open(filepath, 'w') as csvfile: 
        filewriter = csv.writer(csvfile, delimiter=',',
                            quoting=csv.QUOTE_MINIMAL)               
        filewriter.writerow(['Name','Major','Year'])
        filewriter.writerow([record['name'], record['major'], record['year']])

    # Upload the CSV file to the output S3 bucket
    print("upload file started")
    s3.upload_file(
                    Bucket = output_bucket_name,
                    Filename = filepath,
                    Key = filename
                )  
    print("upload file completed")      
    os.remove(filepath)
    print("*************************************************************** done create_csv_file ")
    # return filename  


# Lambda function for processing facial recognition
def face_recognition_handler(event, context):   

    bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try : 
        download_video_from_s3(bucket, object_key, video_directory)

        extract_images_from_video(video_directory + object_key, images_directory)
    
        target_name = process_image(images_directory+ "image-001.jpeg")

        result = get_target_from_dynamodb(target_name)

        create_csv_file(object_key, result)

    except Exception as e :
        print(e)
        raise e

    '''
    # example for event data
    event = 
    {
    "Records": [
        {
            "eventVersion": "2.1", 
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "2023-10-27T06:33:59.544Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "AWS:AIDAZYSJTIT5THD7UDHZE"
            },
            "requestParameters": {
                "sourceIPAddress": "72.196.86.50"
            },
            "responseElements": {
                "x-amz-request-id": "6Q24XTFJ3A3BJ2CJ",
                "x-amz-id-2": "cY12aIow+yMlDa5RZlqkrn8h1WkSmHmD8TS6Stw1LjEUB026g1qpbwwUJmUS/C5mgXAKj9q1y0FsScmOoVBYRnfH5jPSsPlf"
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "069d492b-28b9-43a1-aaa7-1aa32edc6a51",
                "bucket": {
                    "name": "paas-input-bucket-videos",
                    "ownerIdentity": {
                        "principalId": "AZ2PS6I7DNYSV"
                    },
                    "arn": "arn:aws:s3:::paas-input-bucket-videos"
                },
                "object": {
                    "key": "test_5.mp4",
                    "size": 1719624,
                    "eTag": "e4af7894fcd0a4ad49c88fb8e7413f79",
                    "sequencer": "00653B59D763ED466C"
                }
            }
        }
    ]
}
    '''