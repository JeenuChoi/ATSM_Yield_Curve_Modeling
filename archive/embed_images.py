import base64
import os
import re

# 경로 설정
project_path = r'C:\Users\user\Desktop\ATSM_Project'
html_input = os.path.join(project_path, 'ATSM_Final_Grand_Legacy_Report.html')
html_output = os.path.join(project_path, 'ATSM_Final_Grand_Legacy_Report_Standalone.html')

def embed_images():
    print("이미지 임베딩 작업을 시작합니다...")
    
    # 원본 HTML 읽기
    with open(html_input, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 이미지 태그 찾기 (src="outputs/...")
    img_tags = re.findall(r'src="(outputs/.*?\.png)"', content)
    
    embedded_count = 0
    for img_rel_path in img_tags:
        img_full_path = os.path.join(project_path, img_rel_path)
        
        if os.path.exists(img_full_path):
            with open(img_full_path, 'rb') as img_f:
                # 이미지를 Base64로 인코딩
                b64_data = base64.b64encode(img_f.read()).decode('utf-8')
                # HTML 내 경로를 Base64 데이터로 치환
                content = content.replace(f'src="{img_rel_path}"', f'src="data:image/png;base64,{b64_data}"')
                embedded_count += 1
                print(f"임베딩 완료: {img_rel_path}")
        else:
            print(f"파일을 찾을 수 없음: {img_rel_path}")
            
    # 최종 파일 저장
    with open(html_output, 'w', encoding='utf-8') as f_out:
        f_out.write(content)
        
    print(f"\n작업 완료! {embedded_count}개의 이미지가 포함되었습니다.")
    print(f"최종 파일: {html_output}")

if __name__ == "__main__":
    embed_images()
