"""
autolab.py

This module provides a callable function for the entire Autolab pipeline process
NOTE ALL JSON PATHS MUST REFER TO A PATH IN THE /Autolab
     WORKING DIRECTORY

Created: 07/11/2023

"""
from sst_transcription.googlestt import SpeechToText
from instruction_generator.gpt_transcript import TranscriptConversion
from video_conversion.vid_converter import VideoConverter

import json
import os
import sys
import logging
import platform
import jsonschema
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from dotenv import load_dotenv


class Autolab:

    def __init__(self):
        """ Constructor - sets logging format and the output_clean variable
                          This is used to keep track of the residual files
                          generated in the process to create our lab
                          instructions

        Args:
            None
        """
        self._default_logging()
        self.output_clean = None

    def _default_logging(self):
        """
            Sets logging to out default logging format

        Args:
            None

        Return:
            None

        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]')

    def _json_params_verify(self, input_json):
        """
                Verifies and returns all the directories labeled in the JSON file

                Args:
                    input_json (string): input JSON's file path

                Return:
                    stt_params   (dict): SpeechToText parameters
                    instr_params (dict): Instruction Generator parameters
                    vid_params   (dict): Video conversion parameters

        """
        with open(input_json) as file:
            data = json.load(file)
        cwd = os.getcwd()

        vid_params = data["video_conversion_variables"]
        stt_params  = data["transcription_variables"]
        instr_params = data["instruction_variables"]
        
        # Checking vid_params paths
        if not os.path.isfile(cwd + vid_params["input_path"]):
            raise Exception(
                "Error: Cannot validate existence of video_conversion_variables[\"input_path\"]: {}".format(vid_params["input_path"]))
        if os.path.isfile(cwd + vid_params["output_path"]):
            raise Exception(
                "Error: video_conversion_variables[\"output_path\"]: {} already exists".format(vid_params["output_path"]))
        
        # Checking stt_params paths

        # if vid_params output equals stt_params input path then no need to verify
        if stt_params["input_path"] != vid_params["output_path"]:
            if not os.path.isfile(cwd + stt_params["input_path"]):
                raise Exception(
                    "Error: Cannot validate existence of transcription[\"input_path\" {}".format(stt_params["input_path"]))
        if os.path.isfile(cwd + stt_params["output_path"]):
            raise Exception(
                "Error: transcription[\"output_path\" {} already exists".format(stt_params["output_path"]))
        
        # Checking instr_params paths
        
        # if stt_params output equals instr_params input path then no need to verify
        if stt_params["output_path"] != instr_params["input_path"]:
            if not os.path.isfile(cwd + instr_params["input_path"]):
                raise Exception(
                    "Error: Cannot validate existence of instruction[\"input_path\" {}".format(instr_params["input_path"]))
        if os.path.isfile(cwd + instr_params["output_path"]):
            raise Exception(
                "Error: instruction[\"output_path\" {} already exists".format(instr_params["output_path"]))

        return vid_params, stt_params, instr_params

    def _precheck(self, input_json):
        """
                Verifies gcloud auth and json + all path existance

                Args:
                    input_json (string): input JSON's file path

                Return:
                    None

        """

        # GCP authentication 
        if self.check_gcloud_authentication() is False:
            raise Exception("Error: Google Cloud authentication failed!")
        else:
            logging.info("Gcloud auth. successful.")
        
        # JSON existence validation
        if not os.path.isfile(input_json):
            raise Exception("Error: Cannot validate existence of JSON from the directory provided!")

        # read in json for input verification
        with open(input_json) as file:
            data = json.load(file)

        # read in json schema to verify json format
        with open('data/autolab_schema.json') as file:
            schema = json.load(file)

        # Schema validation
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as e:
            raise Exception("Error: Invalid JSON data: {}.format(e)")

    # @TODO this does not seem to work. Gave a false True
    def check_gcloud_authentication(self):
        """
        Checks if the environment is authenticated with Google Cloud (gcloud).

        Returns:
            bool: True if authenticated, False otherwise.
        """
        try:
            # Attempt to get the default credentials
            creds, _ = default()

            # If credentials exist, return True
            if creds is not None:
                return True

        except DefaultCredentialsError:
            pass

        return False

    def generate_procedure(self, json_input, cleanup=True, enable_logging=False):
        """
            Run Autolab pipeline and output instruction set

        Args:
            json_input     (string): json path directory
            cleanup        (bool): dictates whether residual files should be deleted
                                    True: delete all files except for instruction set
                                    False: leaves saved files in their specified file path
            enable_logging (bool): dictates logging
                                        True: logging enabled

        Return:
            instr_json      (dict): JSON of the instructions

        """

        # Enable or diable logging
        if not enable_logging:
            logging.info("NOTICE: Logging has been set to: DISABLE")
            logging.disable(logging.CRITICAL)


        logging.info("NOTICE: Logging has been set to: ENABLE\nAutolab v0.1.1-alpha")

        # Pre-Check
        self._precheck(json_input)
        logging.info("Precheck successful. Verifying JSON parameters...")
        vid_params, stt_params, instr_params = self._json_params_verify(json_input)
        logging.info("JSON parameters are OK")
        
        # get working directory
        cwd = os.getcwd()
        print(cwd)
        
        # retrieve output path strings
        self.output_clean = []
        self.output_clean.append(cwd + vid_params["output_path"])
        self.output_clean.append(cwd + stt_params["output_path"])
        
        # 1) Read and Convert mp4 File to .flac
        # @TODO finish more through implementation of VideoConverter
        ###############################################
        logging.info("Generating .flac file")
        vid_converter = VideoConverter(cwd + vid_params["input_path"])
        try:
            vid_converter.generateAudio(cwd + vid_params["output_path"], codec="flac", quiet=True)
        except:
            self.clean_outputs()
        logging.info("OK")
        ###############################################



        # 2) SpeechToText Transcription
        ###############################################
        logging.info("Generating SpeechToText transcription")
        stt = SpeechToText(
            project_id=stt_params["project_id"], recognizer_id=stt_params["recognizer_id"]
        )

        # read in .flac file
        with open(cwd + stt_params["input_path"], "rb") as fd:
            contents = fd.read()
        response = stt.speech_to_text(contents)

        try:
            transcript_concat = stt.concatenate_transcripts(response)
            transcript_time = stt.get_transcript_list_and_times(response)
        except:
            self.clean_outputs()

        # convert transcript_time into string
        format_transcript_time = ""
        for item in transcript_time:
            text = item[0]
            start_time = item[1]
            end_time = item[2]
            format_transcript_time += f"{text} [{start_time}-{end_time}]\n"
        
        logging.info("OK. Saving transcript...")
        with open(cwd + stt_params["output_path"], "w") as file:
            file.write(format_transcript_time)
        # @TODO need to also store transcript_concat

        logging.info("Saved")
        ###############################################



        # 3) Instruction Generation
        ###############################################
        logging.info("Instruction Generation - {}".format(instr_params["model"]))
        logging.info("Generating lab instructions...")
        transcription_path = cwd + instr_params["input_path"]
        instr_path = cwd + instr_params["output_path"]

        load_dotenv()
        secret_key = os.getenv("OPENAI_API_KEY")
        instr_generator = TranscriptConversion(
            model=instr_params["model"], secret_key=secret_key
        )

        # get lab instruction's json
        try:
            instr_json = instr_generator.generateInstructions(transcript_path=transcription_path)
        except:
            self.clean_outputs()
            
        logging.info("OK. Saving...")

        with open(instr_path, "w") as json_file:
            json.dump(instr_json, json_file, indent=2)

        logging.info("Saved")

        # cleanup if specified by the user
        if cleanup:
            self.clean_outputs()

        logging.info("Autolab complete: File saved at {}".format(instr_path))

        # reset logging 
        if not enable_logging:
            self._default_logging()
        
        return instr_json

    def clean_outputs(self):
        """
            Removes any residual files that are generated to make our instruction file
        Args:
            None

        Return:
            None

        """

        if self.output_clean != None:
            if os.path.isfile(self.output_clean[0]):
                os.remove(self.output_clean[0])
            if os.path.isfile(self.output_clean[1]):
                os.remove(self.output_clean[1])