import streamlit as st

# =====================================================
# 1. 페이지 설정
# =====================================================
st.set_page_config(
    page_title="MD Allboard",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# 2. 스타일
# =====================================================
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }

    .main-title {
        font-size: 44px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 8px;
        letter-spacing: -0.8px;
    }

    .main-subtitle {
        font-size: 17px;
        color: #D1D5DB;
        margin-bottom: 28px;
        line-height: 1.6;
    }

    .section-title {
        font-size: 25px;
        font-weight: 850;
        color: #FFFFFF;
        margin-top: 28px;
        margin-bottom: 14px;
    }

    .card {
        background-color: #171B26;
        padding: 24px;
        border-radius: 18px;
        border: 1px solid #2A2F3A;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.25);
        margin-bottom: 18px;
        min-height: 180px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 850;
        color: #FFFFFF;
        margin-bottom: 10px;
    }

    .card-text {
        font-size: 15px;
        color: #D1D5DB;
        line-height: 1.65;
    }

    .tag {
        display: inline-block;
        background-color: #263244;
        color: #E5E7EB;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 12px;
        margin-right: 6px;
        margin-top: 10px;
    }

    .notice-box {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 20px;
        color: #D1D5DB;
        font-size: 15px;
        line-height: 1.7;
        margin-bottom: 16px;
    }

    .step-box {
        background-color: #171B26;
        border-left: 5px solid #60A5FA;
        padding: 18px 20px;
        border-radius: 12px;
        color: #D1D5DB;
        margin-bottom: 12px;
        font-size: 15px;
        line-height: 1.6;
    }

    .small-text {
        color: #9CA3AF;
        font-size: 13px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. 헤더
# =====================================================
st.markdown('<div class="main-title">📊 MD Allboard</div>', unsafe_allow_html=True)
st.markdown("""
<div class="main-subtitle">
MD 업무 데이터를 빠르게 업로드하고, 상품 · 매장 · 시즌 계획을 한 화면에서 분석하기 위한 대시보드입니다.<br>
ERP에서 다운로드한 엑셀 데이터를 업로드하면, 일간 · 주간 · 월간 기준으로 분석할 수 있습니다.
</div>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# 4. 대시보드 안내
# =====================================================
st.markdown('<div class="section-title">① 대시보드 구성</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-title">📦 Product Category Dashboard</div>
        <div class="card-text">
            상품 카테고리별 판매 현황을 분석하는 페이지입니다.<br><br>
            - CATE1 / CATE2 / CATE3 기준 분석<br>
            - 판매금액 / 판매수량 확인<br>
            - 상품별 BEST / WORST 확인<br>
            - 입고수량, 판매율, 할인율, 재고수량 확인<br>
            - 상품 분석 리포트 엑셀 다운로드 가능
        </div>
        <span class="tag">상품 MD</span>
        <span class="tag">카테고리 분석</span>
        <span class="tag">엑셀 업로드</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-title">🏬 Store Progress Dashboard</div>
        <div class="card-text">
            매장별 목표 대비 진도율을 분석하는 페이지입니다.<br><br>
            - 일간 / 주간 / 월간 기준 전환<br>
            - 지역별 목표 대비 진도율 확인<br>
            - 매장별 목표 / 매출 / 차이금액 확인<br>
            - 방문객수, 구매건수, 전환율, 객단가 확인<br>
            - 우수 매장 / 위험 매장 확인
        </div>
        <span class="tag">매장 관리</span>
        <span class="tag">목표 대비</span>
        <span class="tag">진도율</span>
    </div>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="card">
        <div class="card-title">🧾 MD Plan Builder</div>
        <div class="card-text">
            연간 MD 계획과 시즌 운영 계획을 구성하는 페이지입니다.<br><br>
            - 연간 목표 구조 설계<br>
            - 월별 / 시즌별 계획 구성<br>
            - DROP 운영 계획 정리<br>
            - 상품 운영 방향을 시각적으로 검토
        </div>
        <span class="tag">MD PLAN</span>
        <span class="tag">시즌 계획</span>
        <span class="tag">DROP</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="card">
        <div class="card-title">📅 MD Schedule</div>
        <div class="card-text">
            시즌 일정과 상품 준비 일정을 관리하는 페이지입니다.<br><br>
            - 시즌별 주요 일정 확인<br>
            - DROP 일정 관리<br>
            - 기획 / 생산 / 입고 / 판매 일정 흐름 확인<br>
            - MD 업무 스케줄 정리
        </div>
        <span class="tag">스케줄</span>
        <span class="tag">시즌 운영</span>
        <span class="tag">일정 관리</span>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 5. 사용 방법
# =====================================================
st.markdown('<div class="section-title">② 기본 사용 방법</div>', unsafe_allow_html=True)

st.markdown("""
<div class="step-box">
<b>STEP 1.</b> 왼쪽 사이드바에서 원하는 대시보드를 선택합니다.<br>
예: product category dashboard / store progress dashboard
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-box">
<b>STEP 2.</b> 각 대시보드의 사이드바에서 업로드 양식을 다운로드합니다.<br>
양식에 맞춰 ERP 다운로드 데이터를 정리하면 됩니다.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-box">
<b>STEP 3.</b> 엑셀 또는 CSV 파일을 업로드합니다.<br>
업로드 파일이 없으면 샘플 데이터 기준으로 화면이 표시됩니다.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-box">
<b>STEP 4.</b> 일간 / 주간 / 월간 기준을 선택하고, 필요한 필터를 적용합니다.<br>
필터에 따라 그래프와 표가 자동으로 변경됩니다.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-box">
<b>STEP 5.</b> 필요한 경우 분석 결과를 엑셀 또는 CSV로 다운로드합니다.<br>
보고서 작성이나 추가 분석에 활용할 수 있습니다.
</div>
""", unsafe_allow_html=True)

# =====================================================
# 6. 업로드 데이터 안내
# =====================================================
st.markdown('<div class="section-title">③ 업로드 데이터 안내</div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    st.markdown("""
    <div class="notice-box">
        <b>📦 상품 대시보드 필수 컬럼</b><br><br>
        일자<br>
        CATE1<br>
        CATE2<br>
        CATE3<br>
        상품명<br>
        TAG가<br>
        입고수량<br>
        판매수량<br>
        판매금액<br>
        할인율
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="notice-box">
        <b>🏬 매장 대시보드 필수 컬럼</b><br><br>
        일자<br>
        지역<br>
        매장<br>
        일목표<br>
        일매출<br>
        방문객수<br>
        구매건수
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 7. 보안 안내
# =====================================================
st.markdown('<div class="section-title">④ 데이터 보안 안내</div>', unsafe_allow_html=True)

st.markdown("""
<div class="notice-box">
    현재 업로드 방식은 <b>사용자별 세션에서 파일을 읽어 분석하는 구조</b>입니다.<br><br>
    - 업로드한 파일은 GitHub에 저장되지 않습니다.<br>
    - 업로드한 파일은 다른 사용자에게 자동 공유되지 않습니다.<br>
    - 각 사용자는 본인이 업로드한 파일 기준으로만 분석 화면을 확인합니다.<br>
    - 실제 회사 ERP 데이터는 GitHub에 올리지 않아야 합니다.<br><br>
    향후 회사 내부 공유형으로 확장할 경우, 관리자 업로드 방식이나 사내 서버 / ERP / DB 연동 방식으로 발전시킬 수 있습니다.
</div>
""", unsafe_allow_html=True)

# =====================================================
# 8. 현재 개발 단계
# =====================================================
st.markdown('<div class="section-title">⑤ 현재 개발 단계</div>', unsafe_allow_html=True)

st.markdown("""
<div class="notice-box">
    <b>현재 버전</b><br>
    - 상품 대시보드 업로드 기능 완료<br>
    - 매장 대시보드 업로드 기능 완료<br>
    - 업로드 양식 다운로드 기능 완료<br>
    - 업로드 데이터 미리보기 기능 완료<br>
    - 상품 분석 리포트 다운로드 기능 완료<br><br>

    <b>다음 고도화 후보</b><br>
    - 업로드 오류 메시지 개선<br>
    - 실제 ERP 컬럼명 자동 변환<br>
    - 공통 함수 utils 폴더 분리<br>
    - 관리자 업로드 / 공유형 데이터 구조 검토<br>
    - 사내 서버 또는 ERP 직접 연결 구조 검토
</div>
""", unsafe_allow_html=True)

st.caption("MD Allboard · 실무형 MD 데이터 분석 대시보드")