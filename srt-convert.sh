#!/bin/bash

# 스크립트 실행 방법 확인
if [ $# -ne 1 ]; then
    echo "사용법: $0 <MP4 파일이 있는 폴더 경로>"
    exit 1
fi

# 시간을 분:초 형식으로 변환하는 함수
format_time() {
    local seconds=$1
    local minutes=$((seconds / 60))
    local remaining_seconds=$((seconds % 60))
    echo "${minutes}분 ${remaining_seconds}초"
}

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

echo "총 ${MP4_COUNT}개의 MP4 파일을 처리합니다."

# 시간 측정 결과를 저장할 파일
TIME_LOG="time.txt"
echo "파일명,소요시간(초),소요시간(분:초)" > "$TIME_LOG"

# 각 MP4 파일 처리
for mp4_file in "$FOLDER_PATH"/*.mp4; do
    if [ -f "$mp4_file" ]; then
        filename=$(basename "$mp4_file")
        echo "처리 중: $filename"
        
        # 시작 시간 기록
        start_time=$(date +%s)
        
        # 파일 처리
        python mp4_srt_puller.py "$mp4_file" --model medium --keep-audio
        
        # 종료 시간 기록 및 소요 시간 계산
        end_time=$(date +%s)
        elapsed_time=$((end_time - start_time))
        formatted_time=$(format_time $elapsed_time)
        
        # 결과 기록
        echo "$filename,$elapsed_time,$formatted_time" >> "$TIME_LOG"
        
        echo "완료: $filename (소요시간: $formatted_time)"
        echo "----------------------------------------"
    fi
done

echo "모든 파일 처리가 완료되었습니다."
echo "시간 측정 결과는 $TIME_LOG 파일에서 확인할 수 있습니다." 