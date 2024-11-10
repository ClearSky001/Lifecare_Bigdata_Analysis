#!/bin/bash

## 설명:
## 이 스크립트는 입력받은 paired-end sequencing 데이터 (fastq.gz 파일)에 대해 단일 염기 변이(SNV) 탐지를 수행하는 파이프라인입니다.
## The pipeline includes quality control, adapter trimming, read alignment, duplicate marking, and variant calling.
## 사용되는 주요 도구: FastQC, Cutadapt, BWA, Samtools, GATK, Picard.
##
## Example usage:
## ./snv_call_pipeline.sh hl60_brca1 ./resources ./intermediates ./results
##
## Arguments:
SAMPLE_NAME=$1         # 샘플이름 (Example: hl60_brca1). FASTQ 파일과 결과 파일을 구별하는데 사용됩니다.
INPUT_DIR=$2           # Directory that store input fastq.gz files and reference genome
INTERMEDIATE_DIR=$3    # Directory for storing intermediate files
RESULTS_DIR=$4         # Directory for storing final results

# Define input files
READ1=$INPUT_DIR/"$SAMPLE_NAME"_R1.fastq.gz
READ2=$INPUT_DIR/"$SAMPLE_NAME"_R2.fastq.gz
REFERENCE_GENOME=$INPUT_DIR/reference_genome/chr17_subset.fa

# Create necessary directories
mkdir -p $INTERMEDIATE_DIR
mkdir -p $RESULTS_DIR/FastQC

# Define summary file
SUMMARY_FILE=$RESULTS_DIR/QC_summary.txt



##### 실습1. $READ1 파일 첫번쨰 NGS read의 read length를 계산하여 QC_summary $SUMMARY_FILE 파일에 저장하라
zcat $READ1 | head -2 | tail -1 | awk '{print length($0)}' > $SUMMARY_FILE

##### 실습2. FastQC를 수행하고 결과를 디렉토리 $RESULTS_DIR/FastQC에 저장하라
fastqc -o $RESULTS_DIR/FastQC $READ1 $READ2

##### 실습3-1. Cutadapt를 이용해 $READ1파일과 $READ2파일에 대하여 Illumina adapter 및 low quality base trimming을 수행하여 결과를 $INTERMEDIATE_DIR폴더에 $SAMPLE_NAME.trimmed_R1.fastq.gz, $SAMPLE_NAME.trimmed_R2.fastq.gz의 파일이름으로 저장하라
READ1_TRIMMED=$INTERMEDIATE_DIR/$SAMPLE_NAME.trimmed_R1.fastq.gz
READ2_TRIMMED=$INTERMEDIATE_DIR/$SAMPLE_NAME.trimmed_R2.fastq.gz

cutadapt -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
    -o $READ1_TRIMMED -p $READ2_TRIMMED $READ1 $READ2
    
##### 실습3-2. 두개의 trimmed 파일에 대해 FastQC를 수행하여 결과를 $RESULTS_DIR/FastQC에 저장하라
fastqc -o $RESULTS_DIR/FastQC $READ1_TRIMMED $READ2_TRIMMED

##### 실습3-3. $READ1_TRIMMED 파일에 대한 평균 read length를 계산하여 $SUMMARY_FILE 파일에 "append"하라
zcat $READ1_TRIMMED | awk '{if(NR % 4 == 2) {sum += length($0); count++}} END {print sum/count}' >> $SUMMARY_FILE

##### 실습 4. bwa index, samtools faidx, gatk CreateSequenceDictionary 3가지 툴로 reference genome을 인덱싱하라
bwa index $REFERENCE_GENOME
samtools faidx $REFERENCE_GENOME
gatk CreateSequenceDictionary -R $REFERENCE_GENOME -O ${REFERENCE_GENOME%.*}.dict


##### 실습 5-1. bwa mem 알고리즘을 이용하여 $READ1_TRIMMED $READ2_TRIMMED 파일을 reference genome에 align하고 결과를 $INTERMEDIATE_DIR/$SAMPLE_NAME.aligned.sam 파일에 저장하라
RG="@RG\tID:$SAMPLE_NAME\tSM:$SAMPLE_NAME\tLB:LIB_$SAMPLE_NAME\tPL:ILLUMINA"
samfile=$INTERMEDIATE_DIR/$SAMPLE_NAME.aligned.sam

bwa mem -R "$RG" $REFERENCE_GENOME $READ1_TRIMMED $READ2_TRIMMED > $samfile

##### 실습 5-2. $INTERMEDIATE_DIR/$SAMPLE_NAME.aligned.sam파일에서 전체 read수를 출력하여 $SUMMARY_FILE에 append하라
samtools view -c $samfile >> $SUMMARY_FILE

##### 실습 5-3. Mapping quality가 30 이상인 read 수를 계산하여 $SUMMARY_FILE에 append하라
samtools view -q 30 -c $samfile >> $SUMMARY_FILE

##### 실습 6. samtools sort명령어를 사용하여 aligned.sam파일을 coordinate sorting하고 결과를 BAM형식으로 출력하여 $INTERMEDIATE_DIR/$SAMPLE_NAME.sorted.bam 파일에 저장하라
sorted_bam=$INTERMEDIATE_DIR/$SAMPLE_NAME.sorted.bam
samtools sort -o $sorted_bam $samfile
# sorted.bam 파일 인덱싱
samtools index $sorted_bam

##### 실습 7-1. Picard MarkDuplicates를 이용하여 sorted.bam파일에 PCR duplicate을 마킹하고 결과파일은 $INTERMEDIATE_DIR/$SAMPLE_NAME.markdup.bam 파일에, metric file은 $INTERMEDIATE_DIR/$SAMPLE_NAME.markdup_metrics.txt에 저장하라
PREPROCESSED_BAM_FILE=$INTERMEDIATE_DIR/$SAMPLE_NAME.markdup.bam
metrics_file=$INTERMEDIATE_DIR/$SAMPLE_NAME.markdup_metrics.txt

picard MarkDuplicates I=$sorted_bam O=$PREPROCESSED_BAM_FILE M=$metrics_file

# markdup.bam 파일 인덱싱
samtools index $PREPROCESSED_BAM_FILE

##### 실습 7-2. $PREPROCESSED_BAM_FILE 파일로 부터 PCR duplicate rate를 계산하여 $SUMMARY_FILE에 값을 append하라
# PREPROCESSED_BAM_FILE=$INTERMEDIATE_DIR/$SAMPLE_NAME.markdup.bam
awk '/^LIBRARY/ {getline; print $9}' $metrics_file >> $SUMMARY_FILE

##### 실습 8-1. HaplotypeCaller를 이용해 $PREPROCESSED_BAM_FILE 파일에 대해 variant call을 수행하고 결과를 $RESULTS_DIR/$SAMPLE_NAME.raw_variants.vcf 파일에 저장하라. reference genome에는 $REFERENCE_GENOME 값을 이용할 것
RAW_VCF_FILE=$RESULTS_DIR/$SAMPLE_NAME.raw_variants.vcf

gatk HaplotypeCaller \
    -R $REFERENCE_GENOME \
    -I $PREPROCESSED_BAM_FILE \
    -O $RAW_VCF_FILE \
    --stand-call-conf 30 \
    --verbosity DEBUG

##### 실습 8-2. $RAW_VCF_FILE 파일에서 variant quality > 50 인 record와 header를 출력하여 $FILTERED_VCF 파일에 저장하라
# RAW_VCF_FILE=$RESULTS_DIR/$SAMPLE_NAME.raw_variants.vcf
FILTERED_VCF=$RESULTS_DIR/$SAMPLE_NAME.filtered_variants.vcf
awk '$1 ~ /^#/ || ($1 !~ /^#/ && $6 > 50)' $RAW_VCF_FILE > $FILTERED_VCF