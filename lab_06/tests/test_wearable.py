import pytest
import numpy as np

import torch

from wearable import apply_sliding_window, load_RWHAR_datasets

CSV_FILE_NAME = "/datasets/RealWorldHAR/forearm_acc.csv"

def test_sliding_window_score_5():
    # Sample data
    X = np.array([[i, i + 1, i + 2] for i in range(10)])  # Shape (10, 3)
    y = np.array([i for i in range(10)])  # Shape (10,)
    window_size = 4
    overlap_ratio = 0.5

    # Expected results
    expected_X_windows = np.array([
        [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5]],
        [[2, 3, 4], [3, 4, 5], [4, 5, 6], [5, 6, 7]],
        [[4, 5, 6], [5, 6, 7], [6, 7, 8], [7, 8, 9]],
        [[6, 7, 8], [7, 8, 9], [8, 9, 10], [9, 10, 11]]
    ])
    expected_y_windows = np.array([3, 5, 7, 9])

    # Call the function
    X_windows, y_windows = apply_sliding_window(X, y, window_size, overlap_ratio)

    # Check if the windows match the expected results
    assert np.array_equal(X_windows, expected_X_windows), "X_windows do not match"
    assert np.array_equal(y_windows, expected_y_windows), "y_windows do not match"

def test_load_datasets_score_5():
    config = {"window_size" : 40,
              "overlap_ratio" : 0.75,}


    train_dataset, val_dataset, test_dataset, class_names, class_weights = load_RWHAR_datasets(CSV_FILE_NAME, config = config)

    assert len(train_dataset) == 236795, "X_train shape is different"
    assert len(val_dataset) == 43102, "X_val shape is different"
    assert len(test_dataset) == 40133, "X_test shape is different"
    assert torch.isclose(val_dataset[10000][0].sum(axis = 0), torch.tensor([3.1462554931640625, -18.73414421081543, -3.583420753479004]), atol = 1e-4).all(), "y_train values are incorrect"
    assert torch.isclose(test_dataset[10000][0].sum(axis = 0), torch.tensor([-13.3217191696167, -14.628189086914062, 0.8994050621986389]), atol = 1e-4).all(), "y_train values are incorrect"
