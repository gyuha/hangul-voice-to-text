#!/bin/bash

# 스크립트 실행 방법 확인
if [ $# -ne 1 ]; then
    echo "사용법: $0 <MP4 파일이 있는 폴더 경로>"
    exit 1
fi

# 폴더 경로 확인
FOLDER_PATH="$1"
if [ ! -d "$FOLDER_PATH" ]; then
    echo "오류: '$FOLDER_PATH' 폴더를 찾을 수 없습니다."
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# MP4 파일 개수 확인
MP4_COUNT=$(find "$FOLDER_PATH" -type f -name "*.mp4" | wc -l)
if [ $MP4_COUNT -eq 0 ]; then
    echo "오류: '$FOLDER_PATH' 폴더에 MP4 파일이 없습니다."
    exit 1
fi

echo "총 $MP4_COUNT개의 MP4 파일을 처리합니다."

# 각 MP4 파일 처리
for mp4_file in "$FOLDER_PATH"/*.mp4; do
    if [ -f "$mp4_file" ]; then
        echo "처리 중: $(basename "$mp4_file")"
        python mp4_srt_puller.py "$mp4_file" --model medium --keep-audio
        echo "완료: $(basename "$mp4_file")"
        echo "----------------------------------------"
    fi
done

echo "모든 파일 처리가 완료되었습니다." 