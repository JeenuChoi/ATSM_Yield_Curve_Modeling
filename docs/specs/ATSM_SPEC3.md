# ATSM 프로젝트 진행 상황 및 매크로 확장 계획 (Phase 3)

## 1. 현재까지 완료된 사항 (Status Quo)

### (1) 모델 추정 및 분해 완료
- **3요인 ATSM 모델 구축:** $Q$-measure(가격결정)와 $P$-measure(실제동학)를 모두 포함하는 상태공간모형 완성.
- **정규화(Identification):** 학술적 정석에 따라 $\theta^Q = 0$으로 고정하고, Nelson-Siegel 스타일의 $K^Q$ 제약을 통해 Level, Slope, Curvature 요인을 명확히 분리함.
- **성공적 수렴:** Log-Likelihood 약 14,500대 확보, 관측오차(R) $10^{-6}$ 수준의 정밀한 피팅 달성.
- **기간 프리미엄 분해:** 연속 시간 적분 공식을 사용하여 '기대 단기금리 경로'와 '기간 프리미엄(TP)'을 성공적으로 분해. (TP 양수화 및 2020년 COVID 충격 반영 확인)

### (2) 시스템 인프라
- **자동 보고서 생성:** `outputs/final_paper_report.txt` 및 각종 통계 CSV(`stats_factors.csv` 등) 자동 산출.
- **시각화 자동화:** 요인 로딩, 피팅 결과, 잠재 요인 시계열, 기간 프리미엄 분해 그래프를 PNG로 자동 저장.

---

## 2. 매크로 확장 계획 (Ongoing: Phase 3)

### (1) 분석 주제: "Inflation Uncertainty vs. Term Premium"
- **가설:** 물가 '수준'보다 물가 '불확실성(변동성)'이 장기 금리의 기간 프리미엄을 결정하는 핵심 변수이다.
- **대상 지표:** INDPRO(산업생산), RSAFS(소매판매), M2SL(통화량), CPIAUCSL(물가), UNRATE(실업률), HOUST(주택착공).

### (2) 기술적 준비 상태
- **`src/data/macro_loader.py`:** FRED 데이터를 긁어와 월말(Month-End)로 정렬하고 물가 불확실성(Rolling Std)을 계산하는 로직 구현 완료.
- **`macro_analysis.py`:** 채권 TP 데이터와 매크로 데이터를 병합하고, 공표 시차(Lag)를 반영한 상관관계 분석 및 시각화 로직 구현 완료.

---

## 3. 향후 과제 (Next Steps)

### (1) 데이터 확보 및 병합 (Immediate Task)
- 현재 FRED API 차단 이슈로 인해 매크로 데이터를 직접 확보하거나 로더 수정 필요.
- 확보된 데이터를 `outputs/term_premiums.csv`와 결합하여 `outputs/macro_tp_merged.csv` 생성.

### (2) 정식 회귀 분석
- 기간 프리미엄을 종속변수로, 매크로 변수(Level & Uncertainty)를 독립변수로 하는 다중 회귀 분석 수행.
- COVID 시기 전후의 구조적 변화(Regime Change) 테스트.

### (3) 논문 작성 및 결론 도출
- "연준의 통화정책 기대(Expected Rate)"와 "시장 불확실성(TP)"의 상호작용을 중심으로 2020년대 금리 변동성 설명.

---

## 4. 핵심 코드 위치
- **Main Pipeline:** `main.py`
- **P-measure & Risk Price:** `src/model/parameterization.py`
- **TP Decomposition:** `src/analysis/term_premium.py`
- **Macro Analysis:** `macro_analysis.py` & `src/data/macro_loader.py`

============================================================
*본 문서는 다음 세션에서 프로젝트를 이어서 진행하기 위한 가이드라인으로 작성되었습니다.*
