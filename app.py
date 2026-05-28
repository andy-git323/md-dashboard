<<<<<<< HEAD
import streamlit as st

st.set_page_config(page_title="MD 대시보드", layout="wide")

# 사이드바 메뉴
st.sidebar.title("📦 MD 대시보드")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "🏠 홈",
        "📅 26FW 스케줄",
        "🏪 매장 진도율",
        "📦 카테고리 분석",
        "📋 MD 플랜 빌더",
    ]
)

if menu == "🏠 홈":
    st.title("📦 MD 대시보드")
    st.markdown("---")
    st.subheader("안녕하세요! 👋")
    st.write("왼쪽 메뉴에서 원하는 대시보드를 선택해주세요.")

    col1, col2 = st.columns(2)
    with col1:
        st.info("📅 **26FW 스케줄**\n\n발주·입고 일정 및 카테고리별 진행 현황")
        st.info("📦 **카테고리 분석**\n\n상품 카테고리별 판매금액·수량 분석")
    with col2:
        st.info("🏪 **매장 진도율**\n\n지역·매장별 목표 대비 매출 진도율")
        st.info("📋 **MD 플랜 빌더**\n\n시즌별 MD 업무 단계 체크리스트")

elif menu == "📅 26FW 스케줄":
    exec(open("md_schedule.py", encoding="utf-8").read())

elif menu == "🏪 매장 진도율":
    exec(open("store_progress_dashboard.py", encoding="utf-8").read())

elif menu == "📦 카테고리 분석":
    exec(open("product_category_dashboard.py", encoding="utf-8").read())

elif menu == "📋 MD 플랜 빌더":
=======
import streamlit as st

st.set_page_config(page_title="MD 대시보드", layout="wide")

# 사이드바 메뉴
st.sidebar.title("📦 MD 대시보드")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "🏠 홈",
        "📅 26FW 스케줄",
        "🏪 매장 진도율",
        "📦 카테고리 분석",
        "📋 MD 플랜 빌더",
    ]
)

if menu == "🏠 홈":
    st.title("📦 MD 대시보드")
    st.markdown("---")
    st.subheader("안녕하세요! 👋")
    st.write("왼쪽 메뉴에서 원하는 대시보드를 선택해주세요.")

    col1, col2 = st.columns(2)
    with col1:
        st.info("📅 **26FW 스케줄**\n\n발주·입고 일정 및 카테고리별 진행 현황")
        st.info("📦 **카테고리 분석**\n\n상품 카테고리별 판매금액·수량 분석")
    with col2:
        st.info("🏪 **매장 진도율**\n\n지역·매장별 목표 대비 매출 진도율")
        st.info("📋 **MD 플랜 빌더**\n\n시즌별 MD 업무 단계 체크리스트")

elif menu == "📅 26FW 스케줄":
    exec(open("md_schedule.py", encoding="utf-8").read())

elif menu == "🏪 매장 진도율":
    exec(open("store_progress_dashboard.py", encoding="utf-8").read())

elif menu == "📦 카테고리 분석":
    exec(open("product_category_dashboard.py", encoding="utf-8").read())

elif menu == "📋 MD 플랜 빌더":
    exec(open("md_plan_builder.py", encoding="utf-8").read())