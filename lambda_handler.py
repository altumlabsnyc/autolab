"""
lambda_handler.py

Acts as the interface to AWS Lambda. This file is used to process a GET request containing a uid of a video file,

Created: 07/11/2023

Usage:
- At the moment, this file is not used directly. It is used by AWS Lambda to process a GET request containing a uid of a video file.
"""

from autolab import Autolab

import json
import shutil
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import logging

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
service_key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, service_key)
bucket_name: str = os.getenv("SUPABASE_BUCKET_NAME")
project_id: str = os.getenv("PROJECT_ID")
recognizer_id: str = os.getenv("RECOGNIZER_ID")
config_path: str = "tmp/config.json"
tmp_dir: str = 'tmp'


def generate_config(uid: str, storage_dir: str = tmp_dir):
    """Generates the config file used as input for generate_procedure

    Args:
        uid (str): The supabase uid for the video to generate the config for. 
    """

    config = {
        "variables": {
            "vid_input_path": f"/{storage_dir}/{uid}.mp4",
            "vid_convert_dir": f"/{storage_dir}",
            "transcript_path": f"/{storage_dir}/{uid}.txt",
            "project_id": f"{project_id}",
            "recognizer_id": f"{recognizer_id}",
            "instr_path": f"/{storage_dir}/{uid}_procedure.json",
            "model": "text-davinci-003"
        }
    }

    # Write config to JSON file
    with open(f'{storage_dir}/config.json', 'w') as f:
        json.dump(config, f, indent=4)


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
            config_path, cleanup=True, enable_logging=True)
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
    finally:
        # code to delete all files in /tmp/
        tmp = f'{os.getcwd()}/{tmp_dir}'

        for filename in os.listdir(tmp):
            file_path = os.path.join(tmp, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.warning(f'Failed to delete {file_path}. Reason: {e}')
