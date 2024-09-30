import os
import subprocess
import pytest


SCRIPT_PATH = "./calculate_average.sh"

def create_test_csv(file_path, rows):
    """
    Helper function to create a test CSV file with provided rows.
    """
    with open(file_path, 'w') as f:
        for row in rows:
            f.write(row + "\n")


def test_calculate_average_socre_1():
    test_csv = "resources/score.csv"
    result_file = "tests/average_result.txt"
    
    subprocess.run([SCRIPT_PATH, test_csv, result_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    with open(result_file, 'r') as f:
        result = float(f.read().strip())
    
    assert result == pytest.approx(53.8333, rel=1e-3), f"While testing {SCRIPT_PATH}: Expected 84.33 but got {result}"
    
    os.remove(result_file)


def test_calculate_average_2_score_1():
    test_csv = "tests/test_data.csv"
    result_file = "tests/average_result.txt"
    
    create_test_csv(test_csv, [
        "1,Alice,75.0,100",
        "2,Bob,85.0,100",
        "3,Charlie,95.0,100"
        "4,David,85,100"
    ])
    
    subprocess.run([SCRIPT_PATH, test_csv, result_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    with open(result_file, 'r') as f:
        result = float(f.read().strip())
    
    assert result == pytest.approx(85.0, rel=1e-3), f"While testing {SCRIPT_PATH}: Expected 85.0 but got {result}"
    
    os.remove(test_csv)
    os.remove(result_file)