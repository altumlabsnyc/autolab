from dotenv import load_dotenv

import openai
import tiktoken
import os


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
        self.gpt_prompt = """The following is a snippet of transcript of a lab experiment that was recorded and timestamped. 
        Edit it into a clean and concise procedure that is part of a lab report. 
        Assign each of the steps with the input timestamps."""
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception as e:
            print("Error: Model or specified transcript location is invalid")

    def properReformat(self, raw_response):
        """
        reformat raw reponse into proper list

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

    def generateInstructions(self, transcript_dir):
        """
        apply model onto transcript

        Args:
            transcript_dir (_type_): location of transcript

        Return:
            instr_set      (string): formatted instruction set
        """

        # read in transcript txt file
        with open(transcript_dir, "r") as file:
            self.transcript = file.read()
        num_tokens = len(self.encoding.encode(self.gpt_prompt + self.transcript))
        # max gpt prompt tokens is 4096. Call the api more times if source transcript is longer than 4096 tokens
        if num_tokens > 4096:
            num_tokens = 4096
            print("Error: File too large for GPT-3 to process")
            exit()

        # set prompt
        self.gpt_prompt = self.gpt_prompt + self.transcript

        openai.api_key = self.secret_key
        raw_output = openai.Completion.create(
            model=self.model,
            prompt=self.gpt_prompt,
            temperature=0.2,  # in range (0,2), higher = more creative
            max_tokens=num_tokens,
        )

        raw_instr = raw_output.get("choices")[0].get("text")
        self.instr_set = self.properReformat(raw_instr)

        return self.instr_set
