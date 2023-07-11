"""
lambda_handler.py

TODO

Created: 07/11/2023

Usage:
- TODO
"""

from autolab import Autolab

import json
import requests
from supabase import create_client, Client
from autolab import generate_procedure
from dotenv import load_dotenv
import os

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
service_key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, service_key)
bucket_name: str = os.getenv("SUPABASE_BUCKET_NAME")


def lambda_handler(event, context):
    """
    This function is used as the AWS Lambda handler. It processes a GET request containing a uid of a video file,
    fetches the video file from a Supabase bucket, transcribes the video, and returns the transcript.

    Parameters:
    event (dict): The event object passed by AWS Lambda. This should contain the video uid in 
                  event['queryStringParameters']['uid'].

    context (LambdaContext): The context object passed by AWS Lambda. It provides methods and properties 
                             that provide information about the invocation, function, and execution environment.

    Returns:
    dict: An HTTP response that contains the status code, headers, and body. The body contains the video transcript
          if the processing was successful or an error message if an error occurred.
    """
    try:
        # Parse the uid from incoming event
        uid = event['queryStringParameters']['uid']
        print(uid)

        # Fetch the video from Supabase and store it in tmp/
        tmp_path = f'{os.getcwd()}/tmp/{uid}.mp4'
        with open(tmp_path, 'wb') as f:
            response = supabase.storage.from_(
                bucket_name).download(f'{uid}.mp4')
            f.write(response)

        # Generate transcript from autolab.py and return response
        autolab = Autolab()
        transcript_response = autolab.generate_transcript(tmp_path, cleanup=True, enable_logging=False)
        return {
            'statusCode': 200,
            'body': transcript_response,
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # If any error occurs, return a 500 error. We could try to extract
    # the error code (if its from supabase), but probably not worth it.
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


# Testing
if __name__ == "__main__":
    event = {
        'queryStringParameters': {
            'uid': 'test'
        }
    }
    context = "context"
    print(lambda_handler(event, context))
