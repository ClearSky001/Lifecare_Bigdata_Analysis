import os
import subprocess
import pytest


SCRIPT_PATH = "./advanced_file_duplication_detector.sh"
def parse_output(output):

    output_lines = output.strip().split("\n")
    parsed_output = []
    
    for line in output_lines:
        count_md5, files = line.split(":")
        count, md5 = count_md5.strip().split()
        file_list = [os.path.split(x)[-1] for x in files.strip().split()]
        parsed_output.append((int(count), md5, file_list))
    
    return parsed_output

def compare_result(output, expected):
    assert len(output) == len(expected), "Number of Duplication cases not match"

    for i, (expected_count, expected_md5sum, expected_file_list) in enumerate(expected):
        count, md5sum, file_list = output[i]
        assert count == expected_count, "Duplication count does not match"
        assert md5sum == expected_md5sum, "md5sum checksum does not match"
        assert set(file_list) == set(expected_file_list), "Duplication file list does not match"
        break #only compare top 1


def test_find_duplicates_1_score_2():
    test_dir = "tests/test_1"
    result = subprocess.run([SCRIPT_PATH, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    parsed_output = parse_output(result.stdout)

    expected_result = [
        (3, "f6464ed766daca87ba407aede21c8fcc", ["image007.jpg", "image012.jpg", "image014.jpg"]),
        (2, "c7978522c58425f6af3f095ef1de1cd5", ["image019.jpg", "image020.jpg"]),
        (2, "146b163929b6533f02e91bdf21cb9563", ["image001.jpg", "image003.jpg"]),
    ]
    
    compare_result(parsed_output, expected_result)

        
def test_find_duplicates_2_score_2():
    test_dir = "tests/test_2"
    result = subprocess.run([SCRIPT_PATH, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    parsed_output = parse_output(result.stdout)

    expected_result = [
        (2, "146b163929b6533f02e91bdf21cb9563", ["image001.jpg", "image003.jpg"]),
    ]

    compare_result(parsed_output, expected_result)

def test_find_duplicates_3_score_2():
    test_dir = "tests/test_3"
    result = subprocess.run([SCRIPT_PATH, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    parsed_output = parse_output(result.stdout)

    expected_result = [
        (2, "c7978522c58425f6af3f095ef1de1cd5", ["image019.jpg", "image020.jpg"]),
    ]

    compare_result(parsed_output, expected_result)

def test_find_duplicates_4_score_2():
    test_dir = "tests/test_4"
    result = subprocess.run([SCRIPT_PATH, test_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    parsed_output = parse_output(result.stdout)

    expected_result = [
        (4, "f6464ed766daca87ba407aede21c8fcc", ["image007.jpg", "image012.jpg", "image014.jpg", "image021.jpg"]),
        (2, "c7978522c58425f6af3f095ef1de1cd5", ["image019.jpg", "image020.jpg"]),
        (2, "146b163929b6533f02e91bdf21cb9563", ["image001.jpg", "image003.jpg"]),
    ]

    compare_result(parsed_output, expected_result)
