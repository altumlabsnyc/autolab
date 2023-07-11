from gpt_transcript import TranscriptConversion
import os
import sys
import json
import platform
from dotenv import load_dotenv

if __name__ == "__main__":
    cwd = os.getcwd()
    
    # set input and output directories (input dir must exist before running)
    # TODO need to remove. Darwin/Mac format works for Windows
    #  system = platform.system()
    # sep = None
    # if system == "Darwin":  # mac
    #     sep = "/"
    # elif system == "Windows":  # windows
    #     sep = "\\"
    # else:
    #     sep = "/"
    input_dir = f"{cwd}/instruction_generator/data/gpt_test_transcript_time.txt"
    output_dir = f"{cwd}/instruction_generator/data/outputs/instruction_set.json"

    # Checking input dir exist
    if not os.path.isfile(input_dir):
        print(f"Input File '{input_dir}' does not exists. Program cannot proceed. Goodbye.")
        sys.exit()

    # Checking output dir not exist
    if os.path.isfile(output_dir):
        print(f"File '{output_dir}' exists.")
        response = input("Do you want to overwrite this file? (y/n): ")

        if response.lower() == "y":
            os.remove(output_dir)
            print("File deleted.")
        else:
            print("File not deleted. Program cannot proceed. Goodbye.")
            sys.exit()

    # Loading API Key
    try:
        load_dotenv()
        secret_key = os.getenv('OPENAI_API_KEY')

        # Rest of your code using the secret_key

    except Exception as e:
        print(f"Error occurred while loading the API key: {e}")

    # generate instructions
    print("Generating Instruction Set...")
    instr_generator = TranscriptConversion(
        model="text-davinci-003", secret_key=secret_key
    )
    instr_set = instr_generator.generateInstructions(transcript_dir=input_dir)
    print("Done!\n")

    # print results
    print("Results:")
    print(instr_set)
    print("\n")

    # saves results
    print("Saving Results...")
    if instr_set != None:
        with open(output_dir, "w") as json_file:
            json.dump(instr_set, json_file, indent=2)
        print(f'Saved to \"%s\"' % output_dir)
    else:
        print("Error: Cannot save JSON!")

