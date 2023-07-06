from googlestt import SpeechToText
import os

if __name__ == "__main__":

    # Example of how to call STT on encoded audio bytes
    stt = SpeechToText(project_id="autolab-391921",
                       recognizer_id="recognizer1")

    # Reads file specified in open() and feeds it to the STT
    cwd = os.getcwd()
    with open(f"{cwd}/sst_transcription/output.flac", "rb") as fd:
        contents = fd.read()

        # This response contains all the output data from the model
        response = stt.speech_to_text(contents)

        # Check docs for better description, but these two functions will
        # put the results in a more convenient data type.
        # First one just returns a string, prolly use this for gpt.
        print(stt.concatenate_transcripts(response))
        print(stt.get_transcript_list_and_times(response))
