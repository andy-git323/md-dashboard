import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =====================================================
# 1. 페이지 설정
# =====================================================
st.set_page_config(
    page_title="Store Progress Dashboard",
    page_icon="🏬",
    layout="wide"
)

# =====================================================
# 2. 매장 / 지역 설정
# =====================================================
STORE_ORDER = [f"매장 {i}" for i in range(1, 11)]
REGION_ORDER = ["A지역", "B지역", "C지역"]

STORE_REGION_MAP = {
    "매장 1": "A지역",
    "매장 2": "A지역",
    "매장 3": "A지역",
    "매장 4": "B지역",
    "매장 5": "B지역",
    "매장 6": "B지역",
    "매장 7": "C지역",
    "매장 8": "C지역",
    "매장 9": "C지역",
    "매장 10": "C지역",
}

REGION_COLOR_MAP = {
    "A지역": "#9CA3AF",
    "B지역": "#60A5FA",
    "C지역": "#F59E0B",
}

# =====================================================
# 3. 다크모드 스타일
# =====================================================
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }

    .title {
        font-size: 36px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 15px;
        color: #E5E7EB;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .kpi-card {
        background-color: #171B26;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #2A2F3A;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.25);
    }

    .kpi-label {
        font-size: 14px;
        color: #D1D5DB;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
    }

    .kpi-sub {
        font-size: 13px;
        color: #9CA3AF;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 4. 공통 함수
# =====================================================
def format_won(value):
    value = float(value)

    if abs(value) >= 100000000:
        return f"{value / 100000000:.1f}억"
    elif abs(value) >= 10000:
        return f"{value / 10000:.0f}만"
    else:
        return f"{value:,.0f}"


def format_pct(value):
    return f"{value * 100:.1f}%"


def kpi_card(label, value, sub_text=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)


def apply_dark_chart_style(fig, height=430, x_category_order=None):
    xaxis_config = dict(
        title=None,
        tickfont=dict(size=16, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    )

    if x_category_order is not None:
        xaxis_config.update({
            "categoryorder": "array",
            "categoryarray": x_category_order
        })

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(size=14, color="#FFFFFF"),
        xaxis=xaxis_config,
        yaxis=dict(
            tickfont=dict(size=14, color="#FFFFFF"),
            title_font=dict(size=15, color="#FFFFFF"),
            gridcolor="#262730",
            zerolinecolor="#262730"
        ),
        legend=dict(
            orientation="h",
            y=-0.18,
            font=dict(size=14, color="#FFFFFF")
        )
    )

    return fig

# =====================================================
# 5. 샘플 데이터 생성
# =====================================================
@st.cache_data
def create_sample_store_data():
    np.random.seed(42)

    today = datetime.today().date()
    start_date = today - timedelta(days=59)
    dates = pd.date_range(start=start_date, end=today, freq="D")

    data = []

    for store in STORE_ORDER:
        base_daily_target = np.random.randint(2_500_000, 8_000_000)

        for date in dates:
            weekday = date.weekday()

            if weekday in [5, 6]:
                target = base_daily_target * np.random.uniform(1.15, 1.35)
            else:
                target = base_daily_target * np.random.uniform(0.85, 1.05)

            actual = target * np.random.uniform(0.70, 1.25)

            visitors = int(np.random.randint(80, 350))
            purchase_count = int(visitors * np.random.uniform(0.12, 0.35))
            avg_price = actual / purchase_count if purchase_count > 0 else 0

            data.append({
                "일자": date,
                "지역": STORE_REGION_MAP[store],
                "매장": store,
                "일목표": int(target),
                "일매출": int(actual),
                "방문객수": visitors,
                "구매건수": purchase_count,
                "객단가": int(avg_price)
            })

    df = pd.DataFrame(data)
    df["일자"] = pd.to_datetime(df["일자"])
    df["주차"] = df["일자"].dt.strftime("%Y-W%U")
    df["월"] = df["일자"].dt.strftime("%Y-%m")
    df["요일"] = df["일자"].dt.day_name()

    return df


df = create_sample_store_data()

# =====================================================
# 6. 사이드바
# =====================================================
st.sidebar.title("⚙️ 조회 조건")

view_type = st.sidebar.radio(
    "조회 기준",
    ["일간", "주간", "월간"],
    horizontal=True
)

selected_regions = st.sidebar.multiselect(
    "지역 선택",
    REGION_ORDER,
    default=REGION_ORDER
)

store_list = [
    store for store in STORE_ORDER
    if STORE_REGION_MAP[store] in selected_regions
]

selected_stores = st.sidebar.multiselect(
    "매장 선택",
    store_list,
    default=store_list
)

if view_type == "일간":
    date_list = sorted(df["일자"].dt.date.unique())
    selected_date = st.sidebar.selectbox(
        "일자 선택",
        date_list,
        index=len(date_list) - 1
    )

elif view_type == "주간":
    week_list = sorted(df["주차"].unique())
    selected_week = st.sidebar.selectbox(
        "주차 선택",
        week_list,
        index=len(week_list) - 1
    )

else:
    month_list = sorted(df["월"].unique())
    selected_month = st.sidebar.selectbox(
        "월 선택",
        month_list,
        index=len(month_list) - 1
    )

# =====================================================
# 7. 데이터 필터링
# =====================================================
df_selected = df[
    (df["지역"].isin(selected_regions)) &
    (df["매장"].isin(selected_stores))
].copy()

if df_selected.empty:
    st.warning("선택된 지역/매장 데이터가 없습니다.")
    st.stop()

# =====================================================
# 8. 일간 / 주간 / 월간 집계
# =====================================================
if view_type == "일간":
    filtered = df_selected[df_selected["일자"].dt.date == selected_date]
    period_label = str(selected_date)
    target_col_name = "일목표"
    sales_col_name = "일매출"

elif view_type == "주간":
    filtered = df_selected[df_selected["주차"] == selected_week]
    period_label = selected_week
    target_col_name = "주간목표"
    sales_col_name = "주간매출"

else:
    filtered = df_selected[df_selected["월"] == selected_month]
    period_label = selected_month
    target_col_name = "월간목표"
    sales_col_name = "월간매출"

summary = filtered.groupby(["지역", "매장"], as_index=False).agg({
    "일목표": "sum",
    "일매출": "sum",
    "방문객수": "sum",
    "구매건수": "sum"
})

summary = summary.rename(columns={
    "일목표": target_col_name,
    "일매출": sales_col_name
})

summary["진도율"] = np.where(
    summary[target_col_name] > 0,
    summary[sales_col_name] / summary[target_col_name],
    0
)

summary["차이금액"] = summary[sales_col_name] - summary[target_col_name]

summary["객단가"] = np.where(
    summary["구매건수"] > 0,
    summary[sales_col_name] / summary["구매건수"],
    0
)

summary["전환율"] = np.where(
    summary["방문객수"] > 0,
    summary["구매건수"] / summary["방문객수"],
    0
)

summary["지역"] = pd.Categorical(
    summary["지역"],
    categories=REGION_ORDER,
    ordered=True
)

summary["매장"] = pd.Categorical(
    summary["매장"],
    categories=STORE_ORDER,
    ordered=True
)

summary = summary.sort_values(["지역", "매장"]).reset_index(drop=True)

# =====================================================
# 9. 헤더
# =====================================================
st.markdown('<div class="title">🏬 Store Target Progress Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">지역/매장별 {view_type} 목표 대비 진도율 · 기준: {period_label}</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 10. 전체 KPI
# =====================================================
total_target = summary[target_col_name].sum()
total_sales = summary[sales_col_name].sum()
total_gap = total_sales - total_target
total_progress = total_sales / total_target if total_target > 0 else 0
total_visitors = summary["방문객수"].sum()
total_purchase = summary["구매건수"].sum()
total_conversion = total_purchase / total_visitors if total_visitors > 0 else 0
total_avg_price = total_sales / total_purchase if total_purchase > 0 else 0

achieved_count = len(summary[summary["진도율"] >= 1])
risk_count = len(summary[summary["진도율"] < 0.8])

st.markdown('<div class="section-title">① 전체 현황</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(f"{view_type} 목표", format_won(total_target), "선택 지역/매장 기준")

with c2:
    kpi_card(f"{view_type} 매출", format_won(total_sales), f"차이 {format_won(total_gap)}")

with c3:
    kpi_card("목표 대비 진도율", format_pct(total_progress), f"달성 매장 {achieved_count}개")

with c4:
    kpi_card("위험 매장", f"{risk_count}개", "진도율 80% 미만")

c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card("방문객수", f"{total_visitors:,.0f}명")

with c6:
    kpi_card("구매건수", f"{total_purchase:,.0f}건")

with c7:
    kpi_card("전환율", format_pct(total_conversion))

with c8:
    kpi_card("객단가", format_won(total_avg_price))

# =====================================================
# 11. 지역별 목표 대비 진도율
# =====================================================
st.markdown('<div class="section-title">② 지역별 목표 대비 진도율</div>', unsafe_allow_html=True)

region_summary = summary.groupby("지역", as_index=False, observed=False).agg({
    target_col_name: "sum",
    sales_col_name: "sum",
    "방문객수": "sum",
    "구매건수": "sum"
})

region_summary["진도율"] = np.where(
    region_summary[target_col_name] > 0,
    region_summary[sales_col_name] / region_summary[target_col_name],
    0
)

region_summary["차이금액"] = region_summary[sales_col_name] - region_summary[target_col_name]

region_summary["객단가"] = np.where(
    region_summary["구매건수"] > 0,
    region_summary[sales_col_name] / region_summary["구매건수"],
    0
)

region_summary["전환율"] = np.where(
    region_summary["방문객수"] > 0,
    region_summary["구매건수"] / region_summary["방문객수"],
    0
)

region_summary["지역"] = pd.Categorical(
    region_summary["지역"],
    categories=REGION_ORDER,
    ordered=True
)

region_summary = region_summary.sort_values("지역").reset_index(drop=True)

r_left, r_right = st.columns([1.2, 1])

with r_left:
    fig_region = px.bar(
        region_summary,
        x="지역",
        y="진도율",
        text="진도율",
        color="지역",
        category_orders={"지역": REGION_ORDER},
        color_discrete_map=REGION_COLOR_MAP
    )

    fig_region.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside",
        textfont_size=22,
        textfont_color="#FFFFFF",
        width=0.42
    )

    fig_region.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="#FFFFFF",
        annotation_text="목표 100%",
        annotation_position="top left",
        annotation_font_color="#FFFFFF"
    )

    fig_region = apply_dark_chart_style(
        fig_region,
        height=380,
        x_category_order=REGION_ORDER
    )

    fig_region.update_layout(
        bargap=0.50,
        showlegend=False
    )

    fig_region.update_yaxes(
        title="진도율",
        tickformat=".0%"
    )

    st.plotly_chart(fig_region, use_container_width=True)

with r_right:
    region_display = region_summary.copy()

    region_display[target_col_name] = region_display[target_col_name].apply(format_won)
    region_display[sales_col_name] = region_display[sales_col_name].apply(format_won)
    region_display["진도율"] = region_display["진도율"].apply(format_pct)
    region_display["차이금액"] = region_display["차이금액"].apply(format_won)
    region_display["객단가"] = region_display["객단가"].apply(format_won)
    region_display["전환율"] = region_display["전환율"].apply(format_pct)

    st.dataframe(
        region_display[
            [
                "지역",
                target_col_name,
                sales_col_name,
                "진도율",
                "차이금액",
                "방문객수",
                "구매건수",
                "전환율",
                "객단가"
            ]
        ],
        use_container_width=True,
        height=380
    )

# =====================================================
# 12. 매장별 목표 대비 진도율
# =====================================================
st.markdown('<div class="section-title">③ 매장별 목표 대비 진도율</div>', unsafe_allow_html=True)

fig_progress = px.bar(
    summary,
    x="매장",
    y="진도율",
    text="진도율",
    color="지역",
    category_orders={
        "매장": STORE_ORDER,
        "지역": REGION_ORDER
    },
    color_discrete_map=REGION_COLOR_MAP
)

fig_progress.update_traces(
    texttemplate="%{text:.1%}",
    textposition="outside",
    textfont_size=20,
    textfont_color="#FFFFFF",
    width=0.42
)

fig_progress.add_hline(
    y=1.0,
    line_dash="dash",
    line_color="#FFFFFF",
    annotation_text="목표 100%",
    annotation_position="top left",
    annotation_font_color="#FFFFFF"
)

fig_progress = apply_dark_chart_style(
    fig_progress,
    height=430,
    x_category_order=STORE_ORDER
)

fig_progress.update_layout(
    bargap=0.50,
    legend_title_text="지역"
)

fig_progress.update_yaxes(
    title="진도율",
    tickformat=".0%"
)

st.plotly_chart(fig_progress, use_container_width=True)

# =====================================================
# 13. 매장별 목표 vs 매출
# =====================================================
st.markdown('<div class="section-title">④ 매장별 목표 vs 매출</div>', unsafe_allow_html=True)

fig_compare = go.Figure()

for region in REGION_ORDER:
    region_df = summary[summary["지역"] == region].copy()
    region_color = REGION_COLOR_MAP[region]

    fig_compare.add_trace(
        go.Bar(
            x=region_df["매장"],
            y=region_df[target_col_name],
            name=f"{region} 목표",
            marker_color=region_color,
            opacity=0.45,
            text=region_df[target_col_name],
            texttemplate="%{text:.2s}",
            textposition="outside",
            textfont=dict(size=15, color="#FFFFFF"),
            width=0.26,
            offsetgroup="목표"
        )
    )

    fig_compare.add_trace(
        go.Bar(
            x=region_df["매장"],
            y=region_df[sales_col_name],
            name=f"{region} 매출",
            marker_color=region_color,
            opacity=1.0,
            text=region_df[sales_col_name],
            texttemplate="%{text:.2s}",
            textposition="outside",
            textfont=dict(size=15, color="#FFFFFF"),
            width=0.26,
            offsetgroup="매출"
        )
    )

fig_compare.update_layout(
    barmode="group",
    bargap=0.42,
    bargroupgap=0.25,
    height=460,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(size=14, color="#FFFFFF"),
    xaxis=dict(
        title=None,
        tickfont=dict(size=16, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730",
        categoryorder="array",
        categoryarray=STORE_ORDER
    ),
    yaxis=dict(
        title="금액",
        tickfont=dict(size=14, color="#FFFFFF"),
        title_font=dict(size=15, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    ),
    legend=dict(
        orientation="h",
        y=-0.22,
        font=dict(size=13, color="#FFFFFF")
    )
)

st.plotly_chart(fig_compare, use_container_width=True)

# =====================================================
# 14. 매장별 상세 현황
# =====================================================
st.markdown('<div class="section-title">⑤ 매장별 상세 현황</div>', unsafe_allow_html=True)

display_summary = summary.copy()

display_summary[target_col_name] = display_summary[target_col_name].apply(format_won)
display_summary[sales_col_name] = display_summary[sales_col_name].apply(format_won)
display_summary["진도율"] = display_summary["진도율"].apply(format_pct)
display_summary["차이금액"] = display_summary["차이금액"].apply(format_won)
display_summary["객단가"] = display_summary["객단가"].apply(format_won)
display_summary["전환율"] = display_summary["전환율"].apply(format_pct)

st.dataframe(
    display_summary[
        [
            "지역",
            "매장",
            target_col_name,
            sales_col_name,
            "진도율",
            "차이금액",
            "방문객수",
            "구매건수",
            "전환율",
            "객단가"
        ]
    ],
    use_container_width=True,
    height=420
)

# =====================================================
# 15. 우수 매장 / 위험 매장
# =====================================================
st.markdown('<div class="section-title">⑥ 우수 매장 / 위험 매장</div>', unsafe_allow_html=True)

left, right = st.columns(2)

top_store = summary.sort_values("진도율", ascending=False).head(5)
risk_store = summary.sort_values("진도율", ascending=True).head(5)

with left:
    st.subheader("🏆 우수 매장 TOP 5")

    top_display = top_store.copy()
    top_display["진도율"] = top_display["진도율"].apply(format_pct)
    top_display[sales_col_name] = top_display[sales_col_name].apply(format_won)
    top_display["차이금액"] = top_display["차이금액"].apply(format_won)

    st.dataframe(
        top_display[["지역", "매장", sales_col_name, "진도율", "차이금액"]],
        use_container_width=True,
        height=260
    )

with right:
    st.subheader("⚠️ 위험 매장 TOP 5")

    risk_display = risk_store.copy()
    risk_display["진도율"] = risk_display["진도율"].apply(format_pct)
    risk_display[sales_col_name] = risk_display[sales_col_name].apply(format_won)
    risk_display["차이금액"] = risk_display["차이금액"].apply(format_won)

    st.dataframe(
        risk_display[["지역", "매장", sales_col_name, "진도율", "차이금액"]],
        use_container_width=True,
        height=260
    )

# =====================================================
# 16. 일자별 매출 추이
# =====================================================
st.markdown('<div class="section-title">⑦ 일자별 매출 추이</div>', unsafe_allow_html=True)

daily_trend = filtered.groupby("일자", as_index=False).agg({
    "일목표": "sum",
    "일매출": "sum"
})

daily_trend_long = daily_trend.melt(
    id_vars="일자",
    value_vars=["일목표", "일매출"],
    var_name="구분",
    value_name="금액"
)

fig_trend = px.line(
    daily_trend_long,
    x="일자",
    y="금액",
    color="구분",
    markers=True,
    color_discrete_map={
        "일목표": "#6B7280",
        "일매출": "#D1D5DB"
    }
)

fig_trend.update_traces(
    line=dict(width=3),
    marker=dict(size=8)
)

fig_trend = apply_dark_chart_style(fig_trend, height=390)

fig_trend.update_yaxes(title="금액")

st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# 17. 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑧ 데이터 다운로드</div>', unsafe_allow_html=True)

download_df = summary.copy()
csv = download_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 매장별 진도율 CSV 다운로드",
    data=csv,
    file_name=f"store_progress_{view_type}_{period_label}.csv",
    mime="text/csv"
)

# =====================================================
# 18. 안내
# =====================================================
with st.expander("📌 이 대시보드에서 보는 핵심"):
    st.markdown("""
    이 대시보드는 지역/매장별 목표 대비 진도율을 보는 용도입니다.

    주요 기능:
    - 일간 / 주간 / 월간 기준 선택
    - A지역 / B지역 / C지역 필터
    - 매장 1~10 순서 고정
    - 지역별 색상 구분
    - 지역에 속한 매장도 동일 색상 적용
    - 목표 vs 매출 그래프 옆 배치
    - 목표 달성 매장과 미달 매장 확인
    - 방문객수, 구매건수, 전환율, 객단가 확인
    - CSV 다운로드

    현재 지역 구분:
    - A지역: 매장 1, 2, 3
    - B지역: 매장 4, 5, 6
    - C지역: 매장 7, 8, 9, 10

    현재 색상 구분:
    - A지역: Gray
    - B지역: Blue
    - C지역: Orange
    """)