from googlestt import SpeechToText
from google.cloud import speech_v2
from dotenv import load_dotenv
from google.cloud.speech_v2 import RecognitionConfig, AutoDetectDecodingConfig
import os


def auth_test():
    client = speech_v2.SpeechClient()

    # Specify a configuration for the audio file

    # Specify an audio file. This is a short piece of silence
    # so it won't return any transcriptions, but it will test the API
    audio = {"uri": "gs://cloud-samples-data/speech/brooklyn_bridge.flac"}

    project_id = os.getenv("PROJECT_ID")
    recognizer_id = os.getenv("RECOGNIZER_ID")

    response = client.recognize(
        uri=audio['uri'], recognizer=f"projects/{project_id}/locations/global/recognizers/{recognizer_id}",
        config=RecognitionConfig(
            auto_decoding_config=AutoDetectDecodingConfig()
        )
    )

    # If the request is successful, the client is properly authenticated
    print("Client is properly authenticated")


if __name__ == '__main__':
    load_dotenv()
    auth_test()
