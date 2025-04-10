import whisper
import argparse
import subprocess
import os
import json
from datetime import datetime, timedelta

def extract_audio(mp4_path):
    """MP4 파일에서 오디오를 추출하여 WAV 파일로 저장"""
    wav_path = mp4_path.replace('.mp4', '.wav')
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

def transcribe_video(mp4_path, model_size="base"):
    """MP4 파일을 SRT 자막으로 변환"""
    # 오디오 추출
    print("오디오 추출 중...")
    wav_path = extract_audio(mp4_path)
    if not wav_path:
        return False
    
    try:
        # Whisper 모델 로드
        print(f"모델 {model_size}을 로드 중...")
        model = whisper.load_model(model_size)
        
        # 음성 인식 실행
        print("음성 인식 중...")
        result = model.transcribe(wav_path, language="ko")
        
        # SRT 파일 생성
        srt_path = mp4_path.replace('.mp4', '.srt')
        create_srt(result['segments'], srt_path)
        print(f"자막 파일이 생성되었습니다: {srt_path}")
        
        return True
    finally:
        # 임시 WAV 파일 삭제
        if os.path.exists(wav_path):
            os.remove(wav_path)

def main():
    parser = argparse.ArgumentParser(description='MP4 파일에서 SRT 자막을 추출')
    parser.add_argument('mp4_file', help='변환할 MP4 파일 경로')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'],
                      help='사용할 Whisper 모델 크기 (기본값: base)')
    args = parser.parse_args()

    if not os.path.exists(args.mp4_file):
        print(f"오류: 파일을 찾을 수 없습니다: {args.mp4_file}")
        return

    success = transcribe_video(args.mp4_file, args.model)
    if not success:
        print("자막 생성에 실패했습니다.")

if __name__ == "__main__":
    main()
