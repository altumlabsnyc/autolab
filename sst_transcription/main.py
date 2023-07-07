from googlestt import SpeechToText
import os

if __name__ == "__main__":

    # Example of how to call STT on encoded audio bytes
    stt = SpeechToText(project_id="autolab-391921",
                       recognizer_id="recognizer1")

    # Reads file specified in open() and feeds it to the STT
    cwd = os.getcwd()
    # print(cwd)

    with open(f"{cwd}/data/wetlab1_flac/output.flac", "rb") as fd:
        contents = fd.read()

    # This response contains all the output data from the model
    response = stt.speech_to_text(contents)

    # Check docs for better description, but these two functions will
    # put the results in a more convenient data type.
    # First one just returns a string, prolly use this for gpt.
    transcript_concat = stt.concatenate_transcripts(response)
    transcript_time = stt.get_transcript_list_and_times(response)

    print(transcript_concat)
    print(transcript_time)

    # place them in txt files for future use
    # with open(f"{cwd}/sst_transcription/output/transcript_concat.txt", "w") as file:
    #     file.write(transcript_concat)

    format_transcript_time = ""
    for item in transcript_time:
        text = item[0]
        start_time = item[1]
        end_time = item[2]
        format_transcript_time += f"{text} [{start_time}-{end_time}]\n"
    # print(format_transcript_time)
    with open(f"{cwd}/sst_transcription/output/transcript_time.txt", "w") as file:
        file.write(format_transcript_time)
    