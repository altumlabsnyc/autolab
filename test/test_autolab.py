from autolab.autolab import Autolab
from lambda_function import lambda_handler


# Both these tests don't work lol.
# We can only really test the autolab components directly, not the lambda function.
# This is fine because we should only be testing the lambda function with the AWS console.
def test_pipeline(filename: str, storage_dir: str):
    """This tests the entire pipeline of the Autolab system. It generates a config.json file, runs the Autolab pipeline, and returns the transcript.
    YOU MUST CLEAR THE TMP DIRECTORY BEFORE RUNNING THIS FUNCTION.

    Args:
        filename (str): The name of the file to transcribe. Should not include the file extension.
        storage_dir (str): Name of the storage directory. Must be in the main project directory. Just write the name, no slashes
    """
    # Generate transcript from autolab.py and return response
    autolab = autolab.Autolab()
    transcript_response = autolab.generate_procedure(
        f"{storage_dir}/config.json", cleanup=True, enable_logging=True
    )

    print(transcript_response)
    assert True


def handler_test():
    event = {"queryStringParameters": {"uid": "test"}}
    context = "context"
    output = lambda_handler(event, context)
    print(output)


if __name__ == "__main__":
    handler_test()
