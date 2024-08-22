import json

import boto3

def lambda_handler(event, context):
    # Initialize clients
    s3 = boto3.client('s3')
    ses = boto3.client('ses')
    
    # Get S3 bucket and object details from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Retrieve the email list file from S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        email_data = response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error retrieving file from S3: {e}")
        raise e

    # Split the email data into a list of email addresses
    email_list = email_data.splitlines()
    
    # Email content
    subject = "Test Email from Lambda"
    body_text = "This is a test email sent by AWS Lambda using Amazon SES."
    sender = "unnatideep2019@gmail"  # Replace with a verified email in SES

    # Send email to each address using SES
    for email in email_list:
        try:
            ses.send_email(
                Source=sender,
                Destination={
                    'ToAddresses': [email],
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            print(f"Email sent to {email} successfully.")
        except Exception as e:
            print(f"Error sending email to {email}: {e}")

    return {
        'statusCode': 200,
        'body': 'Emails sent successfully'
