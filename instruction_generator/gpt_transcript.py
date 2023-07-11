"""
gpt_transcript.py

This module contains the class that utilizes the OpenAI's GPT API call to
generate our lab instructions

Created: 07/06/2023

"""

from dotenv import load_dotenv

import openai
import tiktoken
import os
import re

from datetime import date


class TranscriptConversion:
    """Class to convert transcription into lab instructions"""

    def __init__(self, model, secret_key):
        """Constructor - sets up OpenAI API's settings

        Args:
            model      (_type_): OpenAI model type used for conversion
            secret_key (_type_): API keys
        """
        self.secret_key = secret_key
        self.model = model
        self.instr_set = None
        self.transcript = None

        # @TODO Need to generate proper json for Izzy's prompt/ discuss 
        # self.gpt_prompt = """The following is a snippet of transcript of a lab experiment that was recorded and timestamped. 
        #                         Edit it into a clean and concise procedure that is part of a lab report. 
        #                         Assign each of the steps with the input timestamps. """
        
        self.gpt_prompt = """The following transcript of a lab experiement has text with start and end times of when they were said in 
                        a video. Edit the transcript into a clean and concise lab procedure that would appear in a lab report that contains 
                        the start and end times in each of the bullet points. Do not include any other text other than the steps. Before 
                        making this list, generate a short and concise summary of what we are achieving in this lab. With all those in 
                        mind, here is the transcript: """

        try:           
            self.encoding = tiktoken.get_encoding("cl100k_base")
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception as e:
            print("Error: Model or specified transcript location is invalid")
    
    def properReformat(self, raw_response):
        """
            Reformat raw reponse into proper string. 

        Args:
            raw_response       (string): raw output from GPT model

        Return:
            formatted_response (string): reformatted output

        """

        lines = raw_response.split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        formatted_lines = [f"{line}" for index, line in enumerate(lines)]
        formatted_string = "\n".join(formatted_lines)

        return formatted_string
    
    def generateJSON(self, raw_response):
        """
            Generates JSON file of lab instruction set

            Args:
                raw_response (string): raw output from GPT model

            Return:
                instr_json   (json): reformatted, JSON output

        """
        raw_response = raw_response.strip()
        summary, procedure_string = raw_response.split("\n\nProcedure")
        summary_content = summary.replace("Summary:", "").strip()
        steps = procedure_string.split("\n- ")

        procedure = []
        for step in steps:
            pattern = r"^(.*?) \((.*?)\-(.*?)\)$"
            match = re.match(pattern, step)
            if match:
                content = match.group(1).strip()
                start_time = match.group(2).strip()
                end_time = match.group(3).strip()

                step_obj = {
                    "step": content,
                    "start_time": start_time,
                    "end_time": end_time
                }
                procedure.append(step_obj)

        metadata = {
            "version": "Autolab 0.1.1-alpha",
            "author": "Altum Labs",
            "date-generated": date.today().strftime("%Y-%m-%d"),
            "description": "These generated results are a product of Autolab by Altum Labs. It contains private data and is not for distribution. Unauthorized use of this data for any other purposes is strictly prohibited. ",
        }

        instr_json = {
            "metadata": metadata,
            "summary": summary_content,
            "procedure": procedure
        }
        return instr_json
    
    def generateInstructions(self, transcript_path, encoding="cl100k_base"):
        """
        apply model onto transcript

            Args:
                transcript_path      (_type_): location of transcript
                encoding - optional (string): tiktoken encoder base 

            Return:
                instr_set      (json): formatted JSON instruction set
        """

        # read in transcript txt file
        with open(transcript_path, "r") as file:
            self.transcript = file.read()

        # set prompt
        full_prompt = self.gpt_prompt + self.transcript

        num_tokens = len(self.encoding.encode(full_prompt))
        # max gpt prompt tokens is 4096. Call the api more times if source transcript is longer than 4096 tokens
        if num_tokens > 4096:
            print("WARNING: Max GPT API prompt tokens is 4096. @TODO This needs to be handled")
            num_tokens = 4096
            print("Error: File too large for GPT-3 to process")
            exit()

        

        openai.api_key = self.secret_key
        #count tokens to figure out a good max_tokens value
        encoding = tiktoken.get_encoding(encoding)
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = len(encoding.encode(self.transcript))

        raw_output = openai.Completion.create(
            model=self.model,
            prompt=full_prompt,
            temperature=0.2,  # in range (0,2), higher = more creative
            max_tokens=num_tokens,
        )

        raw_instr = raw_output.get('choices')[0].get('text')
        # print("HERE!")
        # print(raw_instr)

        # old string format
        # self.instr_set = self.properReformat(raw_instr)
        self.instr_set = self.generateJSON(raw_instr)
        return self.instr_set
