import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE SETTING
# =====================================================
st.set_page_config(
    page_title="MD PLAN Builder",
    page_icon="🗓️",
    layout="wide"
)

# =====================================================
# STYLE
# =====================================================
st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }

    .title {
        font-size: 38px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 15px;
        color: #6B7280;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 800;
        color: #111827;
        margin-top: 28px;
        margin-bottom: 12px;
    }

    .kpi-card {
        background-color: white;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #E5E7EB;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
    }

    .kpi-label {
        font-size: 14px;
        color: #6B7280;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# FORMAT FUNCTIONS
# =====================================================
def format_won(value):
    try:
        value = float(value)
    except:
        return "0"

    if value >= 100000000:
        return f"{value / 100000000:.1f}억"
    elif value >= 10000:
        return f"{value / 10000:.0f}만"
    else:
        return f"{value:,.0f}"


def format_pct(value):
    try:
        return f"{float(value) * 100:.1f}%"
    except:
        return "0.0%"


def kpi_card(label, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# DEFAULT DATA
# =====================================================
def create_month_plan(year, annual_sales):
    months = [f"{year}-{str(i).zfill(2)}" for i in range(1, 13)]

    # 패션 브랜드 기준 예시 월별 비중
    ratios = [0.06, 0.06, 0.08, 0.08, 0.07, 0.07, 0.08, 0.08, 0.09, 0.10, 0.11, 0.12]

    df = pd.DataFrame({
        "월": months,
        "시즌": [
            "WINTER", "WINTER", "SPRING", "SPRING",
            "SUMMER", "SUMMER", "HOT SUMMER", "HOT SUMMER",
            "FALL", "FALL", "WINTER", "WINTER"
        ],
        "월별비중": ratios,
        "월별목표매출": [annual_sales * r for r in ratios],
        "주요운영": [
            "겨울 잔여 판매 / 신년 기획",
            "봄 상품 준비 / 겨울 소진",
            "SPRING DROP1",
            "SPRING DROP2",
            "SUMMER DROP1",
            "SUMMER DROP2",
            "HOT SUMMER / 티셔츠 집중",
            "간절기 준비",
            "FALL DROP1",
            "FALL DROP2",
            "WINTER DROP1",
            "WINTER DROP2 / 연말 집중"
        ]
    })

    return df


def create_drop_plan(year):
    df = pd.DataFrame({
        "DROP": ["DROP1", "DROP2", "DROP3", "DROP4"],
        "시즌": ["SPRING", "SUMMER", "FALL", "WINTER"],
        "런칭월": [f"{year}-03", f"{year}-06", f"{year}-09", f"{year}-11"],
        "콘셉트": [
            "첫 시즌 이미지 구축 / 기본 착장",
            "가벼운 소재 / 티셔츠 / 굿즈 확장",
            "간절기 레이어드 / 스타일링 강화",
            "아우터 / 선물 수요 / 객단가 상승"
        ],
        "핵심카테고리": [
            "TOP / BOTTOM / LIGHT OUTER",
            "TOP / GOODS",
            "OUTER / TOP / BOTTOM",
            "OUTER / KNIT / GOODS"
        ],
        "목표역할": [
            "브랜드 인지도 형성",
            "판매량 확보",
            "스타일 완성도 강화",
            "매출과 마진 극대화"
        ]
    })

    return df


def create_category_plan():
    df = pd.DataFrame({
        "카테고리": ["OUTER", "TOP", "BOTTOM", "GOODS", "BEAUTY"],
        "SKU수": [12, 35, 18, 20, 8],
        "평균판매가": [129000, 49000, 79000, 29000, 19000],
        "예상판매수량": [3000, 12000, 6000, 10000, 5000],
        "원가율": [0.45, 0.38, 0.42, 0.35, 0.30],
        "메모": [
            "시즌 매출 핵심 / 리스크 높음",
            "초기 볼륨 확보용",
            "착장 완성도 강화",
            "AOV 상승 / 팬덤형 상품",
            "저원가 테스트 카테고리"
        ]
    })

    return df


# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("⚙️ MD PLAN 설정")

plan_year = st.sidebar.number_input(
    "계획 연도",
    min_value=2025,
    max_value=2035,
    value=2026,
    step=1
)

annual_sales_target = st.sidebar.number_input(
    "연간 목표 매출",
    min_value=0,
    value=1_000_000_000,
    step=10_000_000
)

target_margin_rate = st.sidebar.slider(
    "목표 마진율",
    min_value=0.10,
    max_value=0.80,
    value=0.48,
    step=0.01
)

target_sell_through = st.sidebar.slider(
    "목표 판매율",
    min_value=0.10,
    max_value=1.00,
    value=0.70,
    step=0.01
)

total_budget = st.sidebar.number_input(
    "총 투입 예산 / OTB",
    min_value=0,
    value=300_000_000,
    step=10_000_000
)

st.sidebar.divider()
st.sidebar.caption("초기 버전은 샘플 구조로 시작하고, 나중에 ERP/엑셀 양식과 연결하면 됨.")


# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="title">🗓️ MD PLAN Builder</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Annual Sales Plan · Season/DROP Calendar · Category SKU Plan · OTB Simulation</div>',
    unsafe_allow_html=True
)

st.divider()


# =====================================================
# 1. OVERVIEW
# =====================================================
st.markdown('<div class="section-title">① 연간 MD PLAN 요약</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("연간 목표 매출", format_won(annual_sales_target))

with col2:
    kpi_card("목표 마진율", format_pct(target_margin_rate))

with col3:
    kpi_card("목표 판매율", format_pct(target_sell_through))

with col4:
    kpi_card("총 투입 예산", format_won(total_budget))


# =====================================================
# 2. MONTHLY SALES PLAN
# =====================================================
st.markdown('<div class="section-title">② 월별 매출 계획</div>', unsafe_allow_html=True)

month_plan_default = create_month_plan(plan_year, annual_sales_target)

month_plan = st.data_editor(
    month_plan_default,
    use_container_width=True,
    num_rows="dynamic",
    key="month_plan_editor",
    column_config={
        "월별비중": st.column_config.NumberColumn(
            "월별비중",
            format="%.2f"
        ),
        "월별목표매출": st.column_config.NumberColumn(
            "월별목표매출",
            format="%d"
        )
    }
)

month_plan["월별목표매출"] = pd.to_numeric(month_plan["월별목표매출"], errors="coerce").fillna(0)
month_plan["월별비중"] = pd.to_numeric(month_plan["월별비중"], errors="coerce").fillna(0)

monthly_total = month_plan["월별목표매출"].sum()
monthly_ratio_total = month_plan["월별비중"].sum()

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("월별 목표 합계", format_won(monthly_total))

with m2:
    st.metric("연간 목표 대비", format_pct(monthly_total / annual_sales_target if annual_sales_target > 0 else 0))

with m3:
    st.metric("월별 비중 합계", f"{monthly_ratio_total:.2f}")


fig_month = px.bar(
    month_plan,
    x="월",
    y="월별목표매출",
    color="시즌",
    text="월별목표매출",
    title=None
)

fig_month.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside",
    textfont_size=12
)

fig_month.update_layout(
    height=420,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(size=14),
    xaxis=dict(title=None, tickfont=dict(size=14)),
    yaxis=dict(title="목표매출", tickfont=dict(size=13)),
    legend=dict(orientation="h", y=-0.2)
)

st.plotly_chart(fig_month, use_container_width=True)


# =====================================================
# 3. DROP CALENDAR
# =====================================================
st.markdown('<div class="section-title">③ 시즌 / DROP 캘린더</div>', unsafe_allow_html=True)

drop_plan_default = create_drop_plan(plan_year)

drop_plan = st.data_editor(
    drop_plan_default,
    use_container_width=True,
    num_rows="dynamic",
    key="drop_plan_editor"
)

# DROP 타임라인 느낌 차트
drop_count = drop_plan.groupby("런칭월", as_index=False).size()
drop_count.columns = ["런칭월", "DROP수"]

fig_drop = px.scatter(
    drop_plan,
    x="런칭월",
    y="시즌",
    size=[35] * len(drop_plan),
    color="DROP",
    hover_data=["콘셉트", "핵심카테고리", "목표역할"],
    title=None
)

fig_drop.update_layout(
    height=360,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(size=14),
    xaxis=dict(title=None, tickfont=dict(size=14)),
    yaxis=dict(title=None, tickfont=dict(size=14)),
    legend=dict(orientation="h", y=-0.2)
)

st.plotly_chart(fig_drop, use_container_width=True)


# =====================================================
# 4. CATEGORY SKU PLAN
# =====================================================
st.markdown('<div class="section-title">④ 카테고리별 SKU / 매출 계획</div>', unsafe_allow_html=True)

category_plan_default = create_category_plan()

category_plan = st.data_editor(
    category_plan_default,
    use_container_width=True,
    num_rows="dynamic",
    key="category_plan_editor",
    column_config={
        "SKU수": st.column_config.NumberColumn("SKU수", min_value=0, step=1),
        "평균판매가": st.column_config.NumberColumn("평균판매가", min_value=0, step=1000),
        "예상판매수량": st.column_config.NumberColumn("예상판매수량", min_value=0, step=100),
        "원가율": st.column_config.NumberColumn("원가율", min_value=0.0, max_value=1.0, step=0.01, format="%.2f")
    }
)

category_plan["SKU수"] = pd.to_numeric(category_plan["SKU수"], errors="coerce").fillna(0)
category_plan["평균판매가"] = pd.to_numeric(category_plan["평균판매가"], errors="coerce").fillna(0)
category_plan["예상판매수량"] = pd.to_numeric(category_plan["예상판매수량"], errors="coerce").fillna(0)
category_plan["원가율"] = pd.to_numeric(category_plan["원가율"], errors="coerce").fillna(0)

category_plan["예상매출"] = category_plan["평균판매가"] * category_plan["예상판매수량"]
category_plan["예상원가"] = category_plan["예상매출"] * category_plan["원가율"]
category_plan["예상마진"] = category_plan["예상매출"] - category_plan["예상원가"]
category_plan["예상마진율"] = np.where(
    category_plan["예상매출"] > 0,
    category_plan["예상마진"] / category_plan["예상매출"],
    0
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card("총 SKU 수", f"{category_plan['SKU수'].sum():,.0f}개")

with c2:
    kpi_card("예상 매출", format_won(category_plan["예상매출"].sum()))

with c3:
    kpi_card("예상 원가", format_won(category_plan["예상원가"].sum()))

with c4:
    total_expected_sales = category_plan["예상매출"].sum()
    total_expected_margin = category_plan["예상마진"].sum()
    expected_margin_rate = total_expected_margin / total_expected_sales if total_expected_sales > 0 else 0
    kpi_card("예상 마진율", format_pct(expected_margin_rate))


left, right = st.columns([1.2, 1])

with left:
    fig_category = px.bar(
        category_plan,
        x="카테고리",
        y="예상매출",
        text="예상매출",
        color="카테고리"
    )

    fig_category.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont_size=12
    )

    fig_category.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=14),
        xaxis=dict(title=None, tickfont=dict(size=16)),
        yaxis=dict(title="예상매출", tickfont=dict(size=13)),
        showlegend=False
    )

    st.plotly_chart(fig_category, use_container_width=True)

with right:
    display_category = category_plan.copy()
    display_category["평균판매가"] = display_category["평균판매가"].apply(format_won)
    display_category["예상매출"] = display_category["예상매출"].apply(format_won)
    display_category["예상원가"] = display_category["예상원가"].apply(format_won)
    display_category["예상마진"] = display_category["예상마진"].apply(format_won)
    display_category["원가율"] = display_category["원가율"].apply(format_pct)
    display_category["예상마진율"] = display_category["예상마진율"].apply(format_pct)

    st.dataframe(
        display_category[
            ["카테고리", "SKU수", "평균판매가", "예상판매수량", "원가율", "예상매출", "예상마진", "예상마진율"]
        ],
        use_container_width=True,
        height=420
    )


# =====================================================
# 5. OTB / BUDGET PLAN
# =====================================================
st.markdown('<div class="section-title">⑤ OTB / 예산 시뮬레이션</div>', unsafe_allow_html=True)

category_plan["예산비중"] = np.where(
    category_plan["예상원가"].sum() > 0,
    category_plan["예상원가"] / category_plan["예상원가"].sum(),
    0
)

category_plan["권장예산배분"] = total_budget * category_plan["예산비중"]
category_plan["예산차이"] = category_plan["권장예산배분"] - category_plan["예상원가"]

budget_display = category_plan[[
    "카테고리", "예상원가", "예산비중", "권장예산배분", "예산차이"
]].copy()

budget_display["예상원가"] = budget_display["예상원가"].apply(format_won)
budget_display["예산비중"] = budget_display["예산비중"].apply(format_pct)
budget_display["권장예산배분"] = budget_display["권장예산배분"].apply(format_won)
budget_display["예산차이"] = budget_display["예산차이"].apply(format_won)

b_left, b_right = st.columns([1, 1])

with b_left:
    fig_budget = px.pie(
        category_plan,
        names="카테고리",
        values="권장예산배분",
        hole=0.45
    )

    fig_budget.update_layout(
        height=390,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="white",
        font=dict(size=14),
        legend=dict(orientation="h", y=-0.1)
    )

    st.plotly_chart(fig_budget, use_container_width=True)

with b_right:
    st.dataframe(
        budget_display,
        use_container_width=True,
        height=390
    )


# =====================================================
# 6. MD ACTION MEMO
# =====================================================
st.markdown('<div class="section-title">⑥ MD 전략 메모</div>', unsafe_allow_html=True)

memo_1 = st.text_area(
    "브랜드 / 시즌 방향",
    value="이미지 중심의 시즌 DROP 운영. 초기에는 TOP/GOODS로 진입장벽을 낮추고, FW에 OUTER로 객단가를 높인다.",
    height=100
)

memo_2 = st.text_area(
    "상품 운영 전략",
    value="SKU는 초기에 과도하게 늘리지 않고, 반응 상품 중심으로 리오더/컬러 추가를 검토한다.",
    height=100
)

memo_3 = st.text_area(
    "리스크 / 체크포인트",
    value="OUTER는 원가와 재고 리스크가 높으므로 FW 전 판매 반응 데이터를 보고 수량을 조정한다.",
    height=100
)


# =====================================================
# 7. DOWNLOAD EXCEL
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑦ MD PLAN 다운로드</div>', unsafe_allow_html=True)

def to_excel(month_plan, drop_plan, category_plan, memo_df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        month_plan.to_excel(writer, index=False, sheet_name="월별매출계획")
        drop_plan.to_excel(writer, index=False, sheet_name="DROP캘린더")
        category_plan.to_excel(writer, index=False, sheet_name="카테고리SKU계획")
        memo_df.to_excel(writer, index=False, sheet_name="MD전략메모")

    return output.getvalue()


memo_df = pd.DataFrame({
    "구분": ["브랜드/시즌 방향", "상품 운영 전략", "리스크/체크포인트"],
    "내용": [memo_1, memo_2, memo_3]
})

excel_data = to_excel(month_plan, drop_plan, category_plan, memo_df)

st.download_button(
    label="📥 MD PLAN 엑셀 다운로드",
    data=excel_data,
    file_name=f"MD_PLAN_{plan_year}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


# =====================================================
# FOOTER GUIDE
# =====================================================
with st.expander("📌 이 대시보드의 목적"):
    st.markdown("""
    이 대시보드는 실적 분석용이 아니라 **연간 MD PLAN 작성용**입니다.

    주요 목적:
    - 연간 매출 목표를 월별로 배분
    - 시즌 / DROP 운영 캘린더 작성
    - 카테고리별 SKU 수와 예상 매출 설계
    - 원가율과 마진율 시뮬레이션
    - OTB / 예산 배분 검토
    - 최종 MD PLAN 엑셀 다운로드

    다음 단계에서는 여기에 아래 기능을 추가할 수 있습니다.

    - 월별 SKU 상세 계획
    - 상품별 원가 / 판매가 / 수량 계획
    - 시즌별 입고 스케줄
    - 생산 리드타임 관리
    - 실제 ERP 실적과 PLAN 비교
    - PPT 보고서 자동 생성
    """)