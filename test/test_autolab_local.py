"""
test_autolab_local.py

This module runs a local test of Autolab

Created: 07/17/2023

"""

from autolab.autolab import *
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import shutil

def single_file_test():
    """
    Runs Autolab with a 60 second video in our data directory 
    (data/welab1_60seconds/output1.mp4)

    """

    # Set variables
    load_dotenv()
    project_id: str = os.getenv("PROJECT_ID")
    recognizer_id: str = os.getenv("RECOGNIZER_ID")
    tmp_dir: str = os.getenv("TMP_DIR")
    gpt_model: str = "gpt-4"

    
    # Testing video paths
    cwd = os.getcwd()
    relative_mp4_path = "/data/wetlab1_60seconds/output1.mp4"
    mp4_path = cwd + relative_mp4_path
    uid = "test_vid"
    
    # Step 1: Make temp directory
    os.makedirs(tmp_dir)
    
    # Step 2: Run Autolab
    lab = Autolab(project_id, recognizer_id, gpt_model)
    try:
        procedure = lab.generate_procedure_v2(uid, tmp_dir, mp4_path, enable_logging=True)
    except Exception as e:
        print(f"Error! Autolab procedure generation unsuccessful. {e}")

    # Observe before delete
    print(procedure)
    
    while True:
        user_input = input("\n\nAutolab test Finished. Observe residual files generated before deletion. Save instructions? (y/n)")
        if user_input == "y":
            try:
                with open(cwd + "/test/autolab_output.json", "w") as f:
                    # indent here is for easier viewing. It should not be used in practice
                    json.dump(procedure, f, indent = 2)
                print(f"Saved to /test/autolab_output.json")
            except:
                print("Error! Cannot Save JSON")
        shutil.rmtree(tmp_dir)
        break

def multi_file_test():
    """
    Runs Autolab with a 2 minute video in our data directory 
    (data/welab1_60seconds/output1.mp4)

    """

    # Set variables
    load_dotenv()
    project_id: str = os.getenv("PROJECT_ID")
    recognizer_id: str = os.getenv("RECOGNIZER_ID")
    tmp_dir: str = os.getenv("TMP_DIR")
    gpt_model: str = "gpt-4"
    
    # Testing video paths
    cwd = os.getcwd()
    relative_mp4_path = "/data/wetlab1/wetlab1_2min.mp4"
    mp4_path = cwd + relative_mp4_path
    uid = "test_batch_vid"

     # Step 1: Make temp directory
    os.makedirs(tmp_dir)
    
    # Step 2: Run Autolab
    lab = Autolab(project_id, recognizer_id, gpt_model)
    try:
        procedure = lab.generate_procedure_batch(uid, tmp_dir, mp4_path, enable_logging=True)
    except Exception as e:
        print(f"Error! Autolab procedure generation unsuccessful. {e}\n{e.with_traceback}")

    # Observe before delete
    print(procedure)
    
    while True:
        user_input = input("\n\nAutolab test Finished. Observe residual files generated before deletion. Save instructions? (y/n)")
        if user_input == "y":
            try:
                with open(cwd + "/test/autolab_output.json", "w") as f:
                    # indent here is for easier viewing. It should not be used in practice
                    json.dump(procedure, f, indent = 2)
                print(f"Saved to /test/autolab_output.json")
            except:
                print("Error! Cannot Save JSON")
        shutil.rmtree(tmp_dir)
        break

if __name__ == "__main__":
    # To test Autolab on a single, 60 second video
    # single_file_test()
    
    # To test Autolab on longer video
    multi_file_test()
    
        
            
    
    