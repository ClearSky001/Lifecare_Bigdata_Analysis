#!/bin/bash

# 설명:
# 이 스크립트는 $1로 전달받은 디렉토리 경로 내의 .jpg 파일들의 md5sum 체크섬을 생성하고,
# 체크섬을 기준으로 중복된 파일들을 찾아 중복 횟수, 체크섬 값, 그리고 해당되는 파일들의 이름들을 출력합니다.
#
# Arguments:
#    $1: 중복여부를 체크할 파일들이 존재하는 디렉터리 경로
#
# Expected Output (stdout):
#    <중복횟수> <md5sum 체크섬 값>: <중복된 파일들의 이름(공백으로 구분)>
#
# 예시출력:
#     3 f6464ed766daca87ba407aede21c8fcc: image007.jpg image012.jpg image014.jpg
#     2 c7978522c58425f6af3f095ef1de1cd5: image019.jpg image020.jpg
#     2 146b163929b6533f02e91bdf21cb9563: image001.jpg image003.jpg
#
# 이 예시에서는 'image007.jpg', 'image012.jpg', 'image014.jpg' 세 개의 파일이
# 내용이 같아서 동일한 md5sum 값을 가졌고, '3'번 중복되었다는 의미입니다.
#
# Example Usage:
#    ./advanced_file_duplication_detector.sh resources/detecting_duplicate_files


directory=$1

##### YOUR CODE START #####  

# 파일 목록과 그들의 md5 체크섬 값 가져오기
declare -A file_map
while IFS= read -r -d '' file; do
    checksum=$(md5sum "$file" | awk '{ print $1 }')
    file_map["$checksum"]+="$file "
done < <(find "$directory" -type f -name "*.jpg" ! -path "*/.ipynb_checkpoints/*" -print0)

# 중복 파일 정보 저장
declare -A duplicate_counts
declare -A duplicate_files
for checksum in "${!file_map[@]}"; do
    files="${file_map[$checksum]}"
    count=$(echo "$files" | wc -w)
    if [ "$count" -gt 1 ]; then  # 중복이 있는 경우만 저장
        duplicate_counts["$checksum"]=$count
        duplicate_files["$checksum"]="$files"
    fi
done

# 중복 파일 수에 따라 정렬하여 출력
for checksum in "${!duplicate_counts[@]}"; do
    echo "${duplicate_counts[$checksum]} $checksum: ${duplicate_files[$checksum]}"
done | sort -rn -k1

##### YOUR CODE END #####