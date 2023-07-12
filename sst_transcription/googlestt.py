"""
googlesst.py

This module utilizes speech to text via Google's Cloud Platform
to extract a transcript from video

Created: 07/07/2023

"""
from google.cloud import speech_v2
from typing import List, Tuple
import dotenv


class SpeechToText:
    """Class that handles API calls to Google Speech.
    """

    def __init__(self, project_id, recognizer_id):
        """Constructor - Sets up Google client and configuration.

        Args:
            project_id (_type_): Google Project ID
            recognizer_id (_type_): Speech Recognizer to be used (must run create_recognizer if it does not already)
        """
        dotenv.load_dotenv()
        self.__client = speech_v2.SpeechClient()
        self.project_id = project_id
        self.recognizer_id = recognizer_id
        self.__config = speech_v2.RecognitionConfig(
            auto_decoding_config=speech_v2.AutoDetectDecodingConfig())

    def speech_to_text(self,
                       content: bytes = 0,
                       ) -> speech_v2.RecognizeResponse:
        """Calls the STT Recognizer model on [content] and returns response

        Args:
            content (bytes, optional): Encoded audio to be transcribed (should auto detect transcoding, but preferably use FLAC). Defaults to 0.

        Returns:
            speech_v2.RecognizeResponse: Returns response containing result from the model (the transcription and other metadata)
        """

        request = speech_v2.RecognizeRequest(
            recognizer=f"projects/{self.project_id}/locations/global/recognizers/{self.recognizer_id}",
            content=content,
            config=self.__config
        )
        response = self.__client.recognize(request=request)

        return response

    def create_recognizer(self) -> speech_v2.RecognizeResponse:
        """You must call this function if the recognizer does not exist.

        Throws:
            Error if a recognizer already exists with that id.
        """

        # Initialize request arguments
        request = speech_v2.CreateRecognizerRequest(
            parent=f"projects/{self.project_id}/locations/global",
            recognizer=speech_v2.Recognizer(
                display_name=self.recognizer_id, language_codes=["en-US"], model="latest_long"),
            recognizer_id=self.recognizer_id
        )

        # Make the request
        operation = self.__client.create_recognizer(request=request)
        print("Waiting on create_recognizer operation...")

    def concatenate_transcripts(self, response: speech_v2.RecognizeResponse) -> str:
        """
        Concatenates the transcripts from each result in a speech_v2.RecognizeResponse.

        Args:
            response (speech_v2.RecognizeResponse): The response from the Google Cloud Speech-to-Text service.

        Returns:
            str: The concatenated transcripts.
        """
        transcripts = []
        for result in response.results:
            transcripts.append(result.alternatives[0].transcript)
        return "".join(transcripts)

    def get_transcript_list_and_times(self, response: speech_v2.RecognizeResponse) -> List[Tuple[str, float, float]]:
        """
        Returns a list of triples containing the transcript, start time, and end time for each result in a speech_v2.RecognizeResponse.

        The start time for each result is the end time of the previous result, and the start time for the first result is 0 seconds.

        Args:
            response (speech_v2.RecognizeResponse): The response from the Google Cloud Speech-to-Text service.

        Returns:
            List[Tuple[str, float, float]]: A list of triples, where each triple contains a transcript (str), start time (float), and end time (float).
        """
        results = []
        previous_end_time = 0.0  # Start time for the first result

        for result in response.results:

            transcript = result.alternatives[0].transcript
            end_time = float(result.result_end_offset.seconds)

            results.append((transcript, previous_end_time, end_time))

            previous_end_time = end_time

        return results
