from gpt_transcript import TranscriptConversion
import os
import platform
from dotenv import load_dotenv

if __name__ == "__main__":
    cwd = os.getcwd()

    # set input and output directories (input dir must exist before running)
    system = platform.system()
    sep = None
    if system == "Darwin":  # mac
        sep = "/"
    elif system == "Windows":  # windows
        sep = "\\"
    else:
        sep = "/"
    input_dir = f"{cwd}{sep}data{sep}transcript_time.txt"
    output_dir = f"{cwd}{sep}data{sep}outputs{sep}instruction_set.txt"

    # Loading API Key
    load_dotenv()
    secret_key = os.getenv("OPENAI_API_KEY")

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
        with open(output_dir, "w") as file:
            file.write(instr_set)
        print(f'Saved to "%s"' % output_dir)
    else:
        print("Error: Instruction Set has not been generated")
