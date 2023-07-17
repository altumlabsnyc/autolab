"""
autolab.py

This module provides a callable function for the entire Autolab pipeline process.

Created: 07/11/2023

"""
from .googlestt import SpeechToText
from .gpt_transcript import TranscriptConversion
from .vid_converter import VideoConverter
import os
import logging
from dotenv import load_dotenv


class Autolab:
    def __init__(self, project_id, recognizer_id, gpt_model, acodec: str = "flac"):
        """Constructor - sets logging format and the output_clean variable
                          This is used to keep track of the residual files
                          generated in the process to create our lab
                          instructions

        Args:
            None
        """
        load_dotenv()
        self.project_id = project_id
        self.recognizer_id = recognizer_id
        self.gpt_model = gpt_model
        self.acodec = acodec
        self._default_logging()
        self.output_clean = None

    def _default_logging(self):
        """
            Sets logging to our default logging format

        Args:
            None

        Return:
            None

        """
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def generate_procedure(self, uid: str, temp_dir: str, enable_logging=False) -> dict:
        """
        Generates a procedural script based on video input by converting the video to audio, transcribing the speech,
        and then using an instruction generator to convert the transcription into instructions.

        Parameters
        ----------
        uid : str
            A unique identifier for the video from the supabase bucket.
        temp_dir : str
            The path to the directory where temporary files will be stored during the process.
        enable_logging : bool, optional
            If True, logging is enabled. Default is False.

        Returns
        -------
        dict
            A dictionary containing the instructions generated from the transcription.

        Notes
        -----
        1. This function begins by converting a mp4 video file to .flac audio using a `VideoConverter` instance.
        2. The audio is then transcribed into text using a `SpeechToText` instance.
        3. The transcriptions are processed into a string, each transcript segment along with their start and end times.
        4. The transcript is saved in a .txt file.
        5. Finally, instructions are generated based on the saved transcript using a `TranscriptConversion` instance,
        and returned as a dictionary.

        @TODO
        ----
        More thorough implementation of `VideoConverter`.
        """
        logging.basicConfig(
            level=logging.INFO if enable_logging else logging.WARNING, force=True
        )
        # 1) Read and Convert mp4 File to .flac
        # @TODO finish more through implementation of VideoConverter
        ###############################################
        logging.info("Generating .flac file")
        vid_converter = VideoConverter(f"{temp_dir}/{uid}.mp4")
        vid_converter.generateAudio(f"{temp_dir}/{uid}.{self.acodec}", codec=self.acodec, quiet=True)
        logging.info("OK")
        ###############################################

        # 2) SpeechToText Transcription
        ###############################################
        logging.info("Generating SpeechToText transcription")
        stt = SpeechToText(project_id=self.project_id, recognizer_id=self.recognizer_id)

        # read in audio file previously generated
        with open(f"{temp_dir}/{uid}.flac", "rb") as fd:
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

        logging.info("OK. Saving transcript...")
        with open(f"{temp_dir}/{uid}.txt", "w") as file:
            file.write(format_transcript_time)

        logging.info("Saved")
        ###############################################

        # 3) Instruction Generation
        ###############################################
        logging.info("Instruction Generation - {}".format(self.gpt_model))
        logging.info("Generating lab instructions...")
        transcription_path = f"{temp_dir}/{uid}.txt"
        instr_path = f"{temp_dir}/{uid}_instr.txt"

        load_dotenv()
        secret_key = os.getenv("OPENAI_API_KEY")
        instr_generator = TranscriptConversion(
            model=self.gpt_model, secret_key=secret_key
        )

        instr_json = instr_generator.generateInstructions(
            transcript_path=transcription_path
        )

        logging.info("OK. Returning instructions")

        return instr_json
    
    def generate_procedure_v2(self, uid: str, temp_dir: str, video_path: str = None, enable_logging=False) -> dict:
        """
        Generates a procedural script based on video input by converting the video to audio, transcribing the speech,
        and then using an instruction generator to convert the transcription into instructions.

        v2 is a batch input implementation that handles longer videos (>60 seconds) by splitting them into
        60 second clips

        Parameters
        ----------
        uid : str
            A unique identifier for the video from the supabase bucket.
        temp_dir : str
            The path to the directory where temporary files will be stored during the process.
        video_path : str, optional
            The path to the video directory if specified. If not, we will use the temp_dir
        enable_logging : bool, optional
            If True, logging is enabled. Default is False.

        Returns
        -------
        dict
            A dictionary containing the instructions generated from the transcription.

        Notes
        -----
        1. This function begins by converting a mp4 video file to .flac audio using a `VideoConverter` instance.
        2. The audio is then transcribed into text using a `SpeechToText` instance.
        3. The transcriptions are processed into a string, each transcript segment along with their start and end times.
        4. The transcript is saved in a .txt file.
        5. Finally, instructions are generated based on the saved transcript using a `TranscriptConversion` instance,
        and returned as a dictionary.

        @TODO
        ----
        More thorough implementation of `VideoConverter`.
        """

        logging.basicConfig(
            level=logging.INFO if enable_logging else logging.WARNING, force=True
        )

        # 1) Read and Convert mp4 File to .flac
        ###############################################
        logging.info("Generating .flac file")
        if video_path == None:
            video_path = f"{temp_dir}/{uid}.mp4"

        vid_converter = VideoConverter(video_path)
        try:
            vid_converter.generateAudio(f"{temp_dir}/{uid}.{self.acodec}", codec=self.acodec, quiet=True)
        except Exception as e:
            logging.critical(f"vid_converter failed to generate. {e}")

        logging.info("OK")
        ###############################################

        # 2) SpeechToText Transcription
        ###############################################
        logging.info("Generating SpeechToText transcription")
        stt = SpeechToText(project_id=self.project_id, recognizer_id=self.recognizer_id)

        # read in audio file previously generated
        with open(f"{temp_dir}/{uid}.{self.acodec}", "rb") as fd:
            contents = fd.read()

        try:
            response = stt.speech_to_text(contents)
        except Exception as e:
            logging.critical(f"speech_to_text failed to execute. {e}")

        # transcript_concat = stt.concatenate_transcripts(response)
        transcript_time = stt.get_transcript_list_and_times(response)

        # convert transcript_time into string
        format_transcript_time = ""
        for item in transcript_time:
            text = item[0]
            start_time = item[1]
            end_time = item[2]
            format_transcript_time += f"{text} [{start_time}-{end_time}]\n"

        logging.info("OK. Saving transcript...")
        with open(f"{temp_dir}/{uid}.txt", "w") as file:
            file.write(format_transcript_time)

        logging.info("Saved")
        ###############################################

        # 3) Instruction Generation
        ###############################################
        logging.info("Instruction Generation - {}".format(self.gpt_model))
        logging.info("Generating lab instructions...")
        transcription_path = f"{temp_dir}/{uid}.txt"
        instr_path = f"{temp_dir}/{uid}_instr.txt"

        load_dotenv()
        secret_key = os.getenv("OPENAI_API_KEY")
        instr_generator = TranscriptConversion(
            model=self.gpt_model, secret_key=secret_key
        )

        instr_json = instr_generator.generateInstructions(
            transcript_path=transcription_path
        )

        logging.info("OK. Returning instructions")

        return instr_json