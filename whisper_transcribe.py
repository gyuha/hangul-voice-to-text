import argparse
import os

import torch  # 추가: PyTorch 라이브러리 가져오기
import whisper
from pydub import AudioSegment


def convert_mp3_to_wav(mp3_path):
    """MP3 파일을 WAV 파일로 변환"""
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace('.mp3', '.wav')
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_audio(audio_path, model_size="base"):
    """Whisper를 사용하여 음성을 텍스트로 변환"""
    # GPU 사용 가능 여부 확인
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        print(f"GPU를 사용하여 처리합니다: {torch.cuda.get_device_name(0)}")
    else:
        print("경고: GPU를 찾을 수 없어 CPU를 사용합니다.")
    
    # 모델 로드 (GPU 사용 명시)
    model = whisper.load_model(model_size, device=device)
    
    # 음성 인식 실행 (fp16 옵션 추가)
    result = model.transcribe(
        audio_path, 
        language="ko",
        fp16=device == "cuda"  # GPU 사용 시 FP16 활성화
    )
    
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