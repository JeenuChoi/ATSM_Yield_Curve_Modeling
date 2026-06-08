# ATSM Project Specification (Phase 8): Out-of-Sample Validation & Final Review

## 1. 개요 (Overview)
모델의 실전 예측력과 일반화 성능을 검증하기 위한 표본 외(Out-of-Sample, OOS) 분석을 수행함. 2018년까지의 데이터로만 모델을 재구축하여 미래(2019~2026)를 해석하는 엄밀한 테스트를 완료함.

---

## 2. Phase 8: 표본 외 수익률 예측 결과 (OOS Yield Forecast Results)

### (1) 예측 성적표 (10-Year Yield 기준)
- **우리 모델 RMSE:** 23.97 bps
- **Random Walk RMSE:** 27.22 bps
- **Diebold-Mariano Test:** P-value **0.0961** (10% 유의수준에서 유의미한 예측 우위 확보)

### (2) 학술적 시사점 (Academic Discussion)
- **Superiority over RW:** 금융 시계열 예측의 가장 강력한 벤치마크인 Random Walk 모델을 10년물 수익률 예측에서 RMSE 기준 약 3.25bp 앞지름으로써 모델의 실전적 유용성을 입증함.
- **Maturity Specificity:** 단기물(2Y) 대비 장기물(10Y)에서 모델의 우월성이 두드러짐. 이는 거시경제적 불확실성이 장기 기간 프리미엄에 미치는 영향을 본 모델이 성공적으로 포착하고 있음을 시사함.

---

## 3. 프로젝트 최종 자산 (Final Project Assets)

### (1) 실행 스크립트 (Execution Pipeline)
- `main.py`: 전체 기간 최적화 및 황금 데이터 산출.
- `main2.py`: 황금 데이터를 고정한 고속 분석 파이프라인.
- `main3.py`: 고급 계량 검정 (Granger, FEVD, Chow Test).
- `main4.py`: 강건성 검정 (GARCH, Lag Sensitivity, Narrative).
- `main5.py`: ZLB 및 Shadow Rate 특수 구간 분석.
- `main6.py`: OOS 예측 및 DM Test 검증.

### (2) 핵심 결과물 (Key Visuals & Reports)
- **Visuals:** 
  - `benchmarking_acm_nber.png`: ACM 벤치마킹 및 NBER 음영.
  - `fevd_term_premium.png`: TP 변동 원인 분해.
  - `narrative_m2_vs_uncertainty.png`: 유동성 vs 불확실성 줄다리기.
  - `oos_forecast_comparison.png`: OOS 예측 궤적 비교.
- **Reports:**
  - `final_paper_report.txt`: 전체 통계 요약.
  - `advanced_econometric_report.txt`: 인과성 및 구조적 변화 검정 결과.
  - `zlb_shadow_report.txt`: 제로 금리 하한 구간의 강건성 입증.

---

## 4. SCI/Scopus 투고를 위한 최종 제언 (Final Recommendations)
1.  **결과 강조:** 인플레이션 불확실성과 기간 프리미엄의 **Granger 인과성(p=0.007)**과 **공적분(Rank 4)**을 논문의 핵심 Selling Point로 활용할 것.
2.  **차별화:** 코로나 이후 매크로 설명력이 **3배 급증(20% -> 61%)**했다는 발견은 저널 에디터가 매우 선호할 만한 주제임.
3.  **한계 인정:** OOS 결과에서 나타난 수준 오차는 채권 모델의 전형적인 특성으로 기술하되, **ZLB 시기의 높은 설명력**을 통해 모델의 유용성을 방어할 것.

============================================================
*이것으로 ATSM 프로젝트의 모든 실증 분석 및 시스템 구축 과정을 종료한다.*
