from google.cloud import speech_v2


class SpeechToText:

    def __init__(self, project_id, recognizer_id):
        self.__client = speech_v2.SpeechClient()
        self.project_id = project_id
        self.recognizer_id = recognizer_id
        self.__config = speech_v2.RecognitionConfig(
            auto_decoding_config=speech_v2.AutoDetectDecodingConfig())

    def speech_to_text(self,
                       content: bytes = 0,
                       ) -> speech_v2.RecognizeResponse:

        request = speech_v2.RecognizeRequest(
            recognizer=f"projects/{self.project_id}/locations/global/recognizers/{self.recognizer_id}",
            uri="gs://cloud-samples-data/speech/brooklyn_bridge.flac",
            config=self.__config
        )
        response = self.__client.recognize(request=request)

        print(response)

    def create_recognizer(self):

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

        # Print Response
        response = operation.result()

        print(response)
    '''
    def print_response(self, response: speech_v2.RecognizeResponse):
        for result in response.results:
            print_result(result)

    def print_result(self,result: speech_v2.SpeechRecognitionResult):
        best_alternative = result.alternatives[0]
        print("-" * 80)
        print(f"language_code: {result.language_code}")
        print(f"transcript:    {best_alternative.transcript}")
        print(f"confidence:    {best_alternative.confidence:.0%}")
    '''


if __name__ == "__main__":

    stt = SpeechToText(project_id="autolab-391921",
                       recognizer_id="recognizer1")

    # stt.create_recognizer()
    stt.speech_to_text()
