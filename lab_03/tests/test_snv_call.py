import os, shutil
from pathlib import Path
import subprocess
import pytest

RESOURCE_DIR = Path("./resources")

SAMPLE_NAME = "test_sample1"
TEST_DIR = Path("./temporary_testdir")
INPUT_DIR = Path(TEST_DIR) / "inputs"
INTERMEDIATE_DIR = Path(TEST_DIR) / "intermediates"
RESULTS_DIR = Path(TEST_DIR) / "results"
SCRIPT_PATH = "./snv_call_pipeline.sh"


@pytest.fixture(scope="module")
def setup_directories():
    if os.path.exists(TEST_DIR):
        print(f"----- Cleaning up previous test_dir before testing : {TEST_DIR}")
        subprocess.run(["rm", "-rf", TEST_DIR])

    os.makedirs(INPUT_DIR / "reference_genome", exist_ok=True)
    os.makedirs(INTERMEDIATE_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    read1 = RESOURCE_DIR / "hl60_brca1_R1.fastq.gz"
    read2 = RESOURCE_DIR / "hl60_brca1_R2.fastq.gz"
    reference_genome = RESOURCE_DIR / "reference_genome" / "chr17_subset.fa"
    shutil.copy(read1, INPUT_DIR / f"{SAMPLE_NAME}_R1.fastq.gz")
    shutil.copy(read2, INPUT_DIR / f"{SAMPLE_NAME}_R2.fastq.gz")
    shutil.copy(reference_genome, INPUT_DIR / "reference_genome")
    print("----- Test file preparation complete")

    yield  # Run the tests

    print("----- All test run finished. Cleaning up test_dir after testing : {TEST_DIR}")
    subprocess.run(["rm", "-rf", TEST_DIR])

def test_script_execution_score_0(setup_directories):
    result = subprocess.run([SCRIPT_PATH, SAMPLE_NAME, INPUT_DIR, INTERMEDIATE_DIR, RESULTS_DIR], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert result.returncode == 0, f"Script failed to run: {result.stderr.decode()}"

def test_summary_file_score_6():
    # Check if the QC_summary.txt file is created
    summary_file = RESULTS_DIR / "QC_summary.txt"
    assert summary_file.exists(), "QC_summary.txt was not created on expected location"

    expected_values = [151, 147.538, 5242, 5238, 0.0354826]
    with open(summary_file, "r") as f:
        contents = f.read().splitlines()

    assert len(contents) == len(expected_values), f"Expected {len(expected_values)} lines in 'QC_summary.txt' file, but got {len(contents)}"
    
    for i, expected_value in enumerate(expected_values):
        assert float(contents[i].strip()) == pytest.approx(expected_value, abs=1e-4), f"'QC_summary.txt' file line {i+1} value does not match" #: expected {expected_value}, got {contents[i].strip()}


def test_fastqc_results_score_2():
    # Check if FastQC results were generated
    fastqc_dir = RESULTS_DIR / "FastQC"
    assert os.path.exists(fastqc_dir / f"{SAMPLE_NAME}_R1_fastqc.html"), "FastQC R1 report missing"
    assert os.path.exists(fastqc_dir / f"{SAMPLE_NAME}_R2_fastqc.html"), "FastQC R2 report missing"
    assert os.path.exists(fastqc_dir / f"{SAMPLE_NAME}.trimmed_R1_fastqc.html"), "FastQC trimmed R1 report missing"
    assert os.path.exists(fastqc_dir / f"{SAMPLE_NAME}.trimmed_R2_fastqc.html"), "FastQC trimmed R2 report missing"

def test_cutadapt_score_1():
    trimmed_r1 = INTERMEDIATE_DIR / f"{SAMPLE_NAME}.trimmed_R1.fastq.gz"
    trimmed_r2 = INTERMEDIATE_DIR / f"{SAMPLE_NAME}.trimmed_R2.fastq.gz"
    
    assert trimmed_r1.exists(), "Trimmed R1 fastq file not created"
    assert trimmed_r2.exists(), "Trimmed R2 fastq file not created"

def test_ref_index_score_2():
    ref_index1 = INPUT_DIR / "reference_genome/chr17_subset.fa.fai"
    ref_index2 = INPUT_DIR / "reference_genome/chr17_subset.dict"
    ref_index3 = INPUT_DIR / "reference_genome/chr17_subset.fa.bwt"
    assert ref_index1.exists(), "samtools faidx indexing not performed"
    assert ref_index2.exists(), "gatk CreateSequenceDictionary indexing not performed"
    assert ref_index3.exists(), "BWA index not created for reference genome"

def test_align_score_2():
    # Check if the SAM file from BWA MEM was created
    aligned_sam = INTERMEDIATE_DIR / f"{SAMPLE_NAME}.aligned.sam"
    assert aligned_sam.exists(), "Aligned SAM file not created"

def test_sort_bam_score_2():
    sorted_bam = INTERMEDIATE_DIR / f"{SAMPLE_NAME}.sorted.bam"
    assert sorted_bam.exists(), "Sorted BAM file not created"

def test_mark_duplicates_score_1():
    markdup_bam = INTERMEDIATE_DIR / f"{SAMPLE_NAME}.markdup.bam"
    assert markdup_bam.exists(), "MarkDuplicates BAM file not created"

def test_haplotypecaller_vcf_score_2():
    vcf_file = RESULTS_DIR / f"{SAMPLE_NAME}.raw_variants.vcf"
    assert vcf_file.exists(), "VCF file not created by HaplotypeCaller"

    with open(vcf_file, "r") as vcf:
        variant_count = sum(1 for line in vcf if not line.startswith("#"))

    assert variant_count == 37, f"Expected 37 variants at raw_variants.vcf file, but found {variant_count}"

def test_vcf_filter_score_2():
    vcf_file = RESULTS_DIR / f"{SAMPLE_NAME}.filtered_variants.vcf"
    assert vcf_file.exists(), "filtered_variants.vcf file not created"

    with open(vcf_file, "r") as vcf:
        variant_count = sum(1 for line in vcf if not line.startswith("#"))
        
    with open(vcf_file, "r") as vcf:
        header_count = sum(1 for line in vcf if line.startswith("#"))


    assert variant_count == 32, f"Expected 32 variants at filtered_variants.vcf file, but found {variant_count}"
    assert header_count == 26, f"Expected 26 header lines at filtered_variants.vcf file, but found {header_count} lines"