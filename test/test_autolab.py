from autolab.gpt_transcript import TranscriptConversion
from lambda_function import lambda_handler

# Both these tests don't work lol.
# We can only really test the autolab components directly, not the lambda function.
# This is fine because we should only be testing the lambda function with the AWS console.


def test_handler():
    event = {"queryStringParameters": {"uid": "test"}}
    context = "context"
    output = lambda_handler(event, context)
    print(output)


if __name__ == "__main__":
    test_handler()
