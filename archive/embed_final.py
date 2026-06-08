import base64
import os
import re

def get_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""

def embed_all():
    html_path = "ATSM_Final_Report_without.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 이미지 순서대로 매핑 (HTML 내 나타나는 순서 고려)
    # 1. observed_vs_fitted.png
    # 2. term_premium_decomp.png (Golden)
    # 3. term_premium_surface.png (Golden)
    # 4. benchmarking_acm_nber.png (Success box)
    # 5. rolling_risk_shift.png
    # 6. breakpoint_sensitivity.png
    # 7. oos_forecast_comparison.png
    # 8. zlb_tp_distribution.png

    images = [
        "outputs/observed_vs_fitted.png",
        "outputs/term_premium_decomp.png",
        "outputs/term_premium_surface.png",
        "outputs/benchmarking_acm_nber.png",
        "outputs/rolling_risk_shift.png",
        "outputs/breakpoint_sensitivity.png",
        "outputs/oos_forecast_comparison.png",
        "outputs/zlb_tp_distribution.png"
    ]

    def replacer(match):
        if images:
            img_path = images.pop(0)
            b64 = get_b64(img_path)
            if b64:
                print(f"Embedding {img_path}")
                return f'<img src="{b64}">'
            else:
                print(f"Skipping {img_path} (not found)")
                return match.group(0)
        return match.group(0)

    # src="" 패턴을 찾아서 순서대로 교체
    new_html = re.sub(r'<img src="">', replacer, html)
    
    # 이미 src가 차있는 경우 (oos_forecast_comparison.png 등) 처리
    if "outputs/oos_forecast_comparison.png" in new_html:
        b64_oos = get_b64("outputs/oos_forecast_comparison.png")
        new_html = new_html.replace('src="outputs/oos_forecast_comparison.png"', f'src="{b64_oos}"')

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("\n[SUCCESS] Targeted embedding complete.")

if __name__ == "__main__":
    embed_all()
