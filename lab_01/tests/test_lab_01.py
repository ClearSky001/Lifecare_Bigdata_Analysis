import os
import subprocess
import pytest


def test_find_file_duplicates_1_score_25():
    script_path = "./lab_01_file_duplication_detector.sh"
    test_dir = "tests/test_1"
    
    # Run the Bash script on the test directory
    result = subprocess.run([script_path, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Expected output: The duplicate file should be identified
    output_files = result.stdout.strip().split("\n")
    
    assert len(output_files) == 3, "Duplication file count not match"
    assert any([x.endswith("image007.jpg") for x in output_files])
    assert any([x.endswith("image012.jpg") for x in output_files])
    assert any([x.endswith("image014.jpg") for x in output_files])

def test_find_file_duplicates_2_score_25():
    script_path = "./lab_01_file_duplication_detector.sh"
    test_dir = "tests/test_2"
    
    # Run the Bash script on the test directory
    result = subprocess.run([script_path, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Expected output: The duplicate file should be identified
    output_files = result.stdout.strip().split("\n")

    assert len(output_files) == 2, "Duplication file count not match"
    assert any([x.endswith("image001.jpg") for x in output_files])
    assert any([x.endswith("image003.jpg") for x in output_files])

def test_find_file_duplicates_3_score_25():
    script_path = "./lab_01_file_duplication_detector.sh"
    test_dir = "tests/test_3"
    
    # Run the Bash script on the test directory
    result = subprocess.run([script_path, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Expected output: The duplicate file should be identified
    output_files = result.stdout.strip().split("\n")
    
    assert len(output_files) == 2, "Duplication file count not match"
    assert any([x.endswith("image019.jpg") for x in output_files])
    assert any([x.endswith("image020.jpg") for x in output_files])


def test_find_file_duplicates_4_score_25():
    script_path = "./lab_01_file_duplication_detector.sh"
    test_dir = "tests/test_4"
    
    # Run the Bash script on the test directory
    result = subprocess.run([script_path, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Expected output: The duplicate file should be identified
    output_files = result.stdout.strip().split("\n")
    
    assert len(output_files) == 4, "Duplication file count not match"
    assert any([x.endswith("image007.jpg") for x in output_files])
    assert any([x.endswith("image012.jpg") for x in output_files])
    assert any([x.endswith("image014.jpg") for x in output_files])
    assert any([x.endswith("image021.jpg") for x in output_files])