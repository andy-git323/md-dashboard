import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================
# 1. PAGE SETTING
# =====================================================
st.set_page_config(
    page_title="MD Plan Builder",
    page_icon="🧾",
    layout="wide"
)

# =====================================================
# 2. STYLE
# =====================================================
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }

    .title {
        font-size: 38px;
        font-weight: 900;
        color: #FFFFFF !important;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 15px;
        color: #E5E7EB !important;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 850;
        color: #FFFFFF !important;
        margin-top: 28px;
        margin-bottom: 14px;
    }

    .kpi-card {
        background-color: #171B26 !important;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #2A2F3A !important;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.25);
        min-height: 120px;
    }

    .kpi-label {
        font-size: 14px;
        color: #D1D5DB !important;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 900;
        color: #FFFFFF !important;
    }

    .kpi-sub {
        font-size: 13px;
        color: #9CA3AF !important;
        margin-top: 8px;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }

    div[data-testid="stDataFrame"] {
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. FORMAT FUNCTIONS
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


def kpi_card(label, value, sub_text=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)


def apply_dark_chart_style(fig, height=430):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=30, b=30),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(size=14, color="#FFFFFF"),
        xaxis=dict(
            tickfont=dict(size=13, color="#E5E7EB"),
            title_font=dict(size=14, color="#FFFFFF"),
            gridcolor="#262730",
            zerolinecolor="#262730"
        ),
        yaxis=dict(
            tickfont=dict(size=13, color="#E5E7EB"),
            title_font=dict(size=14, color="#FFFFFF"),
            gridcolor="#262730",
            zerolinecolor="#262730"
        ),
        legend=dict(
            font=dict(size=12, color="#FFFFFF"),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.2
        )
    )
    return fig


# =====================================================
# 4. SIDEBAR SETTINGS
# =====================================================
st.sidebar.markdown("---")
st.sidebar.title("⚙️ MD PLAN 설정")

plan_year = st.sidebar.number_input(
    "계획 연도",
    min_value=2024,
    max_value=2030,
    value=2026,
    step=1
)

annual_target_sales = st.sidebar.number_input(
    "연간 목표 매출",
    min_value=100000000,
    max_value=10000000000,
    value=1000000000,
    step=10000000
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
    min_value=0.30,
    max_value=0.95,
    value=0.70,
    step=0.01
)

total_otb_budget = st.sidebar.number_input(
    "총 투입 예산 / OTB",
    min_value=100000000,
    max_value=5000000000,
    value=300000000,
    step=10000000
)

# =====================================================
# 5. DATA
# =====================================================
months = pd.date_range(
    start=f"{plan_year}-01-01",
    end=f"{plan_year}-12-01",
    freq="MS"
)

season_map = {
    1: "WINTER",
    2: "WINTER",
    3: "SPRING",
    4: "SPRING",
    5: "SUMMER",
    6: "SUMMER",
    7: "HOT SUMMER",
    8: "HOT SUMMER",
    9: "FALL",
    10: "FALL",
    11: "WINTER",
    12: "WINTER"
}

monthly_ratio = {
    1: 0.06,
    2: 0.06,
    3: 0.08,
    4: 0.08,
    5: 0.07,
    6: 0.07,
    7: 0.08,
    8: 0.08,
    9: 0.09,
    10: 0.10,
    11: 0.11,
    12: 0.12
}

drop_map = {
    1: "DROP1",
    2: "DROP1",
    3: "DROP2",
    4: "DROP2",
    5: "DROP2",
    6: "DROP3",
    7: "DROP3",
    8: "DROP3",
    9: "DROP4",
    10: "DROP4",
    11: "DROP4",
    12: "DROP4"
}

monthly_plan = pd.DataFrame({
    "월": [m.strftime("%Y-%m") for m in months],
    "월번호": [m.month for m in months]
})

monthly_plan["시즌"] = monthly_plan["월번호"].map(season_map)
monthly_plan["DROP"] = monthly_plan["월번호"].map(drop_map)
monthly_plan["월별비중"] = monthly_plan["월번호"].map(monthly_ratio)
monthly_plan["월별목표매출"] = monthly_plan["월별비중"] * annual_target_sales
monthly_plan["예상원가"] = monthly_plan["월별목표매출"] * (1 - target_margin_rate)
monthly_plan["목표판매수량"] = (monthly_plan["월별목표매출"] / 79000).round(0)

monthly_plan["주요 운영 포인트"] = monthly_plan["시즌"].map({
    "WINTER": "겨울 주력 상품 / 아우터 관리",
    "SPRING": "봄 상품 전환 / 간절기 아이템",
    "SUMMER": "여름 기본물 / 티셔츠 중심",
    "HOT SUMMER": "핫썸머 집중 / 시즌 소진",
    "FALL": "가을 신상품 / 재고 전환"
})

category_plan = pd.DataFrame({
    "카테고리": ["OUTER", "TOP", "BOTTOM", "GOODS", "BEAUTY"],
    "SKU수": [12, 35, 18, 20, 8],
    "평균판매가": [159000, 59000, 89000, 29000, 39000],
    "목표판매율": [0.62, 0.72, 0.68, 0.75, 0.70],
})

category_plan["예상매출"] = (
    category_plan["SKU수"]
    * category_plan["평균판매가"]
    * 500
    * category_plan["목표판매율"]
)

category_plan["예상원가"] = category_plan["예상매출"] * (1 - target_margin_rate)
category_plan["예상재고위험"] = np.where(
    category_plan["목표판매율"] < target_sell_through,
    "주의",
    "양호"
)

drop_plan = pd.DataFrame({
    "DROP": ["DROP1", "DROP2", "DROP3", "DROP4"],
    "운영월": ["1~2월", "3~5월", "6~8월", "9~12월"],
    "시즌": ["WINTER", "SPRING", "SUMMER/HOT", "FALL/WINTER"],
    "SKU수": [18, 25, 24, 26],
    "투입예산": [
        total_otb_budget * 0.18,
        total_otb_budget * 0.27,
        total_otb_budget * 0.25,
        total_otb_budget * 0.30
    ]
})

drop_plan["예상목표매출"] = drop_plan["투입예산"] / (1 - target_margin_rate)

# =====================================================
# 6. HEADER
# =====================================================
st.markdown('<div class="title">🧾 MD Plan Builder</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Annual Sales Plan · Season/DROP Calendar · Category SKU Plan · OTB Simulation</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 7. KPI
# =====================================================
st.markdown('<div class="section-title">① 연간 MD PLAN 요약</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("연간 목표 매출", format_won(annual_target_sales), f"{plan_year}년 기준")

with k2:
    kpi_card("목표 마진율", format_pct(target_margin_rate), "계획 기준")

with k3:
    kpi_card("목표 판매율", format_pct(target_sell_through), "시즌 평균 목표")

with k4:
    kpi_card("총 투입 예산 / OTB", format_won(total_otb_budget), "상품 운영 예산")

k5, k6, k7, k8 = st.columns(4)

with k5:
    kpi_card("월별목표 합계", format_won(monthly_plan["월별목표매출"].sum()), "연간 목표 대비")

with k6:
    kpi_card("총 SKU 수", f"{category_plan['SKU수'].sum():,.0f}개", "카테고리 기준")

with k7:
    kpi_card("예상 매출", format_won(category_plan["예상매출"].sum()), "SKU 계획 기준")

with k8:
    kpi_card("예상 원가", format_won(category_plan["예상원가"].sum()), "마진율 반영")

# =====================================================
# 8. MONTHLY PLAN
# =====================================================
st.markdown('<div class="section-title">② 월별 매출 계획</div>', unsafe_allow_html=True)

monthly_display = monthly_plan.copy()
monthly_display["월별비중"] = monthly_display["월별비중"].apply(format_pct)
monthly_display["월별목표매출"] = monthly_display["월별목표매출"].apply(format_won)
monthly_display["예상원가"] = monthly_display["예상원가"].apply(format_won)
monthly_display["목표판매수량"] = monthly_display["목표판매수량"].apply(lambda x: f"{x:,.0f}개")

st.dataframe(
    monthly_display[
        [
            "월",
            "시즌",
            "DROP",
            "월별비중",
            "월별목표매출",
            "예상원가",
            "목표판매수량",
            "주요 운영 포인트"
        ]
    ],
    use_container_width=True,
    height=430
)

# =====================================================
# 9. MONTHLY SALES CHART
# =====================================================
st.markdown('<div class="section-title">③ 월별 목표 매출 그래프</div>', unsafe_allow_html=True)

fig_monthly = go.Figure()

fig_monthly.add_trace(
    go.Bar(
        x=monthly_plan["월"],
        y=monthly_plan["월별목표매출"],
        name="월별 목표 매출",
        marker_color="#60A5FA",
        text=monthly_plan["월별목표매출"].apply(lambda x: f"{x/100000000:.1f}억"),
        textposition="outside"
    )
)

fig_monthly.update_yaxes(title="매출")
fig_monthly = apply_dark_chart_style(fig_monthly, height=430)

st.plotly_chart(fig_monthly, use_container_width=True)

# =====================================================
# 10. DROP TIMELINE
# =====================================================
st.markdown('<div class="section-title">④ 시즌 / DROP 운영 캘린더</div>', unsafe_allow_html=True)

timeline_y = {
    "DROP1": 4,
    "DROP2": 3,
    "DROP3": 2,
    "DROP4": 1
}

drop_colors = {
    "DROP1": "#60A5FA",
    "DROP2": "#818CF8",
    "DROP3": "#F59E0B",
    "DROP4": "#EF4444"
}

fig_timeline = go.Figure()

for _, row in monthly_plan.iterrows():
    fig_timeline.add_trace(
        go.Scatter(
            x=[row["월"]],
            y=[timeline_y[row["DROP"]]],
            mode="markers+text",
            marker=dict(
                size=28,
                color=drop_colors[row["DROP"]],
                line=dict(width=1, color="#FFFFFF")
            ),
            text=[row["DROP"]],
            textposition="top center",
            name=row["DROP"],
            showlegend=False
        )
    )

fig_timeline.update_yaxes(
    tickmode="array",
    tickvals=[1, 2, 3, 4],
    ticktext=["DROP4", "DROP3", "DROP2", "DROP1"],
    title=None
)

fig_timeline.update_xaxes(title=None)

fig_timeline = apply_dark_chart_style(fig_timeline, height=360)

st.plotly_chart(fig_timeline, use_container_width=True)

# =====================================================
# 11. CATEGORY PLAN
# =====================================================
st.markdown('<div class="section-title">⑤ 카테고리별 SKU / 매출 계획</div>', unsafe_allow_html=True)

category_display = category_plan.copy()
category_display["평균판매가"] = category_display["평균판매가"].apply(format_won)
category_display["목표판매율"] = category_display["목표판매율"].apply(format_pct)
category_display["예상매출"] = category_display["예상매출"].apply(format_won)
category_display["예상원가"] = category_display["예상원가"].apply(format_won)

st.dataframe(
    category_display[
        [
            "카테고리",
            "SKU수",
            "평균판매가",
            "목표판매율",
            "예상매출",
            "예상원가",
            "예상재고위험"
        ]
    ],
    use_container_width=True,
    height=300
)

c1, c2 = st.columns(2)

with c1:
    fig_sku = go.Figure()
    fig_sku.add_trace(
        go.Bar(
            x=category_plan["카테고리"],
            y=category_plan["SKU수"],
            name="SKU 수",
            marker_color="#F59E0B",
            text=category_plan["SKU수"],
            textposition="outside"
        )
    )
    fig_sku.update_yaxes(title="SKU 수")
    fig_sku = apply_dark_chart_style(fig_sku, height=380)
    st.plotly_chart(fig_sku, use_container_width=True)

with c2:
    fig_category_sales = go.Figure()
    fig_category_sales.add_trace(
        go.Bar(
            x=category_plan["카테고리"],
            y=category_plan["예상매출"],
            name="예상 매출",
            marker_color="#60A5FA",
            text=category_plan["예상매출"].apply(lambda x: f"{x/100000000:.1f}억"),
            textposition="outside"
        )
    )
    fig_category_sales.update_yaxes(title="예상 매출")
    fig_category_sales = apply_dark_chart_style(fig_category_sales, height=380)
    st.plotly_chart(fig_category_sales, use_container_width=True)

# =====================================================
# 12. DROP / OTB PLAN
# =====================================================
st.markdown('<div class="section-title">⑥ DROP별 OTB 계획</div>', unsafe_allow_html=True)

drop_display = drop_plan.copy()
drop_display["투입예산"] = drop_display["투입예산"].apply(format_won)
drop_display["예상목표매출"] = drop_display["예상목표매출"].apply(format_won)

st.dataframe(
    drop_display[
        [
            "DROP",
            "운영월",
            "시즌",
            "SKU수",
            "투입예산",
            "예상목표매출"
        ]
    ],
    use_container_width=True,
    height=260
)

fig_drop = go.Figure()

fig_drop.add_trace(
    go.Bar(
        x=drop_plan["DROP"],
        y=drop_plan["투입예산"],
        name="투입예산",
        marker_color="#818CF8",
        text=drop_plan["투입예산"].apply(lambda x: f"{x/100000000:.1f}억"),
        textposition="outside"
    )
)

fig_drop.update_yaxes(title="투입예산")
fig_drop = apply_dark_chart_style(fig_drop, height=380)

st.plotly_chart(fig_drop, use_container_width=True)

# =====================================================
# 13. MD COMMENT
# =====================================================
st.markdown('<div class="section-title">⑦ MD PLAN 자동 코멘트</div>', unsafe_allow_html=True)

top_month = monthly_plan.sort_values("월별목표매출", ascending=False).iloc[0]
top_category = category_plan.sort_values("예상매출", ascending=False).iloc[0]
risk_categories = category_plan[category_plan["예상재고위험"] == "주의"]

comments = [
    f"{plan_year}년 연간 목표 매출은 {format_won(annual_target_sales)}이며, 월별 계획 합계는 {format_won(monthly_plan['월별목표매출'].sum())}입니다.",
    f"월별 매출 계획에서 가장 큰 비중은 {top_month['월']}이며, 목표 매출은 {format_won(top_month['월별목표매출'])}입니다.",
    f"카테고리 기준 예상 매출이 가장 높은 영역은 {top_category['카테고리']}입니다.",
    f"현재 목표 판매율 {format_pct(target_sell_through)} 기준으로 주의가 필요한 카테고리는 {len(risk_categories)}개입니다.",
    "DROP별 예산은 시즌별 매출 비중과 상품 투입 시점을 기준으로 조정할 수 있습니다."
]

comment_lines = ""

for idx, comment in enumerate(comments, start=1):
    comment_lines += (
        f'<p style="color:#E5E7EB; font-size:15px; line-height:1.75; margin-bottom:12px;">'
        f'<b style="color:#FFFFFF;">{idx}.</b> {comment}'
        f'</p>'
    )

comment_box = (
    '<div style="'
    'background-color:#171B26; '
    'border:1px solid #2A2F3A; '
    'border-radius:18px; '
    'padding:22px 26px; '
    'margin-top:10px; '
    'margin-bottom:26px;'
    '">'
    f'{comment_lines}'
    '</div>'
)

st.markdown(comment_box, unsafe_allow_html=True)

# =====================================================
# 14. DOWNLOAD
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑧ 데이터 다운로드</div>', unsafe_allow_html=True)

download_df = pd.concat(
    [
        monthly_plan.assign(구분="월별계획"),
    ],
    ignore_index=True
)

csv = monthly_plan.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 월별 MD PLAN CSV 다운로드",
    data=csv,
    file_name=f"md_plan_monthly_{plan_year}.csv",
    mime="text/csv"
)

st.caption("MD Plan Builder · Annual MD Planning Dashboard")