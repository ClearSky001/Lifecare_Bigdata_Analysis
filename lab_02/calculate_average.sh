#!/bin/bash

# 설명:
# 이 스크립트는 첫 번째 인자로 받은 CSV 파일에서 세 번째 컬럼의 값들의 평균을 계산하고,
# 그 결과를 두 번째 인자로 받은 파일에 저장합니다.
#
# Arguments:
#   $1: 계산할 데이터가 있는 CSV 파일 이름 (예: score.csv)
#   $2: 계산된 평균 값을 저장할 결과 파일 이름 (예: average.txt)
#
# Output:
#   $2: 계산된 평균값이 저장됩니다.
#
# Example Usage:
#   ./calculate_average.sh resources/score.csv average.txt

csv_file=$1
result_file=$2

##### YOUR CODE START #####  

##### YOUR CODE END #####