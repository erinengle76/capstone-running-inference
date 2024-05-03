import boto3
import json

def lambda_handler(event, context):
    # Extracting information from the event
    bucket = event['queryStringParameters']['lambda-image-storage']
    image_key = event['queryStringParameters']['image_key']

    # Accessing the image from S3
    s3 = boto3.client('s3')
    try:
        image_response = s3.get_object(Bucket=bucket, Key=image_key)
        image_content = image_response['Body'].read()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Adjust as necessary for security
            },
            'body': json.dumps({'error': str(e)})
        }

    # Configuring SageMaker client
    sage_client = boto3.client('sagemaker-runtime')

    try:
        # Invoking the SageMaker endpoint
        response = sage_client.invoke_endpoint(
            EndpointName='<INSERT-ENDPOINT-NAME>',
            ContentType='image/jpeg',
            Body=image_content
        )
        # Processing SageMaker response
        result = response['Body'].read().decode('utf-8')
        response_body = {'result': result}
        status_code = 200
    except Exception as e:
        response_body = {'error': str(e)}
        status_code = 500

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # This allows all domains
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',  # Adjust based on your needs
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'  # Ensure these match what you need for your API
        },
        'body': json.dumps(response_body)
    }
