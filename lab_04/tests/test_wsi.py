import pytest
import inspect
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
from wsi import create_masks, extract_patches

data_root_dir = "/datasets/CAMELYON16"
slide_name = "test_001"
slide_filepath = Path(data_root_dir) / f"testing/images/{slide_name}.tif"
annotation_filepath = Path(data_root_dir) / f"testing/lesion_annotations/{slide_name}.xml"

def test_create_masks_score_2():
    mask_level = 5 

    slide, slide_thumbnail, tumor_mask, tissue_mask, normal_mask = create_masks(slide_filepath, annotation_filepath, mask_level = mask_level)

    assert tumor_mask.shape == (2800, 2688), "Tumor mask shape is not what expected"
    assert tumor_mask.shape == normal_mask.shape, "Normal mask shape is inconsistant with Tumor mask"

    result_values = tumor_mask[335:345].sum(axis = 1)
    expected_values = np.array([0, 0, 765, 4080, 6885, 11985, 16575, 17850, 19380, 20910])
    assert np.array_equal(result_values, expected_values), "Tumor mask is not correctly generated."

    result_values = normal_mask[335:345].sum(axis = 1)
    expected_values = np.array([68595, 70380, 69870, 69615, 67320, 72165, 71910, 71655, 69360, 68850])
    assert np.array_equal(result_values, expected_values), "Normal mask is not correctly generated."

def test_extract_patches_score_2():

    patch_config = {
        'patch_size': 304,               # Size of the patch at the highest resolution
        'normal_area_threshold': 0.1,    # Minimum ratio of the normal mask area for selecting normal patches
        'normal_sel_ratio': 1,           # Probability of selecting a normal patch
        'max_normal_patches': 3,      # Maximum number of normal patches to extract
        'tumor_area_threshold': 0.8,     # Minimum ratio of the tumor mask area for selecting tumor patches
        'tumor_sel_ratio': 1,            # Probability of selecting a tumor patch
        'max_tumor_patches': 3        # Maximum number of tumor patches to extract
    }
    mask_level = 4

    patch_save_dir = Path("tests/patches")
    try:
        slide, slide_thumbnail, tumor_mask, tissue_mask, normal_mask = create_masks(slide_filepath, annotation_filepath, mask_level = mask_level)
        
        extract_patches(slide, slide_thumbnail, tumor_mask, normal_mask, mask_level = mask_level, 
                    patch_config= patch_config,
                    save_path = patch_save_dir)
        
        patches = sorted([str(x) for x in patch_save_dir.glob('**/*') if x.is_file()])
        print(patches)

        expected_patches = ['tests/patches/n_11_137.png', 'tests/patches/n_7_192.png', 'tests/patches/n_7_193.png', 'tests/patches/t_50_83.png', 'tests/patches/t_51_46.png', 'tests/patches/t_51_47.png']

        assert patches == expected_patches, "Extracted patches do not match with the expected list."

        img = np.array(Image.open(patches[-1]).convert('RGB'))
        assert img.shape == (304, 304, 3)

        result_values = img[30, 150:155, 0]
        target_values = [135, 142, 150, 149, 148]
        print(result_values)
        assert np.isclose(result_values, target_values, atol = 1).all(), "First patch content does not match with the expected reference image."

    finally:
        if patch_save_dir.exists():
            shutil.rmtree(patch_save_dir)


def test_gitignore_score_2():
    # Path to the .gitignore file
    gitignore_path = "../.gitignore"
    
    checkpoints_patterns = ['checkpoints', '**/checkpoints', '*/checkpoints', 'checkpoints/', '**/checkpoints/', '*/checkpoints/']

    # Initialize flags for checking if both entries exist at the start of a line
    checkpoints_found = False
    
    # Open the .gitignore file and check line-by-line
    with open(gitignore_path, 'r') as f:
        for line in f:
            stripped_line = line.strip()  # Remove any leading/trailing whitespaces
            if any(stripped_line == pattern for pattern in checkpoints_patterns):
                checkpoints_found = True
    
    assert checkpoints_found, "'checkpoints' not found in .gitignore"