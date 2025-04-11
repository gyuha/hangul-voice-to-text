import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta

import whisper


def extract_audio(mp4_path):
    """MP4 파일에서 오디오를 추출하여 WAV 파일로 저장"""
    wav_path = mp4_path.replace('.mp4', '.wav')
    
    # 이미 WAV 파일이 존재하는 경우
    if os.path.exists(wav_path):
        print(f"기존 오디오 파일을 사용합니다: {wav_path}")
        return wav_path
    
    print("오디오 추출 중...")
    command = [
        'ffmpeg',
        '-i', mp4_path,
        '-vn',  # 비디오 스트림 제외
        '-acodec', 'pcm_s16le',  # 16-bit PCM 오디오
        '-ar', '16000',  # 16kHz 샘플링 레이트
        '-ac', '1',  # 모노 오디오
        '-y',  # 기존 파일 덮어쓰기
        wav_path
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        return wav_path
    except subprocess.CalledProcessError as e:
        print(f"오디오 추출 중 오류 발생: {e.stderr.decode()}")
        return None

def format_timestamp(seconds):
    """초 단위 시간을 SRT 형식의 타임스탬프로 변환"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')

def merge_similar_segments(segments, time_threshold=2.0):
    """연속된 동일한 텍스트를 하나로 합치기"""
    if not segments:
        return segments
    
    merged_segments = []
    current_segment = segments[0].copy()
    
    for next_segment in segments[1:]:
        # 현재 세그먼트와 다음 세그먼트의 텍스트가 동일하고
        # 시간 간격이 임계값보다 작은 경우
        if (current_segment['text'].strip() == next_segment['text'].strip() and
            next_segment['start'] - current_segment['end'] <= time_threshold):
            # 끝 시간만 업데이트
            current_segment['end'] = next_segment['end']
        else:
            # 현재 세그먼트를 결과에 추가하고 다음 세그먼트로 이동
            merged_segments.append(current_segment)
            current_segment = next_segment.copy()
    
    # 마지막 세그먼트 추가
    merged_segments.append(current_segment)
    
    return merged_segments

def create_srt(segments, output_path):
    """Whisper의 세그먼트 결과를 SRT 형식으로 변환"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

def print_progress(segment, total_segments, current_segment):
    """진행 상황과 인식된 텍스트를 출력"""
    # 진행률 표시
    progress = (current_segment / total_segments) * 100
    sys.stdout.write(f"\r진행률: {progress:.1f}% ({current_segment}/{total_segments})")
    sys.stdout.flush()
    
    # 인식된 텍스트 출력
    print(f"\n시간: {format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}")
    print(f"인식된 텍스트: {segment['text'].strip()}\n")

def transcribe_video(mp4_path, model_size="base", keep_audio=False):
    """MP4 파일을 SRT 자막으로 변환"""
    # output 폴더 생성
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # SRT 파일 경로 설정
    filename = os.path.basename(mp4_path)
    srt_filename = os.path.splitext(filename)[0] + '.srt'
    srt_path = os.path.join(output_dir, srt_filename)
    
    # 이미 SRT 파일이 존재하는지 확인
    if os.path.exists(srt_path):
        print(f"이미 처리된 파일입니다: {srt_path}")
        return True
    
    # 오디오 추출
    wav_path = extract_audio(mp4_path)
    if not wav_path:
        return False
    
    try:
        # Whisper 모델 로드
        print(f"모델 {model_size}을 로드 중...")
        model = whisper.load_model(model_size)
        
        # 음성 인식 실행
        print("음성 인식 중...")
        
        # 음성 인식 실행 (최적화된 파라미터)
        result = model.transcribe(
            wav_path,
            language="ko",
            verbose=True,  # 자세한 로그 출력
            temperature=0.0,  # 가장 정확한 결과를 위해 온도를 0으로 설정
            compression_ratio_threshold=2.4,  # 압축 비율 임계값 설정
            logprob_threshold=-1.0,  # 로그 확률 임계값 설정
            no_speech_threshold=0.6,  # 무음 임계값 설정
            condition_on_previous_text=True,  # 이전 텍스트를 고려
            initial_prompt="다음은 한국어 음성입니다."  # 초기 프롬프트 설정
        )
        
        # 연속된 동일한 텍스트 합치기
        merged_segments = merge_similar_segments(result['segments'])
        
        # 진행 상황 출력
        total_segments = len(merged_segments)
        for i, segment in enumerate(merged_segments, 1):
            print_progress(segment, total_segments, i)
            # 실시간으로 보이도록 잠시 대기
            time.sleep(0.1)
        
        # SRT 파일 생성
        create_srt(merged_segments, srt_path)
        print(f"\n자막 파일이 생성되었습니다: {srt_path}")
        
        return True
    finally:
        # 임시 WAV 파일 삭제 (keep_audio가 False인 경우에만)
        if not keep_audio and os.path.exists(wav_path):
            os.remove(wav_path)

def main():
    parser = argparse.ArgumentParser(description='MP4 파일에서 SRT 자막을 추출')
    parser.add_argument('mp4_file', help='변환할 MP4 파일 경로')
    parser.add_argument('--model', default='base', 
                      choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                      help='사용할 Whisper 모델 크기 (기본값: base)')
    parser.add_argument('--keep-audio', action='store_true',
                      help='오디오 파일을 삭제하지 않고 보존')
    args = parser.parse_args()

    if not os.path.exists(args.mp4_file):
        print(f"오류: 파일을 찾을 수 없습니다: {args.mp4_file}")
        return

    success = transcribe_video(args.mp4_file, args.model, args.keep_audio)
    if not success:
        print("자막 생성에 실패했습니다.")

if __name__ == "__main__":
    main()
