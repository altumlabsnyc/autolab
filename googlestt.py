from google.cloud import speech_v2


class SpeechToText:
    """Class that handles API calls to Google Speech.
    """

    def __init__(self, project_id, recognizer_id):
        """Sets up Google client and configuration.

        Args:
            project_id (_type_): Google Project ID
            recognizer_id (_type_): Speech Recognizer to be used (must run create_recognizer if it does not already)
        """

        self.__client = speech_v2.SpeechClient()
        self.project_id = project_id
        self.recognizer_id = recognizer_id
        self.__config = speech_v2.RecognitionConfig(
            auto_decoding_config=speech_v2.AutoDetectDecodingConfig())

    def speech_to_text(self,
                       content: bytes = 0,
                       ) -> speech_v2.RecognizeResponse:
        """_summary_

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
