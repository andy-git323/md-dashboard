import streamlit as st

st.set_page_config(
    page_title="MD Allboard",
    page_icon="📦",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }

    .main-title {
        font-size: 42px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 8px;
    }

    .sub-title {
        font-size: 17px;
        color: #D1D5DB;
        margin-bottom: 32px;
    }

    .card {
        background-color: #171B26;
        padding: 24px;
        border-radius: 18px;
        border: 1px solid #2A2F3A;
        margin-bottom: 16px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 8px;
    }

    .card-text {
        font-size: 15px;
        color: #D1D5DB;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📦 MD Allboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">MD 업무를 위한 매장 · 상품 · 스케줄 · 플랜 대시보드</div>',
    unsafe_allow_html=True
)

st.divider()

st.markdown("""
<div class="card">
    <div class="card-title">🏬 Store Progress Dashboard</div>
    <div class="card-text">
        매장별 일간 · 주간 · 월간 목표 대비 진도율을 확인하는 페이지입니다.<br>
        지역별, 매장별 목표/매출/진도율을 볼 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="card-title">📦 Product Category Dashboard</div>
    <div class="card-text">
        상품 카테고리별 판매금액, 판매수량, 판매율, 할인율, 재고수량을 확인하는 페이지입니다.<br>
        CATE1 / CATE2 / CATE3 기준으로 상품 흐름을 볼 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="card-title">🧾 MD Plan Builder</div>
    <div class="card-text">
        연간 MD PLAN, 월별 매출 계획, 시즌/DROP 운영 계획을 구성하는 페이지입니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="card-title">📅 MD Schedule</div>
    <div class="card-text">
        26FW 시즌 일정, 상품 준비 일정, DROP 스케줄을 관리하는 페이지입니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.info("왼쪽 사이드바의 페이지 메뉴에서 원하는 대시보드를 선택하세요.")