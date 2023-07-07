from dotenv import load_dotenv

import openai
import tiktoken
import os

class TranscriptConversion:
    """ Class to convert transcription into lab instructions
    """
    
    def __init__(self, model, secret_key):
        """ Constructor - sets up OpenAI API's settings

        Args:
            model      (_type_): OpenAI model type used for conversion 
            secret_key (_type_): API keys
        """ 
        self.secret_key = secret_key
        self.model = model
        self.instr_set = None
        self.transcript = None
        self.gpt_prompt = "The following transcript of a lab experiement has text with start and end times of when they were said in a video. Edit the transcript into a clean and concise lab procedure that would appear in a lab report. Then, assign each of the steps with timestamps that align with what is stated in the transcript"
        try:           
            self.encoding = tiktoken.get_encoding("cl100k_base")
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception as e:
            print("Error: Model or specified transcript location is invalid")
    
    def properReformat(self,raw_response):
        """
            reformat raw reponse into proper list

            Args:
                raw_response       (string): raw output from GPT model

            Return:
                formatted_response (string): reformatted output

        """

        lines = raw_response.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        formatted_lines = [f'{line}' for index, line in enumerate(lines)]
        formatted_string = '\n'.join(formatted_lines)

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
        num_tokens = len(self.encoding.encode(self.transcript))

        # set prompt
        self.gpt_prompt = self.gpt_prompt + self.transcript

        openai.api_key = self.secret_key
        raw_output = openai.Completion.create(
            model = self.model,
            prompt = self.gpt_prompt,
            temperature = 0.2, #in range (0,2), higher = more creative
            max_tokens=num_tokens,
        )

        raw_instr = raw_output.get('choices')[0].get('text')
        self.instr_set = self.properReformat(raw_instr)
        
        return self.instr_set



