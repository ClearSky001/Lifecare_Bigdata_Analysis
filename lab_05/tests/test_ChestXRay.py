import os

import pytest
import pandas as pd
import numpy as np

from ChestXRay import encode_labels_one_hot, check_data_leakage, split_data_by_patient, calculate_class_weights, evaluation_loop

DATA_ROOT_DIR = "/datasets/ChestX-ray14"


def test_one_hot_encode_score_1():
    data = {
        'Image Index': ['00000001_000.png', '00000001_001.png', '00000001_002.png', '00000002_000.png', '00000003_000.png'],
        'Finding Labels': ['Cardiomegaly', 'Cardiomegaly|Emphysema', 'Cardiomegaly|Effusion', 'No Finding', 'Hernia'],
        'Follow-up #': [0, 1, 2, 0, 0],
        'Patient ID': [1, 1, 1, 2, 3]
    }
    df = pd.DataFrame(data)

    expected_output = pd.DataFrame({
        'Cardiomegaly': [1, 1, 1, 0, 0],
        'Effusion': [0, 0, 1, 0, 0],
        'Emphysema': [0, 1, 0, 0, 0],
        'Hernia': [0, 0, 0, 0, 1],
        'No Finding': [0, 0, 0, 1, 0]
    }, index=[0, 1, 2, 3, 4])
    
    result = encode_labels_one_hot(df, 'Finding Labels')
    assert result.shape == expected_output.shape, "encode_labels_one_hot function returned wrong value"

    result = result[expected_output.columns]  # Ensure column order matches
    assert (result.columns == expected_output.columns).all(), "encode_labels_one_hot function returned wrong value"

    assert np.array_equal(result.to_numpy(), expected_output.to_numpy()), "encode_labels_one_hot function returned wrong value"

def test_data_leakage_score_1():
    train_data = {
        'Patient ID': [1, 2, 3],
        'Data': ['a', 'b', 'c']
    }
    test_data = {
        'Patient ID': [4, 5, 6],
        'Data': ['d', 'e', 'f']
    }
    train_df = pd.DataFrame(train_data)
    test_df = pd.DataFrame(test_data)
    overlap_found = check_data_leakage(train_df, test_df)
    assert overlap_found == False, "check_data_leakage returned wrong value"

    test_data_leak = {
        'Patient ID': [3, 4],
        'Data': ['g', 'h']
    }
    test_df_leak = pd.DataFrame(test_data_leak)
    overlap_found_leak = check_data_leakage(train_df, test_df_leak)
    assert overlap_found_leak == True, "check_data_leakage returned wrong value"

def test_split_data_score_3():
    df = pd.DataFrame({
        'Patient ID': [1, 1, 2, 2, 3, 3],
        'Image Index': ['img1', 'img2', 'img3', 'img4', 'img5', 'img6'],
        'ClassA': [1, 0, 1, 0, 1, 0],
        'ClassB': [0, 1, 0, 1, 0, 1]
    })
    class_labels = ['ClassA', 'ClassB']
    train_df, val_df, test_df = split_data_by_patient(df, class_labels, val_size=0.2, test_size=0.2, random_state=42)

    # Check for patient overlap
    train_patients = set(train_df['Patient ID'].unique())
    val_patients = set(val_df['Patient ID'].unique())
    test_patients = set(test_df['Patient ID'].unique())
    assert len(train_patients & val_patients) == 0
    assert len(train_patients & test_patients) == 0
    assert len(val_patients & test_patients) == 0

    # Check that all patients are included
    all_patients = train_patients | val_patients | test_patients
    assert all_patients == set(df['Patient ID'].unique())

# Test for calculate_class_weights function
def test_class_weights_score_3():
    metadata = pd.read_csv(os.path.join(DATA_ROOT_DIR, "Data_Entry_2017.csv" ))
    label_onehot = encode_labels_one_hot(metadata, 'Finding Labels')
    label_onehot.drop(columns = ["No Finding"], inplace = True)
    class_labels = sorted(label_onehot.columns.tolist())

    metadata_with_onehot = pd.concat([metadata, label_onehot], axis=1) #[['Image Index', 'Patient ID']]


    class_weights = calculate_class_weights(metadata_with_onehot, class_labels)
    #print(list(class_weights))

    expected_output = [8.699801020849554, 39.38904899135447, 23.023998285836726, 47.68432479374729, 7.41931365923256, 43.56279809220986, 65.5005931198102, 492.92070484581507, 4.6358701115914345, 18.391214112763752, 16.70968251461065, 32.122599704579024, 77.35080363382251, 20.146737080347037]

    assert np.isclose(np.array(class_weights), np.array(expected_output), atol=1e-5).all(), "calculate_class_weights function returned different values"

def test_evaluation_loop_score_2():
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from torch import nn
    device = torch.device('cpu')

    class SimpleModel(nn.Module):
        def forward(self, x):
            return x

    torch.manual_seed(0)
    model = SimpleModel()
    criterion = nn.BCEWithLogitsLoss()
    inputs = torch.rand(20, 5)
    targets = torch.randint(0, 2,(20, 5), dtype = torch.float32)

    dataset = TensorDataset(inputs, targets)
    dataloader = DataLoader(dataset, batch_size=4)


    metrics = evaluation_loop(model, device, dataloader, criterion, epoch=0, phase='validation')
    # print(metrics)
    assert metrics['f1_macro'] == pytest.approx(0.619376026272578, abs = 1e-5), "f1_macro value from evaluation_loop is different"
