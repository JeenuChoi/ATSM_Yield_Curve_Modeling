# ATSM Project Specification (Phase 6 & 7): Advanced Rigor & Economic Narrative

## 1. 개요 (Overview)
Phase 4~5의 검증 결과를 바탕으로, SCI/Scopus급 논문의 '기여도'를 극대화하기 위해 통계적 인과성 검정, 구조적 변화 실증, 그리고 거시경제적 내러티브(M2 vs 물가) 분석을 추가함.

---

## 2. Phase 6: 고급 계량경제 검정 (Advanced Econometrics)

### (1) Granger 인과관계 (Granger Causality)
- **발견:** 인플레이션 불확실성($p=0.0073$)과 물가 수준($p=0.0369$)이 기간 프리미엄을 통계적으로 유의미하게 **선행(Lead)**함.
- **의의:** 물가 리스크가 채권 시장의 위험 프리미엄을 결정하는 실질적인 원인임을 입증.

### (2) 분산 분해 (Variance Decomposition)
- **결과:** 기간 프리미엄 변동의 약 **14%**가 순수 매크로 충격에서 기인함.
- **기여도:** 실업률(4.7%), 물가 불확실성(3.8%), 물가 수준(3.2%) 순으로 기여함.

### (3) 구조적 단절 검정 (Chow Test)
- **검증:** 2020년 1월 기점 구조적 변화 확인 ($p < 0.0001$).
- **의의:** 팬데믹 이후 채권 시장의 작동 원리가 이전과 통계적으로 완전히 달라졌음을 확정.

---

## 3. Phase 7: 강건성 및 내러티브 (Robustness & Narrative)

### (1) 대체 변수 검정 (Alternative Proxy)
- **방법:** GARCH(1,1) 모형을 통해 추출한 물가 변동성과 기존 지표 비교.
- **결과:** 두 지표 간 상관관계 **0.5977** 확보. 지표 선정의 강건성 증명.

### (2) 시차 민감도 분석 (Lag Sensitivity)
- **방법:** VAR 시차를 3, 6, 12로 변경하며 IRF 일관성 확인.
- **결과:** 시차 설정에 관계없이 물가 충격에 대한 프리미엄의 양(+)의 반응이 유지됨을 확인.

### (3) 유동성 vs 불확실성 줄다리기 (Economic Narrative)
- **분석:** M2 증가율과 물가 불확실성이 기간 프리미엄에 미치는 영향력을 시계열 상관관계로 분석.
- **통찰:** 양적완화(M2)의 프리미엄 억제 효과가 인플레이션 불확실성에 의해 상쇄되는 동태적 과정을 시각화함.

---

## 4. 추가된 분석 자산 (New Assets)
- **Advanced Report:** `outputs/advanced_econometric_report.txt`
- **Robustness Report:** `outputs/robustness_report.txt`
- **New Visuals:** 
  - `fevd_term_premium.png`
  - `robustness_irf_lag_[3,6,12].png`
  - `narrative_m2_vs_uncertainty.png`

============================================================
*본 문서는 프로젝트의 학술적 깊이를 완성하고 투고 준비를 마치는 최종 단계의 기록이다.*
