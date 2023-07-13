"""
json_gen.py

This module generates input JSON files based on the user's inputs
NOTE This JSON file is meant to be run by one of the following scripts:
        'autolab.py'
        'lambda_handler.py'

Created: 07/11/2023

Usage
- video_path must be located somewhere in the autolab/ working
  directory.
"""
import json
import os


class AL_JSON_Generator:
    def __init__(self, video_path, project_id, recognizer_id, gpt_model, acodec="flac"):
        """Constructor - takes

        Args:
            video_path    (string): path to the video input used in Autolab
            project_id    (string): project_id for GCP
            recognizer_id (string): recognizer_id for GCP SST v2
            gpt_model     (string): model utilized in GPT API call
            acodec        (string): audio codec wanted for output
        """
        with open("autolab_schema.json") as file:
            self.schema = json.load(file)

        if not os.path.isfile(os.getcwd + video_path):
            raise Exception(
                "Error: Cannot find video at the specified path: {}".format(
                    os.getcwd + video_path
                )
            )
        self.vid_input_path = video_path
        self.acodec = acodec
        self.project_id = project_id
        self.recognizer_id = recognizer_id
        self.gpt_model = gpt_model

        self.params = {
            "variables": {
                "vid_input_path": video_path,
                "vid_convert_path": "/temp/{video_path}_autolab_output/{video_path}.{self.acodec}",
                "transcript_path": "/temp/{video_path}_autolab_output/{video_path}_transcript_time.txt",
                "project_id": self.project_id,
                "recognizer_id": self.recognizer_id,
                "instr_path": "/temp/{video_path}_autolab_output/{video_path}_instruction_set.json",
                "model": self.gpt_model,
            }
        }

    def setPaths(self, vid_convert_path, transcript_path, instr_path):
        """
        Sets paths needed for JSON

        Args:
            vid_convert_path (string): input JSON's file path
            transcript_path  (string): transcript path
            instr_path       (string): lab instruction path
        Return:
            stt_params   (dict): SpeechToText parameters
            instr_params (dict): Instruction Generator parameters
            vid_params   (dict): Video conversion parameters

        """
        self.params["variables"]["vid_convert_path"] = vid_convert_path
        self.params["variables"]["transcript_path"] = transcript_path
        self.params["variables"]["instr_path"] = instr_path

    def retrieveJSON(self):
        return self.params
