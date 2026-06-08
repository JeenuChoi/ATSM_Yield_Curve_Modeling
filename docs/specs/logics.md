# ATSM Project Logic & Publication Roadmap (Phase 4)

## 1. 프로젝트의 근본적 목표 (Core Objective)
본 프로젝트의 1차적 목표는 **무차익 Affine Term Structure Model (ATSM)**을 구축하여 미국 국채 수익률 곡선을 **Level, Slope, Curvature**라는 3개의 잠재요인으로 분해하고, 최종적으로 각 만기별 수익률에서 **기간 프리미엄(Term Premium, TP)**을 정밀하게 추출하는 것이었습니다.

- **Phase 1:** Q-measure(가격 결정 동학) 기반의 3요인 모델 구축 및 Kalman Filter-MLE 추정 프로세스 완성.
- **Phase 2:** P-measure(실제 시장 동학)와 Market Price of Risk($\lambda_t$) 추정을 통한 기간 프리미엄 분해 성공.
- **Phase 3:** 추출된 기간 프리미엄과 매크로 변수(물가 불확실성 등) 간의 상관관계 분석 및 자동화 파이프라인 구축.

---

## 2. 현재 구현 상태 (Current Status)
- **추정 엔진:** PCA/VAR 기반 초기값 생성부터 Global(DE) + Local(L-BFGS-B) MLE 최적화까지 이어지는 견고한 추정 파이프라인 보유.
- **분해 로직:** 연속 시간 적분 공식을 활용하여 '기대 단기금리 경로'와 '기간 프리미엄'을 수학적으로 정확히 분리.
- **매크로 통합:** FRED API 연동, 로컬 데이터 캐싱, 5개 핵심 매크로 지표(CPI, UNRATE, M2, INDPRO, INF_UNCERTAIN) 통합 분석 완료.
- **시각화:** 3D Surface Plot을 포함한 전 만기(1~30년) 시각화 및 자동 리포트 생성 기능 탑재.

---

## 3. SCI / Scopus급 논문 등재를 위한 고도화 전략 (The Gap)
단순한 모델 추정을 넘어 학술적 가치를 인정받기 위해 반드시 보완해야 할 요소들입니다.

### (1) 계량경제학적 엄밀성 (Econometric Rigor)
현재의 단순 OLS 회귀분석은 잔차의 자기상관(Durbin-Watson 0.03 수준) 문제로 인해 통계적 신뢰도가 낮습니다.
- **단위근 및 공적분 검정:** 수준 변수(Level)들의 불안정성(Non-stationarity)을 확인하고, 필요시 차분(Difference) 또는 VECM(Vector Error Correction Model) 도입.
- **VAR / VEC 모형 전환:** 단순 회귀가 아닌 매크로 변수와 TP 간의 동태적 상호작용을 분석하는 VAR 모형 구축.
- **충격반응함수(IRF):** 물가 불확실성 충격이 기간 프리미엄에 미치는 시차별 영향력을 시각화하여 경제적 파급효과 증명.

### (2) 국면 전환 분석의 고도화 (Regime-Switching Analysis)
임의의 코로나 날짜(2020년 1월)로 데이터를 자르는 것은 학술적으로 약점이 될 수 있습니다.
- **NBER Recession 분석:** 공식적인 경기 침체기 더미 변수를 활용한 분석.
- **Markov-Switching Model:** 데이터가 스스로 고물가/저물가, 고변동성/저변동성 체제(Regime)를 찾아내도록 하여, 각 체제별로 기간 프리미엄의 결정 요인이 어떻게 바뀌는지 분석.

### (3) 제로 금리 하한(ZLB) 및 섀도우 레이트(Shadow Rate) 논의
2008년~2015년 등 금리가 0% 근처에 머물렀던 시기는 일반적인 Gaussian 모델로 설명하기 어렵습니다.
- **ZLB 처리:** 현재 모델의 한계를 명시하거나, Kim-Wright(2005) 또는 Krippner(2013) 식의 Shadow Rate 개념을 도입하여 ZLB 시기의 프리미엄 왜곡을 보정했음을 강조.

### (4) 벤치마킹 및 교차 검증 (Benchmarking)
우리가 추출한 TP가 학계에서 널리 쓰이는 데이터와 얼마나 일치하는지 보여주어야 합니다.
- **ACM TP 비교:** 뉴욕 연준(NY Fed)에서 제공하는 Adrian, Crump, and Moench (2013)의 기간 프리미엄 데이터와 우리의 추출 결과 간의 상관관계 제시.
- **Wright (2011) 등 선행 연구:** 인플레이션 불확실성이 프리미엄을 높인다는 기존 문헌과의 결과 비교 및 차별점 부각.

### (5) 예측력 테스트 (Out-of-Sample Forecasting)
- **In-sample Fit vs. Out-of-sample Forecast:** 우리가 발견한 매크로 변수들이 미래의 기간 프리미엄이나 채권 수익률을 실제로 더 잘 예측하는지(RMSE, Diebold-Mariano Test) 검증. 저널 에디터들이 가장 선호하는 섹션 중 하나입니다.

---

## 4. 향후 액션 아이템 (Next Steps)
1. **VAR 분석 모듈 추가:** `src/analysis/econometrics.py`를 생성하여 단위근 검정 및 VAR 모형 구현.
2. **벤치마크 데이터 확보:** NY Fed의 ACM 기간 프리미엄 데이터를 가져와 우리 결과와 비교하는 코드 작성.
3. **ZLB 시기 분석 제외/포함 테스트:** ZLB 시기를 제외했을 때 매크로-TP 관계가 더 뚜렷해지는지 확인.
4. **논문 초고 작성:** 현재까지의 방법론(Methodology)과 결과(Results)를 바탕으로 LaTeX 또는 Markdown 기반 초고 작성 시작.

============================================================
*본 문서는 프로젝트의 학술적 완성도를 높이기 위한 가이드라인으로 활용됩니다.*
