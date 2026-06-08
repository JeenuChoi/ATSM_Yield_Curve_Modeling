# ATSM 프로젝트 진행 상황 및 향후 계획

## 프로젝트 개요

나는 현재 **국채 수익률곡선(여러 만기 금리)**을 대상으로, **무차익(arbitrage-free) 조건을 만족하는 3요인 affine term structure model (ATSM)**을 구축하고, 이를 **state-space 형태로 표현한 뒤 Kalman filter / smoother와 MLE**를 이용해 추정하는 프로젝트를 진행 중이다.  

최종 목표는 다음과 같다.

1. 여러 만기의 국채 금리를 **3개의 잠재요인(latent factors)** 으로 설명한다.
2. 이 잠재요인들이 따르는 동학을 **affine Gaussian dynamics**로 설정한다.
3. 단기금리(short rate)를 상태변수의 affine function으로 두고,

\[
r_t = \delta_0 + \delta_1' X_t
\]

채권가격이

\[
P(t,\tau)=\exp(A(\tau)+B(\tau)'X_t)
\]

꼴을 따르도록 하여 **무차익 조건 하에서 모든 만기의 수익률을 일관되게 가격결정**한다.

4. 이를 상태공간모형으로 바꾸어 **Kalman filter 기반 likelihood**를 계산하고, **MLE**로 파라미터를 추정한다.
5. 추정된 결과를 이용해 **smoothed latent factors**를 복원하고, 관측수익률과 적합수익률을 비교하며 진단한다.
6. 마지막으로 장기금리를

\[
\text{yield} = \text{expected future short rates} + \text{term premium}
\]

으로 분해하여 **기간프리미엄(term premium)** 을 추정한다.
7. 실무적 난제인 **식별성(identification), 확률적 특이성(stochastic singularity), 위험가격(market price of risk) 추정 불안정성**은 단계적 설계로 통제한다.

---

# 1. 현재까지 이미 완료한 것

현재 나는 **ATSM의 추정 파이프라인 자체는 거의 완성**한 상태다.  
구체적으로는 아래 단계들이 이미 구현 및 실행 완료되었다.

---

## (1) 데이터 로딩 완료

- 로컬 파일 `feds200628_clean.csv`를 사용해 데이터 로딩 완료
- 데이터 shape는 `(434, 8)`로 확인됨
- 즉, **434개 시점, 8개 만기**의 국채 수익률 데이터 사용 중
- 데이터는 GSW 계열 국채 수익률 데이터로 이해하면 된다

주의:

- 날짜 파싱 경고가 있었음
- `pd.to_datetime(df['Date'])`에서 `%d/%m/%Y` 형식 관련 warning이 발생했으므로, 향후 재현성과 안정성을 위해 날짜 포맷을 명시하거나 `dayfirst=True`를 넣는 정리가 필요함
- 다만 현재 추정 자체는 성공적으로 수행되었음

---

## (2) Stage 1: PCA + VAR 기반 초기값 생성 완료

- PCA와 VAR 기반의 사전 추정(pre-estimation)을 통해 **초기 잠재요인과 초기 파라미터 후보값**을 생성함
- 측정오차 공분산행렬 \(R\) 에 대해 diagonal floor를 둔 상태에서 초기 추정 성공
- 로그상 `Estimated R diagonal (with floor)` 가 출력되었고, 초기 추정 및 bound 설정도 완료됨

이 단계의 의미:

- 바로 full MLE로 들어가지 않고,
- **초기값 문제와 비선형 최적화 불안정성**을 줄이기 위해
- PCA/VAR 기반으로 시작점을 잡는 구조를 이미 구축함

---

## (3) State-space model 구성 완료

이미 상태공간모형이 만들어져 있다.

### 상태방정식

잠재요인 \(X_t\)는 transition dynamics를 따름:

\[
X_{t+1} = \Phi X_t + c + \varepsilon_t, \qquad \varepsilon_t \sim N(0,Q)
\]

### 측정방정식

관측수익률 \(y_t\)는

\[
y_t = A + H X_t + \eta_t, \qquad \eta_t \sim N(0,R)
\]

형태로 구성되어 있음

여기서:

- \(H\) 는 만기별 factor loading matrix
- \(A\) 는 만기별 affine intercept
- \(R\) 은 measurement noise covariance
- \(Q\) 는 latent factor innovation covariance

로그에 `Phi`, `Q diag`, `R diag`, `H min/max`가 출력되었으므로, **최종 상태공간모형 조립까지 완료**되었다고 판단됨

---

## (4) Main optimization 완료

MLE 추정은 이미 완료되었다.

최적화는 2단계로 수행됨:

### 1단계: Global optimization

- `differential_evolution` 사용
- 최대 iteration은 작게 주어졌기 때문에 fully converge하지는 않았지만,
- negative log-likelihood를 크게 개선함

초기값:

- Initial Neg-LogLik: `-8548.29`

글로벌 탐색 후:

- Best Neg-LogLik: `-14856.11`

### 2단계: Local optimization

- `L-BFGS-B` 사용
- fine-tuning 수행
- 최종적으로 optimization success 판정

최종 결과:

- Best log likelihood: `15024.999...`
- filter loglik: `15045.312...`

즉,

- **Kalman filter likelihood 기반 MLE 추정 자체는 성공**
- global + local의 staged estimation도 이미 잘 동작함

---

## (5) 주요 파라미터 추정 완료

이미 다음 파라미터들이 추정되었다.

### \(K^Q\) (Mean Reversion Matrix)

\[
K^Q =
\begin{bmatrix}
0.0154 & 0 & 0\\
0.3628 & 0.6497 & 0\\
0.0388 & -0.3975 & 0.1654
\end{bmatrix}
\]

### \(\Sigma\) (Volatility Matrix)

하삼각 구조로 추정됨

### \(\theta^Q\) (Long-run Mean)

\[
\theta^Q = [0.000356,\ 0.053876,\ 0.026178]
\]

### \(\delta_0\)

\[
\delta_0 = 0.04676
\]

### \(\delta_1\)

\[
\delta_1 = [1.1060,\ 0.07175,\ -0.04963]
\]

### \(R\) (Observation Noise)

8개 만기에 대한 diagonal observation noise가 추정됨

즉,

- **short rate specification**
- **risk-neutral dynamics**
- **measurement error**
까지 모두 수치적으로 추정 완료됨

---

## (6) Kalman Filter / Smoother 실행 완료

최종 state-space model을 구축한 뒤,

- Kalman filter
- Kalman smoother

를 모두 실행했고,

다음 결과를 이미 확보했다:

- filtered likelihood
- smoothed latent factors
- fitted yields
- residuals / innovations

즉, **잠재요인 복원까지 완료**된 상태다.

---

## (7) 결과 플롯 생성 완료

현재 다음 그림들이 이미 생성되었다.

### Factor Loadings \(B(\tau)/\tau\)

- Factor 1: 전 만기에서 거의 일정 → **Level**
- Factor 2: 단기에서 크고 장기로 갈수록 0으로 수렴 → **Slope**
- Factor 3: hump shape → **Curvature**

즉, 모델이 **교과서적인 level-slope-curvature 구조를 잘 복원**했다.

### Observed vs Fitted Yields

- 1년, 7년, 30년 예시에서 observed와 fitted가 거의 겹침
- 시계열 적합도가 매우 높음

### Smoothed Latent Factors

- 3개 잠재요인의 시계열이 복원됨
- 경제적으로 해석 가능한 움직임을 보임

### Kalman Filter Residuals (Innovations) + ACF

- 잔차와 자기상관함수를 점검함
- 몇몇 만기에서 잔차의 약한 자기상관이 남아 있음

즉, **결과 해석과 기본 진단까지는 수행 완료**되었다.

---

## (8) Quick Diagnostics 완료

출력된 주요 진단값:

### \(\Phi\)

\[
\Phi =
\begin{bmatrix}
0.9987 & 0 & 0\\
-0.0294 & 0.9473 & 0\\
-0.0037 & 0.0320 & 0.9863
\end{bmatrix}
\]

해석:

- Factor 1은 매우 persistent
- Factor 2는 상대적으로 mean reversion이 강함
- Factor 3도 persistent하지만 Factor 1보다는 덜함

### \(Q\) Diagonal

- Factor 1 shock variance 매우 작음
- Factor 2, 3은 더 큰 변동성

### Fitted vs Observed Std

- 만기별 fitted yield 변동성과 observed yield 변동성이 거의 동일
- 모델이 시계열 변동성을 잘 재현

---

# 2. 현재까지 하지 않은 것

현재 프로젝트에서 **아직 핵심적으로 남아 있는 부분**은 아래다.

## (1) Physical Measure \(P\) Dynamics 추정

현재는 **risk-neutral \(Q\)-measure dynamics** 중심이다.

하지만 term premium decomposition을 위해서는

- \(K^P\)
- \(\theta^P\)
- market price of risk

가 필요하다.

---

## (2) Market Price of Risk 추정

다음 형태가 필요하다.

\[
\lambda(X_t)=\lambda_0+\lambda_1 X_t
\]

이를 통해

\[
K^P = K^Q + \Sigma \lambda_1
\]

같은 관계를 사용한다.

---

## (3) Expected Short Rate Path 계산

필요한 값:

\[
E_t^P[r_{t+1}], E_t^P[r_{t+2}], ..., E_t^P[r_{t+n}]
\]

---

## (4) Term Premium Decomposition

최종 분해:

\[
y_t^{(n)} = \frac{1}{n}\sum_{j=0}^{n-1} E_t^P[r_{t+j}] + TP_t^{(n)}
\]

현재는

- fitted yield는 있음
- term premium은 없음

---

## (5) Identification / Robustness 정리

추가 검토 필요:

- factor 수
- measurement error 구조
- risk price specification
- normalization 방식

---

# 3. 현재 프로젝트 위치

## 완료된 것

- 데이터 준비
- affine pricing 구조
- state-space model
- Kalman filter likelihood
- MLE 추정
- latent factor smoothing
- yield fitting
- diagnostics

## 아직 남은 것

- \(P\)-measure dynamics
- market price of risk
- expected short rate path
- term premium decomposition

---

# 4. 앞으로 진행 계획

## Step 1 — 현재 코드 구조 점검

- 현재 dynamics가 Q인지 P인지 확인

---

## Step 2 — P-dynamics 도입

\[
X_{t+1} = \mu^P + \Phi^P X_t + \varepsilon_{t+1}
\]

---

## Step 3 — Market Price of Risk 도입

\[
\lambda(X_t)=\lambda_0+\lambda_1 X_t
\]

---

## Step 4 — P와 Q 연결

\[
K^P = K^Q + \Sigma \lambda_1
\]

---

## Step 5 — Kalman Filter 수정

- transition: P
- measurement: Q

---

## Step 6 — Expected Short Rate 계산

\[
E_t^P[r_{t+j}]
\]

---

## Step 7 — Term Premium 계산

\[
TP_t^{(n)} = y_t^{(n)} - \frac{1}{n}\sum_{j=0}^{n-1} E_t^P[r_{t+j}]
\]

---

## Step 8 — 결과 검증

- 경기 국면 비교
- external benchmark 비교

---

## Step 9 — Robustness

- measurement error 구조
- factor 수 비교
- risk price restriction
- 초기값 민감도
- identification 정리

---

# 핵심 요약

현재 나는

- 3요인 무차익 ATSM 추정
- Kalman filter / smoother
- latent factor 복원
- yield fitting

까지 완료했다.

하지만 아직

- physical measure dynamics
- market price of risk
- expected short-rate path
- term premium decomposition

은 구현하지 않았다.

따라서 다음 단계는 **term premium estimation 단계**이다.