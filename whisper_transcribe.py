import whisper
import argparse
from pydub import AudioSegment
import os

def convert_mp3_to_wav(mp3_path):
    """MP3 파일을 WAV 파일로 변환"""
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace('.mp3', '.wav')
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_audio(audio_path, model_size="base"):
    """Whisper를 사용하여 음성을 텍스트로 변환"""
    # 모델 로드
    model = whisper.load_model(model_size)
    
    # 음성 인식 실행
    result = model.transcribe(audio_path, language="ko")
    
    return result["text"]

def main():
    parser = argparse.ArgumentParser(description='Whisper를 사용하여 MP3 파일에서 음성을 텍스트로 변환')
    parser.add_argument('mp3_file', help='변환할 MP3 파일 경로')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'],
                      help='사용할 Whisper 모델 크기 (기본값: base)')
    args = parser.parse_args()

    # MP3를 WAV로 변환
    wav_path = convert_mp3_to_wav(args.mp3_file)
    
    print(f"모델 {args.model}을 사용하여 음성을 인식 중입니다...")
    # 음성을 텍스트로 변환
    text = transcribe_audio(wav_path, args.model)
    
    # 임시 WAV 파일 삭제
    os.remove(wav_path)
    
    print("\n인식된 텍스트:")
    print(text)

if __name__ == "__main__":
    main() 