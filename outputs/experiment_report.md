# ATSM Research & Experiment Methodology Report

본 문서는 미국 국채 수익률 곡선을 Level, Slope, Curvature의 3요인으로 분해하고, 기간 프리미엄(Term Premium)을 추출하여 매크로 변수와의 관계를 분석한 실험 방법론을 기술한다.

## 1. 연구 목적 (Objective)
- **무차익 Affine Term Structure Model (ATSM)**을 구축하여 정밀한 기간 프리미엄 추출.
- 추출된 기간 프리미엄과 매크로 변수(물가 불확실성, 통화량 등) 간의 동태적 상호작용 규명.
- 글로벌 벤치마크(NY Fed ACM)와의 비교를 통한 모델의 타당성 검증 및 포스트 코로나 시대의 구조적 변화 분석.

## 2. 데이터 구성 (Data Source)
- **수익률 데이터 (Yields):** Gurkaynak, Sack, and Wright (GSW) 데이터셋.
  - 만기: 1, 2, 3, 5, 7, 10, 20, 30년물 (8개 만기).
  - 기간: 1990-01-31 ~ 2026-02-28 (월말 기준).
- **매크로 데이터 (Macro):** FRED API 연동 지표.
  - INDPRO (산업생산), M2 (통화량), CPI (물가), UNRATE (실업률).
  - **INF_UNCERTAIN:** CPI 월간 변화율의 12개월 이동 표준편차로 산출된 물가 불확실성.
- **경기 사이클:** NBER Recession Indicator (USREC).
- **벤치마크:** NY Fed ACM 10Y Term Premium (로컬 CSV 참조).

## 3. 모델 프레임워크 (Model Framework)

### 3.1. ATSM 구조
- **상태공간모형 (State-Space Model):**
  - **전이 방정식 (Transition):** $X_t = \mu^P + \Phi^P X_{t-1} + \Sigma \epsilon_t$
  - **관측 방정식 (Measurement):** $Y_t = A(n) + B(n) X_t + e_t$
- **무차익 제약 (No-Arbitrage):** 위험의 시장 가격(Market Price of Risk) $\lambda_t = \lambda_0 + \lambda_1 X_t$를 도입하여 $P$(실제)와 $Q$(가격결정) 측도를 연결.

### 3.2. 기간 프리미엄 분해 (Decomposition)
- **Yield = Expected Short Rate Path + Term Premium**
- **기대 경로:** $P$-measure 동학 하에서 만기까지의 평균 단기 금리 기대치 적분.
- **기간 프리미엄:** 관측된 수익률과 기대 경로의 차이로 정의.

## 4. 계량경제학적 검증 (Econometric Rigor)

### 4.1. 단위근 및 공적분 검정
- **ADF Test:** 기간 프리미엄의 비정상성(Non-stationarity) 확인.
- **Johansen Cointegration:** 기간 프리미엄과 매크로 변수 간의 장기 균형 관계(Rank 4) 확인.

### 4.2. 동태적 분석 (VAR & VECM)
- **VAR (Vector Autoregression):** 1차 차분 데이터를 사용하여 단기적 충격 반응(IRF) 분석. Durbin-Watson 지수를 2.0 수준으로 개선하여 가짜 회귀(Spurious Regression) 방지.
- **VECM (Vector Error Correction Model):** 공적분 관계를 반영하여 장기 균형으로의 회복 과정을 모델링.

## 5. 주요 실험 결과 (Core Findings)

### 5.1. 기간 프리미엄의 합리성
- **10년물 평균:** 34.9bp (양수 구간 확보).
- **벤치마크 일치성:** NY Fed ACM 모델과 **0.9757**의 상관관계 달성 (부호 보정 후).

### 5.2. 구조적 변화 (Post-COVID Shift)
- 코로나 이전 대비 코로나 이후 매크로 변수의 설명력(R-squared)이 **20%에서 61%로 급증**.
- 특히 **인플레이션 불확실성**이 프리미엄 상승의 지배적 요인임을 입증.

### 5.3. 경기 침체 효과 (Flight-to-Safety)
- NBER 경기 침체기 동안 기간 프리미엄이 평균 **12.4bp 하락**.
- 이는 경제 위기 시 안전 자산(장기 국채) 선호에 따른 수요 폭증 현상을 실증적으로 포착한 결과임.

### 5.4. 표본 외 예측력 (Out-of-Sample Forecasting)
- **분석 방법:** 2018년까지의 데이터로 모델을 재추정하고, 2019~2026년 수익률을 1-step ahead 방식으로 예측.
- **주요 성과 (10Y Yield):**
  - **Model RMSE (23.97 bps) < Random Walk RMSE (27.22 bps)**
  - **Diebold-Mariano Test:** p-value = **0.0961**
- **결론:** 금융 시계열의 난제인 Random Walk 모델을 장기물 예측에서 유의미하게(10% 수준) 앞지름으로써 모델의 실전적 우수성을 검증함.

## 6. 통계적 유효성 가이드
- 모든 모델 잔차의 Durbin-Watson 지수가 1.9~2.1 사이에 위치하여 자기상관 문제 해결됨.
- IRF 신뢰구간 분석을 통해 물가 불확실성 충격의 지속성을 통계적으로 유의미하게 확인.

============================================================
*본 보고서는 ATSM 프로젝트의 최종 학술적 성과를 정리한 문서이다.*
