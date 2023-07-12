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
from dotenv import load_dotenv
import os

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
service_key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, service_key)
bucket_name: str = os.getenv("SUPABASE_BUCKET_NAME")
project_id: str = os.getenv("PROJECT_ID")
recognizer_id: str = os.getenv("RECOGNIZER_ID")
config_path: str = "config.json"


def generate_config(uid: str):
    """Generates the config file used as input for generate_procedure

    Args:
        uid (str): The supabase uid for the video to generate the config for. 
    """

    config = {
        "variables": {
            "vid_input_path": f"/tmp/{uid}.mp4",
            "vid_convert_path": f"/tmp/{uid}.flac",
            "transcript_path": f"/tmp/{uid}.txt",
            "project_id": f"{project_id}",
            "recognizer_id": f"{recognizer_id}",
            "instr_path": f"/tmp/{uid}_procedure.json"
        }
    }

    # # Write config to JSON file
    # with open(config_path, 'w') as f:
    #     json.dump(config, f, indent=4)


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

        # Fetch the video from Supabase and store it in tmp/
        tmp_path = f'{os.getcwd()}/tmp/{uid}.mp4'
        with open(tmp_path, 'wb') as f:
            response = supabase.storage.from_(
                bucket_name).download(f'{uid}.mp4')
            f.write(response)

        # Generate config.json
        generate_config(uid)

        # Generate transcript from autolab.py and return response
        autolab = Autolab()
        transcript_response = autolab.generate_procedure(
            config_path, cleanup=True, enable_logging=False)
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
        raise e
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


# Testing
if __name__ == "__main__":
    generate_config("test")
    event = {
        'queryStringParameters': {
            'uid': 'test'
        }
    }
    context = "context"
    print(lambda_handler(event, context))
