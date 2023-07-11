"""
pipeline.py

This module runs the entire Autolab pipeline, and serves as the most basic version of Autolab. This includes:
   - Video conversion into optimal audio format
   - SpeechToText Conversion
   - GPT Instruction Generation

NOTE YOU MUST PUT INPUT FILES IN THE /Autolab WORKING DIRECTORY

NOTE ALL JSON PATHS MUST REFER TO A PATH IN THE /Autolab
     WORKING DIRECTORY

Created: 07/06/2023

Usage:
- python3 pipeline.py
- Edit all parameters in the JSON file
- NOTE you must to delete the output files if you plan to rerun the pipeline with the same output directories

"""
from sst_transcription.googlestt import SpeechToText
from instruction_generator.gpt_transcript import TranscriptConversion


import json
import os
import ffmpeg
import sys
from dotenv import load_dotenv
import platform


def directoryPrecheck(input_json):
    """
    Verifies all directories described in the JSON for any pre-existing files (for write)
            and already existing files (for read) that would conflict with our program

    Args:
        input_json (json): read-in json file

    Return:
        status     (boolean): true if all pass, false if fail

    """

    # Load variables for stt and instruction generation
    stt_vars = input_json["transcription_variables"]
    instr_vars = input_json["instruction_variables"]
    vid_vars = input_json["video_conversion_variables"]

    # Checking input dirs exist
    # input_bool = (
    #     os.path.isfile(stt_vars["input_dir"])
    #     and os.path.isfile(instr_vars["input_dir"])
    #     and os.path.isfile(vid_vars["input_dir"])
    # )
    # output_bool = (
    #     os.path.isfile(stt_vars["output_dir"])
    #     and os.path.isfile(instr_vars["output_dir"])
    #     and os.path.isfile(vid_vars["output_dir"])
    # )
    # retrieve working directory
    cwd = os.getcwd()

    # Checking directory existance
    input_bool = os.path.isfile(cwd + vid_vars["input_path"])
    output_bool = os.path.isfile(cwd + stt_vars["output_path"]) or os.path.isfile(cwd + instr_vars["output_path"]) or os.path.isfile(cwd + vid_vars["output_path"])

    # Checks if input directories exist for reference/use
    if not input_bool:
        print("FAIL: One or more input files do not exists. Please check the input_path variables in the '{}' file.".format(input_json))
        return False

    # Checks if output directories don't exist for clean write
    if output_bool:
        print("FAIL: One or more of the export directories exists. Please check the output_path variables in the '{}' file.".format(input_json))
        return False

    print("PASS!")
    return True


if __name__ == "__main__":
    # major.minor.patch-pre_release_label
    print("Autolab v0.1.1-alpha")
    print("_" * 20 + "\n")

    # print ("Gcloud Authenticating...")
    # os.system('cmd /k "gcloud auth application-default login"')

    print("Reading JSON...")

    json_input = (
        "inputs_win.json" if platform.system() == "Windows" else "inputs_mac.json"
    )

    # all paths in the JSON assume we are in the autolab/ directory
    with open(json_input) as file:
        data = json.load(file)
        print("Success!\n")

    # directory precheck
    pf_check = directoryPrecheck(data)

    # if we fail precheck
    if not pf_check:
        sys.exit()

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
        ffmpeg.input(cwd + vid_vars["input_path"])
        .output(cwd + vid_vars["output_path"], acodec="flac")
        .run(quiet=True)
    }

    print("Success (1/3)\n")

    # 2) SpeechToText Transcription
    ###############################################
    print("Generating SpeechToText Transcription...")

    stt = SpeechToText(
        project_id=stt_vars["project_id"], recognizer_id=stt_vars["recognizer_id"]
    )

    with open(cwd + stt_vars["input_path"], "rb") as fd:
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
    with open(cwd + stt_vars["output_path"], "w") as file:
        file.write(format_transcript_time)
    # @TODO need to also store transcript_concat

    print("Success (2/3)\n")

    # 2) Instruction Generation
    ###############################################
    print("Generating Instructions...")

    transcription_path = cwd + instr_vars["input_path"]
    instr_path = cwd + instr_vars["output_path"]

    load_dotenv()
    secret_key = os.getenv("OPENAI_API_KEY")
    instr_generator = TranscriptConversion(
        model=instr_vars["model"], secret_key=secret_key
    )
    instr_set = instr_generator.generateInstructions(transcript_path=transcription_path)

    print("Done! Saving...")
    if instr_set != None:
        with open(instr_path, "w") as json_file:
            json.dump(instr_set, json_file, indent=2)
    else:
        print("Error: Instruction Set has not been generated")

    print("Success (3/3)\n")
    print("_" * 20 + "\n")
    print(f'Instructions saved to "%s"\nAutolab terminating' % instr_path)
