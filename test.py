import os
from lambda_handler import lambda_handler, generate_config


def handler_test():

    tmp_dir = f"tmp/"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    generate_config("test")
    event = {
        'queryStringParameters': {
            'uid': 'test'
        }
    }
    context = "context"
    output = lambda_handler(event, context)
    print(output)


if __name__ == "__main__":
    handler_test()
