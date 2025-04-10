# 음성-텍스트 변환기

MP3 파일에서 음성을 텍스트로 변환하는 Python 스크립트입니다. Google Speech Recognition과 OpenAI Whisper 두 가지 방법을 지원합니다.
또한 MP4 파일에서 SRT 자막을 추출하는 기능도 제공합니다.

## 설치 방법

1. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 추가로 필요한 시스템 패키지 설치:
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`
- Windows: [FFmpeg 다운로드](https://ffmpeg.org/download.html)

## 사용 방법

### 1. Google Speech Recognition 사용
```bash
python main.py [MP3 파일 경로]
```

### 2. Whisper 사용
```bash
python whisper_transcribe.py [MP3 파일 경로] [--model MODEL_SIZE]
```

### 3. MP4에서 SRT 자막 추출
```bash
python mp4_srt_puller.py [MP4 파일 경로] [--model MODEL_SIZE]
```

모델 크기 옵션:
- `tiny`: 가장 작은 모델 (빠른 속도, 낮은 정확도)
- `base`: 기본 모델 (권장)
- `small`: 중간 크기 모델
- `medium`: 큰 모델
- `large`: 가장 큰 모델 (높은 정확도, 느린 속도)

예시:
```bash
python mp4_srt_puller.py video.mp4 --model base
```

## 참고사항

### Google Speech Recognition
- 인터넷 연결이 필요합니다.
- 한국어 음성 인식이 지원됩니다.

### Whisper
- 오프라인에서 작동합니다.
- 더 높은 정확도를 제공합니다.
- 모델 크기에 따라 처리 속도가 달라집니다.
- 처음 실행 시 모델을 다운로드합니다.

### MP4에서 SRT 자막 추출
- FFmpeg가 필요합니다.
- MP4 파일에서 오디오를 추출하여 처리합니다.
- 자동으로 타임스탬프가 포함된 SRT 파일을 생성합니다.
- 처리 완료 후 임시 WAV 파일은 자동으로 삭제됩니다. 