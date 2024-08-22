import boto3
import pymongo
import os
import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import time
from datetime import datetime

# Function to launch an EC2 instance with RHEL GUI
def launch_ec2_instance():
    ec2 = boto3.resource('ec2')
    print("Launching EC2 instance with RHEL GUI...")
    instances = ec2.create_instances(
        ImageId='ami-022ce6f32988af5fa',  # Replace with a RHEL AMI ID
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='redhat_key',  # Replace with your key pair name
        SecurityGroups=['launch-wizard-11'],  # Replace with your security group
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'RHEL-GUI-Instance'}]
            }
        ]
    )
    print(f"Instance {instances[0].id} launched successfully.")

# Function to access logs from CloudWatch
def access_cloud_logs():
    logs = boto3.client('logs')
    log_group = input("Enter the CloudWatch log group name: ")
    log_stream = input("Enter the CloudWatch log stream name: ")
    response = logs.get_log_events(
        logGroupName=log_group,
        logStreamName=log_stream,
        startFromHead=True
    )
    for event in response['events']:
        print(event['message'])

# Function for event-driven architecture with S3 and AWS Transcribe

def event_driven_transcription():
    print("Setting up event-driven transcription...")
    
    s3 = boto3.client('s3')
    transcribe = boto3.client('transcribe')
    
    bucket_name = input("Enter the S3 bucket name: ")
    file_key = input("Enter the S3 file key (e.g., audio.mp3): ")
    
    # Create a unique job name using the file name and timestamp
    job_name = f"{file_key.split('.')[0]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Start the transcription job
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f's3://{bucket_name}/{file_key}'},
        MediaFormat='mp3',
        LanguageCode='en-IN',
        OutputBucketName=bucket_name
    )
    
    print(f"Transcription job '{job_name}' started.")
    
    # Wait for the job to complete
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            break
        print("Waiting for transcription to complete...")
        time.sleep(5)
    
    if job_status == 'COMPLETED':
        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        print(f"Transcription completed. Transcript URI: {transcript_uri}")
        
        # Fetch and print the transcription
        transcript_response = s3.get_object(Bucket=bucket_name, Key=f"{job_name}.json")
        transcript_text = transcript_response['Body'].read().decode('utf-8')
        
        import json
        transcript_data = json.loads(transcript_text)
        print("Transcribed Text:")
        print(transcript_data['results']['transcripts'][0]['transcript'])
    else:
        print(f"Transcription job '{job_name}' failed.")

# Function to connect Python to MongoDB using Lambda
def connect_python_to_mongodb():
   

    print("connecting.....")
    uri = "mongodb+srv://unnatideep40:1122334455667788@cluster0.nudjced.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&ssl=true&tlsAllowInvalidCertificates=true"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))


    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = client.get_database('NewDb')  # Replace with your database name
    collection = db['Data']  # Replace with your collection name
    
    # Example operation
    document = {'nice': 'to meet you'}
    collection.insert_one(document)
    
    print("Document inserted into MongoDB.") 

# Function to upload a file to S3
def upload_object_to_s3():
    s3 = boto3.client('s3')
    file_name_with_path = input("Enter the file name with path to upload: ")
    bucket = input("Enter the S3 bucket name: ")
    file_name = input("enter the file name to display: ")

    try:
        s3.upload_file(file_name_with_path, bucket, file_name)
        print(f"File '{file_name}' uploaded successfully to '{bucket}'.")
    except Exception as e:
        print(f"Error: {e}")

# Function to integrate Lambda with S3 and SES
def lambda_s3_ses_integration():
   s3 = boto3.client('s3')
    file_path = input("Enter the full file path of the email list file: ")
    bucket_name = input("Enter the S3 bucket name: ")
    file_name = os.path.basename(file_path)
    
    try:
        s3.upload_file(file_path, bucket_name, file_name)
        print(f"File '{file_name}' uploaded successfully to S3 bucket '{bucket_name}'.")
        print("Lambda function will be triggered to send emails.")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")


# Menu system
def menu():
    while True:
        print("\nMenu:")
        print("1. Launch EC2 instance with RHEL GUI")
        print("2. Access logs from the cloud (CloudWatch)")
        print("3. Event-driven architecture for audio transcription")
        print("4. Connect Python to MongoDB using Lambda")
        print("5. Upload an object to S3")
        print("6. Integrate Lambda with S3 and SES to send emails")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            launch_ec2_instance()
        elif choice == '2':
            access_cloud_logs()
        elif choice == '3':
            event_driven_transcription()
        elif choice == '4':
            connect_python_to_mongodb()
        elif choice == '5':
            upload_object_to_s3()
        elif choice == '6':
            lambda_s3_ses_integration()
        elif choice == '7':
            print("Exiting the program...")
            sys.exit()
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    menu()
