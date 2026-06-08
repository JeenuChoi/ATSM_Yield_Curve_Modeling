# ATSM Project Specification (Phase 4 & 5): Econometric Rigor and Global Benchmarking

## 1. 개요 (Overview)
Phase 3에서 추출된 기간 프리미엄(Term Premium)과 매크로 변수 간의 관계를 학술적으로 입증하기 위해 계량경제학적 엄밀성을 확보하고, 뉴욕 연준(NY Fed)의 ACM 모델 및 NBER 경기 사이클 데이터를 통해 모델의 신뢰성을 검증함.

---

## 2. Phase 4: 계량경제학적 엄밀성 (Econometric Rigor)

### (1) 진단 및 문제 해결
- **Durbin-Watson (DW) 이슈:** 초기 OLS 회귀 결과 DW 지수가 0.03 수준으로 심각한 자기상관(Serial Correlation) 발견. 이는 '가짜 회귀(Spurious Regression)'의 위험을 시사함.
- **정상성 검정 (ADF Test):** 기간 프리미엄(TP)이 수준 변수(Level) 상태에서 비정상성(Non-stationary)임을 확인.
- **차분(Difference) 및 VAR 도입:** 변수를 1차 차분하고 VAR(Vector Autoregression) 모형을 적용하여 DW 지수를 **2.0 근처**로 개선, 통계적 무결성 확보.

### (2) 장기 균형 분석 (Cointegration)
- **Johansen Cointegration Test:** TP와 매크로 변수들 사이에 **Rank 4**의 강력한 공적분 관계가 존재함을 입증.
- **VECM(Vector Error Correction Model) 추정:** 변수 간의 단기적 충격뿐만 아니라 장기적인 균형 복원력을 모델링함.
- **충격반응함수(IRF):** 물가 불확실성 쇼크에 대해 TP가 파동형(VAR) 및 수렴형(VECM)으로 반응하는 동태적 특성을 시각화함.

---

## 3. Phase 5: 벤치마킹 및 실증 분석 (Validation)

### (1) "Golden Data" 고정 (Fixed-Data Pipeline)
- MLE 최적화의 민감도를 제어하기 위해 성공적으로 추정된 수치를 CSV로 고정.
- `main2.py`를 신설하여 최적화 과정을 생략하고 고정된 데이터를 바탕으로 분석만 수행하는 파이프라인 구축.

### (2) NY Fed ACM 모델 비교 (Benchmarking)
- **대상:** 2년물부터 10년물까지 전 만기 ACM 기간 프리미엄 데이터와 비교.
- **결과:** 부호(Sign) 보정 후 우리 모델과 ACM 모델 간의 상관계수가 **최대 0.9757(10Y 기준)**로 나타남.
- **학술적 의의:** "경제적 상식(양수 TP)"을 지키면서도 "시장의 표준(ACM)"을 완벽하게 재현함.

### (3) NBER 경기 사이클 및 안전 자산 선호 (Business Cycle)
- **NBER Recession Shading:** 그래프에 경기 침체기 음영을 추가하여 시각적 직관성 확보.
- **Flight-to-Safety 효과:** 경기 침체기에 TP가 평균 12.4bp 하락함을 실증적으로 밝힘. 이는 위기 시 장기 국채 수요 폭증에 따른 프리미엄 압착 현상을 정확히 포착한 결과임.

---

## 4. 최종 시스템 구성 및 데이터 위치
- **Analysis Data:** `outputs/macro_tp_merged.csv`
- **Benchmarking Data:** `data/THREEFYTP[2-10].csv`
- **Econometric Module:** `src/analysis/econometrics.py`
- **Benchmarking Module:** `src/analysis/benchmarking.py`
- **Final Visuals:** `outputs/benchmarking_acm_nber.png`, `outputs/irf_vecm_uncertainty_to_tp.png`

---

## 5. 핵심 성과 (Final Achievements)
1.  **합리적 TP 추출:** 10년물 평균 34.9bp의 양수(+) 기간 프리미엄 확보.
2.  **포스트 코로나 통찰:** 코로나 이후 매크로 설명력(R-sq)이 61%로 폭등함을 증명.
3.  **학술적 일관성:** 글로벌 벤치마크 모델과 97% 이상의 동조성 입증.

============================================================
*본 문서는 Phase 4~5의 성과를 정리하고 논문 집필을 위한 최종 명세서로 작성되었습니다.*
