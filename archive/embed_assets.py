import base64
import os

def embed_images():
    html_path = "ATSM_Final_Report_without.html"
    
    # 내장할 이미지 목록 및 매핑
    image_mapping = {
        "outputs/benchmarking_acm_nber.png": "benchmarking_acm_nber.png",
        "outputs/rolling_risk_shift.png": "rolling_risk_shift.png",
        "outputs/breakpoint_sensitivity.png": "breakpoint_sensitivity.png",
        "outputs/zlb_tp_distribution.png": "zlb_tp_distribution.png"
    }

    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    for path, alt_text in image_mapping.items():
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode('utf-8')
                data_uri = f"data:image/png;base64,{b64_string}"
                
                # 기존 경로 치환 (오타가 있을 수 있는 패턴 포함)
                html_content = html_content.replace(f'src="{path}"', f'src="{data_uri}"')
                # 혹시 모를 중첩 경로 오타 대응
                html_content = html_content.replace(f'src="outputs/{path}"', f'src="{data_uri}"')
                print(f"Embedded: {path}")
        else:
            print(f"Warning: Image not found at {path}")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("\n[SUCCESS] All images embedded into ATSM_Final_Report_without.html")

if __name__ == "__main__":
    embed_images()
