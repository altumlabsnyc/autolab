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
import shutil
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
        self.instr_path = None

    def _default_logging(self):
        """
            Sets logging to out default logging format

        Args:
            None

        Return:
            None

        """
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.basicConfig(
            level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]')

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

        params = data["variables"]

        # Checking params paths
        if not os.path.isfile(cwd + params["vid_input_path"]):
            raise Exception(
                "Error: Cannot validate existence of variables[\"input_path\"]: {}".format(params["vid_input_path"]))
        
        if not os.path.exists(cwd + params["vid_convert_dir"]):
            raise Exception(
                "Error: variables[\"vid_convert_dir\"]: {} does not exists".format(params["vid_convert_dir"]))
        
        if os.path.isfile(cwd + params["transcript_path"]):
            raise Exception(
                "Error: variables[\"transcript_path\"]: {} already exists".format(params["transcript_path"]))

        if os.path.isfile(cwd + params["project_id"]):
            raise Exception(
                "Error: variables[\"project_id\"]: {} already exists".format(params["project_id"]))
        
        if os.path.isfile(cwd + params["recognizer_id"]):
            raise Exception(
                "Error: variables[\"recognizer_id\"]: {} already exists".format(params["recognizer_id"]))
        
        if os.path.isfile(cwd + params["instr_path"]):
            raise Exception(
                "Error: variables[\"instr_path\"]: {} already exists".format(params["instr_path"]))

        return params

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
            raise Exception(
                "Error: Cannot validate existence of JSON from the directory provided!")

        # read in json for input verification
        with open(input_json) as file:
            data = json.load(file)

        # read in json schema to verify json format
        with open('autolab_schema.json') as file:
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
            logging.disable(logging.CRITICAL)

        logging.info(
            "NOTICE: Logging has been set to: ENABLE\nAutolab v0.1.1-alpha")

        # Pre-Check
        self._precheck(json_input)
        logging.info("Precheck successful. Verifying JSON parameters...")
        params = self._json_params_verify(json_input)
        logging.info("JSON parameters are OK")

        # get working directory
        cwd = os.getcwd()

        # saves temporary directory path
        # TODO implement output_clan
        self.output_clean = cwd + params["vid_convert_dir"]
        self.instr_path = params["instr_path"]

        # 1) Read and Convert mp4 File to .flac
        # @TODO finish more through implementation of VideoConverter
        ###############################################
        logging.info("Generating .flac file(s)")
        vid_converter = VideoConverter(cwd + params["vid_input_path"])
        try:
            vid_converter.split_and_convert(
                cwd + params["vid_convert_dir"], codec="flac", quiet=True)
        except:
            print("ERROR: Autolab.py Step 1")
            # self.clean_outputs()
        logging.info("OK")
        ###############################################

        # 2) SpeechToText Transcription
        ###############################################
        logging.info("Generating SpeechToText transcription")
        stt = SpeechToText(
            project_id=params["project_id"], recognizer_id=params["recognizer_id"]
        )

        
        # TODO this will fill up memory if transcript is super long
        # Need to fix (output to temporary file and then read back in?)
        responses = []

        for filename in os.listdir(cwd + params["vid_convert_dir"]):
            filepath = cwd + params["vid_convert_dir"] + "/" + filename
            if os.path.splitext(filename)[1] == '.flac':
                # read in audio file previously generated
                print(filepath)
                with open(filepath, "rb") as fd:
                    tmp_response = fd.read()
                responses.append(stt.speech_to_text(tmp_response))
        
        # TODO this will fill up memory if transcript is super long
        # Need to fix (output to temporary file and then read back in?)
        # TODO also lazy code here. also needs a fix

        format_transcript_time = ""
        transcript_time = ""

        for response in responses:
            try:
                # transcript_concat = stt.concatenate_transcripts(response)
                transcript_time = stt.get_transcript_list_and_times(response)
            except:
                print("ERROR: Autolab.py Step 2")
                # self.clean_outputs()

            # convert transcript_time into string
            format_transcript_time = ""
            for item in transcript_time:
                text = item[0]
                start_time = item[1]
                end_time = item[2]
                format_transcript_time += f"{text} [{start_time}-{end_time}]\n"

        logging.info("OK. Saving transcript...")
        with open(cwd + params["transcript_path"], "w") as file:
            file.write(format_transcript_time)
        # @TODO need to also store transcript_concat

        logging.info("Saved")
        ###############################################

        # 3) Instruction Generation
        ###############################################
        logging.info("Instruction Generation - {}".format(params["model"]))
        logging.info("Generating lab instructions...")
        transcription_path = cwd + params["transcript_path"]
        instr_path = cwd + params["instr_path"]

        load_dotenv()
        secret_key = os.getenv("OPENAI_API_KEY")
        instr_generator = TranscriptConversion(
            model=params["model"], secret_key=secret_key
        )

        
        # get lab instruction's json
        try:
            instr_json, raw = instr_generator.generateInstructions(
                transcript_path=transcription_path)
            print(raw)
        

            logging.info("OK. Saving...")

            with open(instr_path, "w") as json_file:
                json.dump(instr_json, json_file, indent=2)
        except:
            print("ERROR: Autolab.py Step 3")
            # self.clean_outputs()

        logging.info("Saved")

        # # cleanup if specified by the user
        # if cleanup:
        #     self.clean_outputs()

        logging.info("Autolab complete: File saved at {}".format(instr_path))

        # reset logging
        if not enable_logging:
            self._default_logging()

    # TODO needs to be implemented for multi file 
    # I've commented it out for now
    # NOTE this means you need to delete the output files before
    # running again
    def clean_outputs(self):
        """
            Removes any residual files that are generated to make our instruction file
        Args:
            None

        Return:
            None

        """
        

        # if self.output_clean != None:
        #     for file in self.output_clean:
        #         if os.path.isfile(file):
        #             os.remove(file)
            
