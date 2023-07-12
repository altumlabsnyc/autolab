import os
from lambda_handler import lambda_handler, generate_config
from autolab import Autolab


def test_pipeline(filename: str, storage_dir: str):
    """This tests the entire pipeline of the Autolab system. It generates a config.json file, runs the Autolab pipeline, and returns the transcript.
    YOU MUST CLEAR THE TMP DIRECTORY BEFORE RUNNING THIS FUNCTION.

    Args:
        filename (str): The name of the file to transcribe. Should not include the file extension.
        storage_dir (str): Name of the storage directory. Must be in the main project directory. Just write the name, no slashes
    """

    # Generate config.json
    generate_config(filename, storage_dir=storage_dir)

    # Generate transcript from autolab.py and return response
    autolab = Autolab()
    transcript_response = autolab.generate_procedure(
        f'{storage_dir}/config.json', cleanup=True, enable_logging=True)

    print(transcript_response)


def handler_test():

    tmp_dir = f"tmp/"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    event = {
        'queryStringParameters': {
            'uid': 'test'
        }
    }
    context = "context"
    output = lambda_handler(event, context)
    print(output)


if __name__ == "__main__":
    test_pipeline('sec1', 'test_storage')
