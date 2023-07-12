# AutoLab API

![Version](https://img.shields.io/badge/version-0.1.1_alpha-blue)

AutoLab is a proprietary API developed by Altum Labs. It's designed to convert wet lab procedures into a procedural guide in an effortless and accurate way. It accepts a .mp4 file of a wet lab procedure and transforms it into a step-by-step guide.

**Please note that this software is not open source and cannot be used without the express permission of Altum Labs.**

## Features

- Transcription of audio from a wet lab .mp4 file using Google Speech.
- Generation of a step-by-step procedural guide from the transcription using GPT-4.

## Installation

This software is proprietary and its use is restricted. For installation details, please contact Altum Labs. To set up the system, cd into the autolab directory and install the packages with pip or conda:

```bash
pip install -r requirements.txt
```

or with conda:

```bash
conda install --file requirements.txt
```

### Setting up Google Cloud authentication

You will need to set up the Google Cloud authentication in config.json.

### Troubleshooting:

If the Python version isn't compatible, try running installing Python 3.10:

```bash
conda install python=3.10
```

(Not recommended) If the installation fails, try overriding the dependencies:

```bash
pip install -nodeps requirements.txt
```

As a last resort, you can try to manually install each package by searching their respective installation instructions.

## Important Directories

stt_transcriptions - Contains the scripts used to transcribe mp4 or mp3 files using the Google Cloud Speech To Text (STT) v2 API.  
instruction_generator - Contains the scripts used to convert STT transcriptions into a clean lab procedure using GPT-4.

## Running the tests

TODO:
You can create your own tests by running the following Python script. You will need to specify a video destination in config.json.
Note that files must be deleted from the tmp/ directory before generate_procedure is called.

```python
from autolab import AutoLab

# Initialize autolab
lab = AutoLab()

# Transcribe a video and generate a procedure
# Use schema in data/autolab_schema.json
procedure = lab.generate_procedure('config.json')

# Returns a json containing the procedure
print(procedure)

```

## Built with

- FFMPEG - used to convert mp4 files to mp3 files and segment them into 60-second clips
- Google Cloud Speech to Text v2 API - used to transcribe mp3 files
- GPT-4 - used to generate a clean lab procedure from the transcription

## Authors

- **Ricky Fok** - _Initial work_ - [FoksWok](https://github.com/FoksWok)
- **Izzy Qian** - _Initial work_ - [izzyaltum](https://github.com/izzyaltum)
- **Grant Rinehimer** - _Initial work_ - [AtomicAudit](https://github.com/AtomicAudit)
