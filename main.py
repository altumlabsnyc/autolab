from googlestt import SpeechToText


if __name__ == "__main__":

    # Example of how to call STT on encoded audio bytes
    stt = SpeechToText(project_id="autolab-391921",
                       recognizer_id="recognizer1")

    audio = 0
    response = stt.speech_to_text(audio)
    print(response)
