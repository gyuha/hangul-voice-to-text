import os
import speech_recognition as sr
from pydub import AudioSegment
import argparse

def convert_mp3_to_wav(mp3_path):
    """MP3 파일을 WAV 파일로 변환"""
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace('.mp3', '.wav')
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_audio(audio_path):
    """음성 파일을 텍스트로 변환"""
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        
    try:
        # 한국어로 인식하도록 설정
        text = recognizer.recognize_google(audio, language='ko-KR')
        return text
    except sr.UnknownValueError:
        return "음성을 인식할 수 없습니다."
    except sr.RequestError as e:
        return f"음성 인식 서비스 오류: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='MP3 파일에서 음성을 텍스트로 변환')
    parser.add_argument('mp3_file', help='변환할 MP3 파일 경로')
    args = parser.parse_args()

    # MP3를 WAV로 변환
    wav_path = convert_mp3_to_wav(args.mp3_file)
    
    # 음성을 텍스트로 변환
    text = transcribe_audio(wav_path)
    
    # 임시 WAV 파일 삭제
    os.remove(wav_path)
    
    print("인식된 텍스트:")
    print(text)

if __name__ == "__main__":
    main() 