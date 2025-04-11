import whisper
import argparse
import subprocess
import os
import json
from datetime import datetime, timedelta
import sys
import time

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
        
        # 음성 인식 실행
        result = model.transcribe(
            wav_path,
            language="ko",
            verbose=True,  # 자세한 로그 출력
            # compression_ratio_threshold=3.4,
            # logprob_threshold=-1.0,
            # no_speech_threshold=0.6,
            # condition_on_previous_text=True,
            # initial_prompt=None,
            # word_timestamps=True,
            
        )
        
        # 진행 상황 출력
        total_segments = len(result['segments'])
        for i, segment in enumerate(result['segments'], 1):
            print_progress(segment, total_segments, i)
            # 실시간으로 보이도록 잠시 대기
            time.sleep(0.1)
        
        # SRT 파일 생성
        srt_path = mp4_path.replace('.mp4', '.srt')
        create_srt(result['segments'], srt_path)
        print(f"\n자막 파일이 생성되었습니다: {srt_path}")
        
        return True
    finally:
        # 임시 WAV 파일 삭제 (keep_audio가 False인 경우에만)
        if not keep_audio and os.path.exists(wav_path):
            os.remove(wav_path)

def main():
    parser = argparse.ArgumentParser(description='MP4 파일에서 SRT 자막을 추출')
    parser.add_argument('mp4_file', help='변환할 MP4 파일 경로')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'],
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
