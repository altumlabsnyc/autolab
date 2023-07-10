"""
pipeline.py

This module runs the entire Autolab pipeline, and serves as the most basic version of Autolab

Contributers: Ricky Fok, Izzy Qian, Grant Rinehimer
Created: 07/06/2023

Usage:
- python3 pipeline.py
- Edit all parameters in the JSON file
- For now, you need to delete the output files if you plan to rerun the pipeline with the same output directories

"""
from sst_transcription.googlestt import SpeechToText
from instruction_generator.gpt_transcript import TranscriptConversion


import json
import os
import ffmpeg
from dotenv import load_dotenv

if __name__ == "__main__":
    # major.minor.patch-pre_release_label
    print("Autolab v0.1.0-alpha")
    print("_" * 20 + "\n")

    # print ("Gcloud Authenticating...")
    # os.system('cmd /k "gcloud auth application-default login"')

    print ("Reading JSON...")

    # all dir in the JSON assume we are in the autolab/ directory
    with open("inputs.json") as file:
        data = json.load(file)
        print("Success!\n")

    cwd = os.getcwd()
    print(cwd)

    # Load variables for stt and instruction generation
    stt_vars = data["transcription_variables"]
    instr_vars = data["instruction_variables"]
    vid_vars = data["video_conversion_variables"]

    # 1) Read and Convert mp4 File to .flac
    ###############################################
    print("Generating .flac file")

    {
        ffmpeg
        .input(cwd + vid_vars["input_dir"])
        .output(cwd + vid_vars["output_dir"], acodec='flac')
        .run(quiet=True)
    }

    print("Success (1/3)\n")

    # 2) SpeechToText Transcription
    ###############################################
    print("Generating SpeechToText Transcription...")

    stt = SpeechToText(project_id=stt_vars["project_id"],
                       recognizer_id=stt_vars["recognizer_id"])
    
    with open(cwd + stt_vars["input_dir"], "rb") as fd:
        contents = fd.read()
    response = stt.speech_to_text(contents)

    transcript_concat = stt.concatenate_transcripts(response)
    transcript_time = stt.get_transcript_list_and_times(response)

    # convert transcript_time into string
    format_transcript_time = ""
    for item in transcript_time:
        text = item[0]
        start_time = item[1]
        end_time = item[2]
        format_transcript_time += f"{text} [{start_time}-{end_time}]\n"

    print("Done! Saving...")
    with open(cwd + stt_vars["output_dir"], "w") as file:
        file.write(format_transcript_time)
    #@TODO need to also store transcript_concat

    print("Success (2/3)\n")

    # 2) Instruction Generation
    ###############################################
    print("Generating Instructions...")

    transcription_dir = cwd + instr_vars["input_dir"]
    instr_dir = cwd + instr_vars["output_dir"]

    load_dotenv()
    secret_key = os.getenv('OPENAI_API_KEY')
    instr_generator = TranscriptConversion(model=instr_vars["model"], secret_key=secret_key)
    instr_set = instr_generator.generateInstructions(transcript_dir=transcription_dir)

    print("Done! Saving...")
    if instr_set != None:
        with open(instr_dir, "w") as file:
            file.write(instr_set)
    else:
        print("Error: Instruction Set has not been generated")
    
    print("Success (3/3)\n")
    print("_" * 20 + "\n")
    print(f'Instructions saved to \"%s\"\nAutolab terminating' % instr_dir)