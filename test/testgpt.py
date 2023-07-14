from testgptscript import TranscriptConversion
import os
import json
from dotenv import load_dotenv


def instruction_gen_test():
    cwd = os.getcwd()
    # print(cwd)

    # set input and output directories (input dir must exist before running)
    input_dir = f"{cwd}/test/testinput.txt"
    output_dir = f"{cwd}/test/testoutput.json"

    # Loading API Key
    load_dotenv()
    secret_key = os.getenv("OPENAI_API_KEY")

    # generate instructions
    print("Generating Instruction Set...")
    instr_generator = TranscriptConversion(model="gpt-4", secret_key=secret_key)
    instr_set = instr_generator.generateInstructions(transcript_path=input_dir)
    print("Done!\n")

    # print results
    print("Results:")
    print(instr_set)
    print("\n")

    # saves results
    print("Saving Results...")
    if instr_set != None:
        with open(output_dir, "w") as file:
            # file.write(instr_set)
            json.dump(instr_set, file)
        print(f'Saved to "%s"' % output_dir)
    else:
        print("Error: Instruction Set has not been generated")


if __name__ == "__main__":
    instruction_gen_test()
