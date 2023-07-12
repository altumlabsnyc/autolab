"""
gpt_transcript.py

This module contains the class that utilizes the OpenAI's GPT API call to
generate our lab instructions

Created: 07/06/2023

"""

from dotenv import load_dotenv
import openai
import tiktoken
import re
import json
from datetime import date
import re


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

        self.gpt_prompt = """The following is a timestamped transcript of a lab. Edit it into a clean and concise procedure instruction that would appear in a lab report. Include "Summary" concisely stating the lab's goals, separate with "Procedure", start with "-" for each step, and indicate which timestamp the step was from in "()". Transcript: """

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
        formatted_lines = [f"{line}" for line in lines]
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
        try:
            summary, procedure_string = raw_response.split("Procedure:")
        except Exception as e:
            print(f"Error: Cannot split summary and procedure. {e}")
            return None
        summary_content = summary.replace("Summary:", "").strip()
        steps = procedure_string.split("\n-")

        procedure = []
        for step in steps:
            # Izzy trying new format that doesn't use timestamps
            pattern = r"^(.*?) \((.*?)\-(.*?)\)$"
            match = re.match(pattern, step)
            if match:
                content = match.group(1).strip()
                start_time = match.group(2).strip()
                end_time = match.group(3).strip()

                step_obj = {
                    "step": content,
                    "start_time": start_time,
                    "end_time": end_time,
                }
                procedure.append(step_obj)
            else:
                print(f"Error: Cannot parse step {step}")

        metadata = {
            "version": "Autolab 0.1.1-alpha",
            "author": "Altum Labs",
            "date-generated": date.today().strftime("%Y-%m-%d"),
            "description": "These generated results are a product of Autolab by Altum Labs. It contains private data and is not for distribution. Unauthorized use of this data for any other purposes is strictly prohibited. ",
        }

        instr_json = {
            "metadata": metadata,
            "summary": summary_content,
            "procedure": procedure,
        }
        return instr_json
    
    # NOTE 
    def genInstrv2(self, transcript_path, encoding="cl100k_base"):
        """
        Generates Instruction set by applying the model on the
        transcript.

            Args:
                transcript_path      (_type_): location of transcript
                encoding - optional (string): tiktoken encoder base 

            Return:
                instr_set      (json): formatted JSON instruction set
                raw_str       (string): raw string output from GPT model
        """

        # read in transcript txt file
        with open(transcript_path, "r") as file:
            self.transcript = file.read()

        # gpt_prompt = """The following is a timestamped transcript of a lab. Edit it into a clean and concise procedure instruction that would appear in a lab report. Include "Summary" concisely stating the lab's goals, and format all of it as a JSON with start and end times as different entries. Transcript: """
        openai.api_key = self.secret_key
        # count tokens to figure out a good max_tokens value
        encoding = tiktoken.get_encoding(encoding)
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = 4097 - len(encoding.encode(self.gpt_prompt + self.transcript))

        # Call GPT4
        raw_output = None
        raw_instr = None

        msg = [
                {"role": "system", "content": self.gpt_prompt},
                {"role": "user", "content": self.transcript},
            ]
        raw_output = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=msg,
            temperature=0.2,  # in range (0,2), higher = more creative
            # chatcompletion doesn't need max_tokens parameter
        )
        raw_instr = raw_output.get("choices")[0].get("message").get("content")
        data = json.loads(raw_instr)
        summary = data["Summary"]
        procedure = data["Procedure"]

        metadata = {
            "version": "Autolab 0.1.1-alpha",
            "author": "Altum Labs",
            "date-generated": date.today().strftime("%Y-%m-%d"),
            "description": "These generated results are a product of Autolab by Altum Labs. It contains private data and is not for distribution. Unauthorized use of this data for any other purposes is strictly prohibited. ",
        }

        instr_json = {
            "metadata": metadata,
            "summary": summary,
            "procedure": procedure,
        }
        return instr_json

        print(raw_instr)
    
    def generateInstructions(self, transcript_path, encoding="cl100k_base"):
        """
        apply model onto transcript

            Args:
                transcript_path      (_type_): location of transcript
                encoding - optional (string): tiktoken encoder base 

            Return:
                instr_set      (json): formatted JSON instruction set
                raw_str       (string): raw string output from GPT model
        """

        # read in transcript txt file
        with open(transcript_path, "r") as file:
            self.transcript = file.read()

        # set prompt
        full_prompt = self.gpt_prompt + self.transcript

        openai.api_key = self.secret_key
        # count tokens to figure out a good max_tokens value
        encoding = tiktoken.get_encoding(encoding)
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = 4097 - len(encoding.encode(full_prompt))

        # Call one of the GPT models
        raw_output = None
        raw_instr = None
        if self.model == "gpt-4" or "gpt-3.5-turbo":
            msg = [
                {"role": "system", "content": self.gpt_prompt},
                {"role": "user", "content": self.transcript},
            ]
            raw_output = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=msg,
                temperature=0.2,  # in range (0,2), higher = more creative
                # chatcompletion doesn't need max_tokens parameter
            )
            raw_instr = raw_output.get("choices")[0].get("message").get("content")
        elif self.model == "text-davinci-003":
            raw_output = openai.Completion.create(
                model=self.model,
                prompt=full_prompt,
                temperature=0,  # in range (0,2), higher = more creative
                max_tokens=num_tokens,
            )
            raw_instr = raw_output.get("choices")[0].get("text")
        else:
            print(f"Error: Invalid model specified - {self.model}")
            return None

        print(raw_output)
        stop_reason = raw_output.get("choices")[0].get("finish_reason")
        if stop_reason != "stop":
            print(f"Error: GPT was stopped early because of {stop_reason}")
            return None

        # old string format
        # self.instr_set = self.properReformat(raw_instr)
        self.instr_set = self.generateJSON(raw_instr)
        return self.instr_set, raw_instr
