# 🏘️ 전국 시군구 생활SOC 현황 대시보드 v2

인터랙티브 지도와 함께하는 2015-2024 생활인프라 시설 및 인구 변화 분석 대시보드

## ✨ 주요 기능

- **인터랙티브 지도**: 시군구 클릭으로 상세정보 확인
- **지역유형 비교**: 전국 / 인구감소지역 / 비인구감소지역 탭
- **상세 정보 패널**: 기본정보, 시설현황, 주거현황, 통근현황
- **시계열 차트**: 인구밀도, 생활시설 변화 추이

## 📦 로컬 실행

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 실행
streamlit run app.py

# 3. 브라우저에서 확인
# http://localhost:8501
```

## 🚀 Streamlit Cloud 배포

### Step 1: GitHub 저장소 생성
1. https://github.com 접속 → 로그인
2. 오른쪽 상단 **+** → **New repository**
3. Repository name: `sgg-dashboard`
4. Public 선택 → **Create repository**

### Step 2: 파일 업로드
1. **Add file** → **Upload files**
2. 이 폴더의 모든 파일 드래그 & 드롭:
   - `app.py`
   - `requirements.txt`
   - `data/SGG_Full_Data_4326_tol100.geojson`
3. **Commit changes**

### Step 3: Streamlit Cloud 연결
1. https://share.streamlit.io 접속
2. **Sign in with GitHub**
3. **New app** 클릭
4. 설정:
   - Repository: `your-username/sgg-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
5. **Deploy!**

### Step 4: 완료! 🎉
- URL: `https://sgg-dashboard-yourusername.streamlit.app`

## 📁 프로젝트 구조

```
sgg_dashboard_v2/
├── app.py                              # 메인 앱
├── requirements.txt                    # 패키지 의존성
├── README.md                           # 설명서
└── data/
    └── SGG_Full_Data_4326_tol100.geojson  # 시군구 지오데이터
```

## 📊 데이터 필드

| 카테고리 | 필드 | 설명 |
|----------|------|------|
| 기본 | SIGUNGU_NM, SIDO_NM | 시군구/시도명 |
| 인구 | POP_YY, PDEN_YY | 인구, 인구밀도 |
| 시설 | LIV, MED, CARE, EDU, CUL, SPT | 6개 시설유형 |
| 주거 | HAPT, HDET, HMULTI, HROW | 주거유형별 가구수 |
| 통근 | COM_T_20, COM_A/T/O_P/T_20 | 통근시간, 수단별 |

---

Built with ❤️ by USDL @ SNU
