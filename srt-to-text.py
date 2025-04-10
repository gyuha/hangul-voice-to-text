from __future__ import annotations
import re  
import sys  
import os

def extract_text_from_srt(input_filepath, output_filepath):  
    try:  
        with open(input_filepath, 'r', encoding='utf-8') as infile, \
             open(output_filepath, 'w', encoding='utf-8') as outfile:  

            # 각 줄을 순회하며 처리  
            for line in infile:  
                stripped_line = line.strip()  

                # 빈 줄, 숫자만 있는 줄, 시간 정보 줄은 건너뛰니다.  
                if not stripped_line or \
                   re.match(r'^\d+$', stripped_line) or \
                   re.match(r'^\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}$', stripped_line):  
                    continue  

                # 위 조건에 해당하지 않으면 텍스트 줄로 간주  
                # HTML 유사 태그 제거  
                text_line = re.sub(r'<[^>]+>', '', line)  
                # 앞뒤 공백 제거 후 결과 파일에 쓰기  
                cleaned_text = text_line.strip()  
                if cleaned_text: # 태그 제거 후 내용이 남은 경우에만 쓰기  
                    outfile.write(cleaned_text + '\n')  

        print(f"텍스트 추출 완료: {output_filepath}")  

    except FileNotFoundError:  
        print(f"오류: 입력 파일 '{input_filepath}'을(를) 찾을 수 없습니다.", file=sys.stderr)  
        sys.exit(1)
    except Exception as e:  
        print(f"오류 발생: {e}", file=sys.stderr)  
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("사용법: python srt-to-text.py <입력_SRT_파일>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not input_file.endswith('.srt'):
        print("오류: SRT 파일만 처리할 수 있습니다.")
        sys.exit(1)

    # 출력 파일명 생성 (.srt를 .txt로 변경)
    output_file = os.path.splitext(input_file)[0] + '.txt'
    
    extract_text_from_srt(input_file, output_file)

if __name__ == '__main__':
    main()

# --- 사용 예시 ---  
# 입력 SRT 파일 경로와 출력 텍스트 파일 경로를 지정하세요.  
# input_srt_file = 'your_subtitle.srt'  
# output_text_file = 'extracted_text_srt.txt'  
# extract_text_from_srt(input_srt_file, output_text_file)  
# 실제 사용 시에는 위 주석을 해제하고 파일 경로를 맞게 수정하세요.  

