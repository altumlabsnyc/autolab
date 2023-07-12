# AutoLab API

![Version](https://img.shields.io/badge/version-0.1.1_alpha-blue)

AutoLab is a proprietary API developed by Altum Labs. It's designed to convert wet lab procedures into a procedural guide in an effortless and accurate way. It accepts a .mp4 file of a wet lab procedure and transforms it into a step-by-step guide.

**Please note that this software is not open source and cannot be used without the express permission of Altum Labs.**

## Features

- Transcription of audio from a wet lab .mp4 file using Google Speech.
- Generation of a step-by-step procedural guide from the transcription using GPT-4.

## Installation

This software is proprietary and its use is restricted. For installation details, please contact Altum Labs.

## Usage

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
Note that files must be deleted from the tmp/ directory before generate_procedure is called.


## Authors

- **Ricky Fok** - *Initial work* - [FoksWok](https://github.com/FoksWok)
- **Izzy Qian** - *Initial work* - [izzyaltum](https://github.com/izzyaltum)
- **Grant Rinehimer** - *Initial work* - [AtomicAudit](https://github.com/AtomicAudit)
