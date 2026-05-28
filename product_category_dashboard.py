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
    page_title="Product Category Dashboard",
    page_icon="📦",
    layout="wide"
)

# =====================================================
# 2. 카테고리 설정
# =====================================================
CATE1_ORDER = ["APP", "ACC"]

CATE2_ORDER = [
    "OUTER", "INNER", "BOTTOM",
    "CAP", "BAG", "SHOES", "ETC"
]

CATE2_TO_CATE1 = {
    "OUTER": "APP",
    "INNER": "APP",
    "BOTTOM": "APP",
    "CAP": "ACC",
    "BAG": "ACC",
    "SHOES": "ACC",
    "ETC": "ACC",
}

CATE3_MAP = {
    "OUTER": ["JACKET", "COAT", "JUMPER", "CARDIGAN"],
    "INNER": ["T-SHIRT", "SHIRT", "KNIT", "HOODIE"],
    "BOTTOM": ["PANTS", "DENIM", "SKIRT", "SHORTS"],
    "CAP": ["BALL CAP", "BUCKET HAT", "BEANIE"],
    "BAG": ["BACKPACK", "TOTE BAG", "CROSS BAG"],
    "SHOES": ["SNEAKERS", "SANDAL", "BOOTS"],
    "ETC": ["SOCKS", "KEYRING", "POUCH", "ACC ETC"],
}

CATE3_ORDER = []
for cate2 in CATE2_ORDER:
    CATE3_ORDER.extend(CATE3_MAP[cate2])

CATE1_COLOR_MAP = {
    "APP": "#60A5FA",
    "ACC": "#F59E0B",
}

CATE2_COLOR_MAP = {
    "OUTER": "#3B82F6",
    "INNER": "#60A5FA",
    "BOTTOM": "#93C5FD",
    "CAP": "#F59E0B",
    "BAG": "#FBBF24",
    "SHOES": "#F97316",
    "ETC": "#9CA3AF",
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


def format_qty(value):
    return f"{value:,.0f}개"


def format_pct(value):
    return f"{value * 100:.1f}%"


def format_million_label(value):
    value = float(value)
    if value <= 0:
        return ""
    return f"{value / 1_000_000:.0f}M"


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
        tickfont=dict(size=15, color="#FFFFFF"),
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
            y=-0.22,
            font=dict(size=13, color="#FFFFFF")
        )
    )

    return fig


# =====================================================
# 5. 샘플 상품 데이터 생성
# =====================================================
@st.cache_data
def create_sample_product_data():
    np.random.seed(42)

    today = datetime.today().date()
    start_date = today - timedelta(days=89)
    dates = pd.date_range(start=start_date, end=today, freq="D")

    data = []

    for cate2 in CATE2_ORDER:
        cate1 = CATE2_TO_CATE1[cate2]
        cate3_list = CATE3_MAP[cate2]

        for cate3 in cate3_list:
            for i in range(1, 6):
                item_code = f"{cate2[:2]}-{cate3[:2]}-{i:03d}"
                item_name = f"{cate3} ITEM {i}"

                tag_price = np.random.choice([
                    19000, 29000, 39000, 49000, 69000,
                    89000, 129000, 159000, 199000
                ])

                inbound_qty = np.random.randint(250, 1500)

                for date in dates:
                    if cate1 == "APP":
                        base_qty = np.random.randint(2, 18)
                    else:
                        base_qty = np.random.randint(1, 14)

                    if date.weekday() in [5, 6]:
                        qty = int(base_qty * np.random.uniform(1.2, 1.8))
                    else:
                        qty = int(base_qty * np.random.uniform(0.7, 1.2))

                    qty = max(qty, 0)

                    discount_rate = np.random.choice(
                        [0, 0.05, 0.1, 0.15, 0.2],
                        p=[0.45, 0.2, 0.2, 0.1, 0.05]
                    )

                    selling_price = int(tag_price * (1 - discount_rate))
                    sales_amount = qty * selling_price

                    data.append({
                        "일자": date,
                        "CATE1": cate1,
                        "CATE2": cate2,
                        "CATE3": cate3,
                        "상품코드": item_code,
                        "상품명": item_name,
                        "TAG가": tag_price,
                        "입고수량": inbound_qty,
                        "판매수량": qty,
                        "판매금액": sales_amount,
                        "실판매가": selling_price,
                        "할인율": discount_rate
                    })

    df = pd.DataFrame(data)

    df["일자"] = pd.to_datetime(df["일자"])
    df["주차"] = df["일자"].dt.strftime("%Y-W%U")
    df["월"] = df["일자"].dt.strftime("%Y-%m")
    df["요일"] = df["일자"].dt.day_name()

    df["CATE1"] = pd.Categorical(df["CATE1"], categories=CATE1_ORDER, ordered=True)
    df["CATE2"] = pd.Categorical(df["CATE2"], categories=CATE2_ORDER, ordered=True)
    df["CATE3"] = pd.Categorical(df["CATE3"], categories=CATE3_ORDER, ordered=True)

    return df


df = create_sample_product_data()

# =====================================================
# 6. 사이드바 필터
# =====================================================
st.sidebar.title("⚙️ 조회 조건")

view_type = st.sidebar.radio(
    "조회 기준",
    ["일간", "주간", "월간"],
    horizontal=True
)

selected_cate1 = st.sidebar.multiselect(
    "CATE1 선택",
    CATE1_ORDER,
    default=CATE1_ORDER
)

available_cate2 = [
    cate2 for cate2 in CATE2_ORDER
    if CATE2_TO_CATE1[cate2] in selected_cate1
]

selected_cate2 = st.sidebar.multiselect(
    "CATE2 선택",
    available_cate2,
    default=available_cate2
)

available_cate3 = [
    cate3 for cate3 in CATE3_ORDER
    if df[
        (df["CATE2"].isin(selected_cate2)) &
        (df["CATE3"] == cate3)
    ].shape[0] > 0
]

selected_cate3 = st.sidebar.multiselect(
    "CATE3 선택",
    available_cate3,
    default=available_cate3
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
    (df["CATE1"].isin(selected_cate1)) &
    (df["CATE2"].isin(selected_cate2)) &
    (df["CATE3"].isin(selected_cate3))
].copy()

if df_selected.empty:
    st.warning("선택된 카테고리 데이터가 없습니다.")
    st.stop()

if view_type == "일간":
    filtered = df_selected[df_selected["일자"].dt.date == selected_date]
    period_label = str(selected_date)

elif view_type == "주간":
    filtered = df_selected[df_selected["주차"] == selected_week]
    period_label = selected_week

else:
    filtered = df_selected[df_selected["월"] == selected_month]
    period_label = selected_month

if filtered.empty:
    st.warning("선택된 기간에 데이터가 없습니다.")
    st.stop()

# =====================================================
# 8. 헤더
# =====================================================
st.markdown('<div class="title">📦 Product Category Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">상품 카테고리별 {view_type} 판매금액 · 판매수량 분석 / 기준: {period_label}</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 9. 전체 KPI
# =====================================================
total_sales = filtered["판매금액"].sum()
total_qty = filtered["판매수량"].sum()
avg_price = total_sales / total_qty if total_qty > 0 else 0
active_items = filtered[filtered["판매수량"] > 0]["상품명"].nunique()
total_items = filtered["상품명"].nunique()
active_rate = active_items / total_items if total_items > 0 else 0

best_cate2 = (
    filtered.groupby("CATE2", observed=True)["판매금액"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

st.markdown('<div class="section-title">① 전체 현황</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card("판매금액", format_won(total_sales), f"{view_type} 기준")

with c2:
    kpi_card("판매수량", format_qty(total_qty), "총 판매 수량")

with c3:
    kpi_card("평균판매가", format_won(avg_price), "금액 / 수량")

with c4:
    kpi_card("판매 발생 상품", f"{active_items}개", f"가동률 {format_pct(active_rate)}")

c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card("전체 상품 수", f"{total_items}개")

with c6:
    kpi_card("BEST CATE2", best_cate2)

with c7:
    app_sales = filtered[filtered["CATE1"] == "APP"]["판매금액"].sum()
    kpi_card("APP 매출", format_won(app_sales))

with c8:
    acc_sales = filtered[filtered["CATE1"] == "ACC"]["판매금액"].sum()
    kpi_card("ACC 매출", format_won(acc_sales))

# =====================================================
# 10. CATE1 판매금액 / 판매수량
# =====================================================
st.markdown('<div class="section-title">② CATE1 판매금액 / 판매수량</div>', unsafe_allow_html=True)

cate1_summary = filtered.groupby("CATE1", as_index=False, observed=True).agg({
    "판매금액": "sum",
    "판매수량": "sum"
})

cate1_summary = cate1_summary[cate1_summary["판매금액"] > 0].copy()
cate1_summary["CATE1"] = pd.Categorical(cate1_summary["CATE1"], categories=CATE1_ORDER, ordered=True)
cate1_summary = cate1_summary.sort_values("CATE1")
cate1_summary["판매금액라벨"] = cate1_summary["판매금액"].apply(format_million_label)

left, right = st.columns(2)

with left:
    fig_cate1_sales = px.bar(
        cate1_summary,
        x="CATE1",
        y="판매금액",
        text="판매금액라벨",
        color="CATE1",
        category_orders={"CATE1": CATE1_ORDER},
        color_discrete_map=CATE1_COLOR_MAP
    )

    fig_cate1_sales.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        textfont_size=15,
        textfont_color="#FFFFFF",
        width=0.42
    )

    fig_cate1_sales = apply_dark_chart_style(fig_cate1_sales, height=390, x_category_order=CATE1_ORDER)
    fig_cate1_sales.update_layout(bargap=0.45, showlegend=False)
    fig_cate1_sales.update_yaxes(title="판매금액")
    st.plotly_chart(fig_cate1_sales, use_container_width=True)

with right:
    fig_cate1_qty = px.bar(
        cate1_summary,
        x="CATE1",
        y="판매수량",
        text="판매수량",
        color="CATE1",
        category_orders={"CATE1": CATE1_ORDER},
        color_discrete_map=CATE1_COLOR_MAP
    )

    fig_cate1_qty.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont_size=15,
        textfont_color="#FFFFFF",
        width=0.42
    )

    fig_cate1_qty = apply_dark_chart_style(fig_cate1_qty, height=390, x_category_order=CATE1_ORDER)
    fig_cate1_qty.update_layout(bargap=0.45, showlegend=False)
    fig_cate1_qty.update_yaxes(title="판매수량")
    st.plotly_chart(fig_cate1_qty, use_container_width=True)

# =====================================================
# 11. CATE2 판매금액 / 판매수량
# =====================================================
st.markdown('<div class="section-title">③ CATE2 판매금액 / 판매수량</div>', unsafe_allow_html=True)

cate2_summary = filtered.groupby(["CATE1", "CATE2"], as_index=False, observed=True).agg({
    "판매금액": "sum",
    "판매수량": "sum"
})

cate2_summary = cate2_summary[cate2_summary["판매금액"] > 0].copy()
cate2_summary["CATE2"] = pd.Categorical(cate2_summary["CATE2"], categories=CATE2_ORDER, ordered=True)
cate2_summary = cate2_summary.sort_values("CATE2")
cate2_summary["판매금액라벨"] = cate2_summary["판매금액"].apply(format_million_label)

cate2_left, cate2_right = st.columns(2)

with cate2_left:
    fig_cate2_sales = px.bar(
        cate2_summary,
        x="CATE2",
        y="판매금액",
        text="판매금액라벨",
        color="CATE2",
        category_orders={"CATE2": CATE2_ORDER},
        color_discrete_map=CATE2_COLOR_MAP
    )

    fig_cate2_sales.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        textfont_size=14,
        textfont_color="#FFFFFF",
        width=0.45
    )

    fig_cate2_sales = apply_dark_chart_style(fig_cate2_sales, height=420, x_category_order=CATE2_ORDER)
    fig_cate2_sales.update_layout(bargap=0.40, showlegend=False)
    fig_cate2_sales.update_yaxes(title="판매금액")
    st.plotly_chart(fig_cate2_sales, use_container_width=True)

with cate2_right:
    fig_cate2_qty = px.bar(
        cate2_summary,
        x="CATE2",
        y="판매수량",
        text="판매수량",
        color="CATE2",
        category_orders={"CATE2": CATE2_ORDER},
        color_discrete_map=CATE2_COLOR_MAP
    )

    fig_cate2_qty.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont_size=14,
        textfont_color="#FFFFFF",
        width=0.45
    )

    fig_cate2_qty = apply_dark_chart_style(fig_cate2_qty, height=420, x_category_order=CATE2_ORDER)
    fig_cate2_qty.update_layout(bargap=0.40, showlegend=False)
    fig_cate2_qty.update_yaxes(title="판매수량")
    st.plotly_chart(fig_cate2_qty, use_container_width=True)

# =====================================================
# 12. CATE3 세부 카테고리 현황
# =====================================================
st.markdown('<div class="section-title">④ CATE3 세부 카테고리 현황</div>', unsafe_allow_html=True)

cate3_summary = filtered.groupby(["CATE1", "CATE2", "CATE3"], as_index=False, observed=True).agg({
    "TAG가": "max",
    "입고수량": "max",
    "판매금액": "sum",
    "판매수량": "sum",
    "할인율": "mean"
})

cate3_summary = cate3_summary[cate3_summary["판매금액"] > 0].copy()

cate3_summary["판매율"] = np.where(
    cate3_summary["입고수량"] > 0,
    cate3_summary["판매수량"] / cate3_summary["입고수량"],
    0
)

cate3_summary["재고수량"] = cate3_summary["입고수량"] - cate3_summary["판매수량"]
cate3_summary["재고수량"] = cate3_summary["재고수량"].clip(lower=0)

cate3_summary["평균판매가"] = np.where(
    cate3_summary["판매수량"] > 0,
    cate3_summary["판매금액"] / cate3_summary["판매수량"],
    0
)

cate3_summary["CATE1"] = pd.Categorical(cate3_summary["CATE1"], categories=CATE1_ORDER, ordered=True)
cate3_summary["CATE2"] = pd.Categorical(cate3_summary["CATE2"], categories=CATE2_ORDER, ordered=True)
cate3_summary["CATE3"] = pd.Categorical(cate3_summary["CATE3"], categories=CATE3_ORDER, ordered=True)

cate3_summary = cate3_summary.sort_values(["CATE1", "CATE2", "CATE3"]).reset_index(drop=True)
cate3_summary["판매금액라벨"] = cate3_summary["판매금액"].apply(format_million_label)

fig_cate3 = px.bar(
    cate3_summary,
    x="CATE3",
    y="판매금액",
    text="판매금액라벨",
    color="CATE2",
    category_orders={
        "CATE3": CATE3_ORDER,
        "CATE2": CATE2_ORDER
    },
    color_discrete_map=CATE2_COLOR_MAP
)

fig_cate3.update_traces(
    texttemplate="%{text}",
    textposition="outside",
    textfont_size=12,
    textfont_color="#FFFFFF",
    width=0.45
)

fig_cate3 = apply_dark_chart_style(fig_cate3, height=440, x_category_order=CATE3_ORDER)
fig_cate3.update_layout(bargap=0.38, legend_title_text="CATE2")
fig_cate3.update_yaxes(title="판매금액")
st.plotly_chart(fig_cate3, use_container_width=True)

# =====================================================
# 13. 상품별 BEST / WORST
# =====================================================
st.markdown('<div class="section-title">⑤ 상품별 BEST / WORST</div>', unsafe_allow_html=True)

product_summary = filtered.groupby(
    ["CATE1", "CATE2", "CATE3", "상품명"],
    as_index=False,
    observed=True
).agg({
    "TAG가": "max",
    "입고수량": "max",
    "판매금액": "sum",
    "판매수량": "sum",
    "할인율": "mean"
})

product_summary = product_summary[product_summary["입고수량"] > 0].copy()

product_summary["판매율"] = np.where(
    product_summary["입고수량"] > 0,
    product_summary["판매수량"] / product_summary["입고수량"],
    0
)

product_summary["재고수량"] = product_summary["입고수량"] - product_summary["판매수량"]
product_summary["재고수량"] = product_summary["재고수량"].clip(lower=0)

best_amount_items = product_summary.sort_values("판매금액", ascending=False).head(10)
best_rate_items = product_summary.sort_values("판매율", ascending=False).head(10)
worst_rate_items = product_summary.sort_values("판매율", ascending=True).head(10)

def make_product_display(input_df):
    display = input_df.copy()

    display["TAG가"] = display["TAG가"].apply(format_won)
    display["입고수량"] = display["입고수량"].apply(format_qty)
    display["판매수량"] = display["판매수량"].apply(format_qty)
    display["판매율"] = display["판매율"].apply(format_pct)
    display["할인율"] = display["할인율"].apply(format_pct)
    display["재고수량"] = display["재고수량"].apply(format_qty)
    display["판매금액"] = display["판매금액"].apply(format_won)

    return display[
        [
            "CATE1",
            "CATE2",
            "CATE3",
            "상품명",
            "TAG가",
            "입고수량",
            "판매수량",
            "판매율",
            "할인율",
            "재고수량",
            "판매금액"
        ]
    ]

tab1, tab2, tab3 = st.tabs(["🏆 금액 BEST", "🔥 판매율 BEST", "⚠️ 판매율 WORST"])

with tab1:
    st.dataframe(
        make_product_display(best_amount_items),
        use_container_width=True,
        height=380
    )

with tab2:
    st.dataframe(
        make_product_display(best_rate_items),
        use_container_width=True,
        height=380
    )

with tab3:
    st.dataframe(
        make_product_display(worst_rate_items),
        use_container_width=True,
        height=380
    )

# =====================================================
# 14. 카테고리 상세 테이블
# =====================================================
st.markdown('<div class="section-title">⑥ 카테고리 상세 테이블</div>', unsafe_allow_html=True)

detail_display = cate3_summary.copy()

detail_display["TAG가"] = detail_display["TAG가"].apply(format_won)
detail_display["입고수량"] = detail_display["입고수량"].apply(format_qty)
detail_display["판매수량"] = detail_display["판매수량"].apply(format_qty)
detail_display["판매율"] = detail_display["판매율"].apply(format_pct)
detail_display["할인율"] = detail_display["할인율"].apply(format_pct)
detail_display["재고수량"] = detail_display["재고수량"].apply(format_qty)
detail_display["판매금액"] = detail_display["판매금액"].apply(format_won)

st.dataframe(
    detail_display[
        [
            "CATE1",
            "CATE2",
            "CATE3",
            "TAG가",
            "입고수량",
            "판매수량",
            "판매율",
            "할인율",
            "재고수량",
            "판매금액"
        ]
    ],
    use_container_width=True,
    height=420
)

# =====================================================
# 15. 일자별 판매금액 / 판매수량 추이
# =====================================================
st.markdown('<div class="section-title">⑦ 일자별 판매금액 / 판매수량 추이</div>', unsafe_allow_html=True)

daily_trend = filtered.groupby("일자", as_index=False).agg({
    "판매금액": "sum",
    "판매수량": "sum"
})

fig_trend = go.Figure()

fig_trend.add_trace(
    go.Scatter(
        x=daily_trend["일자"],
        y=daily_trend["판매금액"],
        mode="lines+markers",
        name="판매금액",
        line=dict(color="#60A5FA", width=3),
        marker=dict(size=7)
    )
)

fig_trend.add_trace(
    go.Scatter(
        x=daily_trend["일자"],
        y=daily_trend["판매수량"],
        mode="lines+markers",
        name="판매수량",
        yaxis="y2",
        line=dict(color="#F59E0B", width=3),
        marker=dict(size=7)
    )
)

fig_trend.update_layout(
    height=430,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(size=14, color="#FFFFFF"),
    xaxis=dict(
        title=None,
        tickfont=dict(size=14, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    ),
    yaxis=dict(
        title="판매금액",
        tickfont=dict(size=13, color="#FFFFFF"),
        title_font=dict(size=15, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    ),
    yaxis2=dict(
        title="판매수량",
        overlaying="y",
        side="right",
        tickfont=dict(size=13, color="#FFFFFF"),
        title_font=dict(size=15, color="#FFFFFF"),
        showgrid=False
    ),
    legend=dict(
        orientation="h",
        y=-0.2,
        font=dict(size=13, color="#FFFFFF")
    )
)

st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# 16. 데이터 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑧ 데이터 다운로드</div>', unsafe_allow_html=True)

download_df = product_summary.copy()
csv = download_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 상품별 분석 CSV 다운로드",
    data=csv,
    file_name=f"product_category_analysis_{view_type}_{period_label}.csv",
    mime="text/csv"
)

# =====================================================
# 17. 안내
# =====================================================
with st.expander("📌 이 대시보드에서 보는 핵심"):
    st.markdown("""
    이 대시보드는 상품 카테고리별 판매금액과 판매수량을 일간/주간/월간 단위로 보는 용도입니다.

    현재 카테고리 구조:
    - CATE1: APP / ACC
    - CATE2: OUTER / INNER / BOTTOM / CAP / BAG / SHOES / ETC
    - CATE3: CATE1 → CATE2 순서에 맞춰 고정 정렬

    상품별 BEST/WORST 표:
    - 상품코드 제거
    - TAG가
    - 입고수량
    - 판매수량
    - 판매율
    - 할인율
    - 재고수량
    - 판매금액

    카테고리 상세 테이블:
    - TAG가
    - 입고수량
    - 판매수량
    - 판매율
    - 할인율
    - 재고수량
    - 판매금액
=======
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
    page_title="Product Category Dashboard",
    page_icon="📦",
    layout="wide"
)

# =====================================================
# 2. 카테고리 설정
# =====================================================
CATE1_ORDER = ["APP", "ACC"]

CATE2_ORDER = [
    "OUTER", "INNER", "BOTTOM",
    "CAP", "BAG", "SHOES", "ETC"
]

CATE2_TO_CATE1 = {
    "OUTER": "APP",
    "INNER": "APP",
    "BOTTOM": "APP",
    "CAP": "ACC",
    "BAG": "ACC",
    "SHOES": "ACC",
    "ETC": "ACC",
}

CATE3_MAP = {
    "OUTER": ["JACKET", "COAT", "JUMPER", "CARDIGAN"],
    "INNER": ["T-SHIRT", "SHIRT", "KNIT", "HOODIE"],
    "BOTTOM": ["PANTS", "DENIM", "SKIRT", "SHORTS"],
    "CAP": ["BALL CAP", "BUCKET HAT", "BEANIE"],
    "BAG": ["BACKPACK", "TOTE BAG", "CROSS BAG"],
    "SHOES": ["SNEAKERS", "SANDAL", "BOOTS"],
    "ETC": ["SOCKS", "KEYRING", "POUCH", "ACC ETC"],
}

CATE3_ORDER = []
for cate2 in CATE2_ORDER:
    CATE3_ORDER.extend(CATE3_MAP[cate2])

CATE1_COLOR_MAP = {
    "APP": "#60A5FA",
    "ACC": "#F59E0B",
}

CATE2_COLOR_MAP = {
    "OUTER": "#3B82F6",
    "INNER": "#60A5FA",
    "BOTTOM": "#93C5FD",
    "CAP": "#F59E0B",
    "BAG": "#FBBF24",
    "SHOES": "#F97316",
    "ETC": "#9CA3AF",
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


def format_qty(value):
    return f"{value:,.0f}개"


def format_pct(value):
    return f"{value * 100:.1f}%"


def format_million_label(value):
    value = float(value)
    if value <= 0:
        return ""
    return f"{value / 1_000_000:.0f}M"


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
        tickfont=dict(size=15, color="#FFFFFF"),
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
            y=-0.22,
            font=dict(size=13, color="#FFFFFF")
        )
    )

    return fig


# =====================================================
# 5. 샘플 상품 데이터 생성
# =====================================================
@st.cache_data
def create_sample_product_data():
    np.random.seed(42)

    today = datetime.today().date()
    start_date = today - timedelta(days=89)
    dates = pd.date_range(start=start_date, end=today, freq="D")

    data = []

    for cate2 in CATE2_ORDER:
        cate1 = CATE2_TO_CATE1[cate2]
        cate3_list = CATE3_MAP[cate2]

        for cate3 in cate3_list:
            for i in range(1, 6):
                item_code = f"{cate2[:2]}-{cate3[:2]}-{i:03d}"
                item_name = f"{cate3} ITEM {i}"

                tag_price = np.random.choice([
                    19000, 29000, 39000, 49000, 69000,
                    89000, 129000, 159000, 199000
                ])

                inbound_qty = np.random.randint(250, 1500)

                for date in dates:
                    if cate1 == "APP":
                        base_qty = np.random.randint(2, 18)
                    else:
                        base_qty = np.random.randint(1, 14)

                    if date.weekday() in [5, 6]:
                        qty = int(base_qty * np.random.uniform(1.2, 1.8))
                    else:
                        qty = int(base_qty * np.random.uniform(0.7, 1.2))

                    qty = max(qty, 0)

                    discount_rate = np.random.choice(
                        [0, 0.05, 0.1, 0.15, 0.2],
                        p=[0.45, 0.2, 0.2, 0.1, 0.05]
                    )

                    selling_price = int(tag_price * (1 - discount_rate))
                    sales_amount = qty * selling_price

                    data.append({
                        "일자": date,
                        "CATE1": cate1,
                        "CATE2": cate2,
                        "CATE3": cate3,
                        "상품코드": item_code,
                        "상품명": item_name,
                        "TAG가": tag_price,
                        "입고수량": inbound_qty,
                        "판매수량": qty,
                        "판매금액": sales_amount,
                        "실판매가": selling_price,
                        "할인율": discount_rate
                    })

    df = pd.DataFrame(data)

    df["일자"] = pd.to_datetime(df["일자"])
    df["주차"] = df["일자"].dt.strftime("%Y-W%U")
    df["월"] = df["일자"].dt.strftime("%Y-%m")
    df["요일"] = df["일자"].dt.day_name()

    df["CATE1"] = pd.Categorical(df["CATE1"], categories=CATE1_ORDER, ordered=True)
    df["CATE2"] = pd.Categorical(df["CATE2"], categories=CATE2_ORDER, ordered=True)
    df["CATE3"] = pd.Categorical(df["CATE3"], categories=CATE3_ORDER, ordered=True)

    return df


df = create_sample_product_data()

# =====================================================
# 6. 사이드바 필터
# =====================================================
st.sidebar.title("⚙️ 조회 조건")

view_type = st.sidebar.radio(
    "조회 기준",
    ["일간", "주간", "월간"],
    horizontal=True
)

selected_cate1 = st.sidebar.multiselect(
    "CATE1 선택",
    CATE1_ORDER,
    default=CATE1_ORDER
)

available_cate2 = [
    cate2 for cate2 in CATE2_ORDER
    if CATE2_TO_CATE1[cate2] in selected_cate1
]

selected_cate2 = st.sidebar.multiselect(
    "CATE2 선택",
    available_cate2,
    default=available_cate2
)

available_cate3 = [
    cate3 for cate3 in CATE3_ORDER
    if df[
        (df["CATE2"].isin(selected_cate2)) &
        (df["CATE3"] == cate3)
    ].shape[0] > 0
]

selected_cate3 = st.sidebar.multiselect(
    "CATE3 선택",
    available_cate3,
    default=available_cate3
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
    (df["CATE1"].isin(selected_cate1)) &
    (df["CATE2"].isin(selected_cate2)) &
    (df["CATE3"].isin(selected_cate3))
].copy()

if df_selected.empty:
    st.warning("선택된 카테고리 데이터가 없습니다.")
    st.stop()

if view_type == "일간":
    filtered = df_selected[df_selected["일자"].dt.date == selected_date]
    period_label = str(selected_date)

elif view_type == "주간":
    filtered = df_selected[df_selected["주차"] == selected_week]
    period_label = selected_week

else:
    filtered = df_selected[df_selected["월"] == selected_month]
    period_label = selected_month

if filtered.empty:
    st.warning("선택된 기간에 데이터가 없습니다.")
    st.stop()

# =====================================================
# 8. 헤더
# =====================================================
st.markdown('<div class="title">📦 Product Category Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">상품 카테고리별 {view_type} 판매금액 · 판매수량 분석 / 기준: {period_label}</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 9. 전체 KPI
# =====================================================
total_sales = filtered["판매금액"].sum()
total_qty = filtered["판매수량"].sum()
avg_price = total_sales / total_qty if total_qty > 0 else 0
active_items = filtered[filtered["판매수량"] > 0]["상품명"].nunique()
total_items = filtered["상품명"].nunique()
active_rate = active_items / total_items if total_items > 0 else 0

best_cate2 = (
    filtered.groupby("CATE2", observed=True)["판매금액"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

st.markdown('<div class="section-title">① 전체 현황</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card("판매금액", format_won(total_sales), f"{view_type} 기준")

with c2:
    kpi_card("판매수량", format_qty(total_qty), "총 판매 수량")

with c3:
    kpi_card("평균판매가", format_won(avg_price), "금액 / 수량")

with c4:
    kpi_card("판매 발생 상품", f"{active_items}개", f"가동률 {format_pct(active_rate)}")

c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card("전체 상품 수", f"{total_items}개")

with c6:
    kpi_card("BEST CATE2", best_cate2)

with c7:
    app_sales = filtered[filtered["CATE1"] == "APP"]["판매금액"].sum()
    kpi_card("APP 매출", format_won(app_sales))

with c8:
    acc_sales = filtered[filtered["CATE1"] == "ACC"]["판매금액"].sum()
    kpi_card("ACC 매출", format_won(acc_sales))

# =====================================================
# 10. CATE1 판매금액 / 판매수량
# =====================================================
st.markdown('<div class="section-title">② CATE1 판매금액 / 판매수량</div>', unsafe_allow_html=True)

cate1_summary = filtered.groupby("CATE1", as_index=False, observed=True).agg({
    "판매금액": "sum",
    "판매수량": "sum"
})

cate1_summary = cate1_summary[cate1_summary["판매금액"] > 0].copy()
cate1_summary["CATE1"] = pd.Categorical(cate1_summary["CATE1"], categories=CATE1_ORDER, ordered=True)
cate1_summary = cate1_summary.sort_values("CATE1")
cate1_summary["판매금액라벨"] = cate1_summary["판매금액"].apply(format_million_label)

left, right = st.columns(2)

with left:
    fig_cate1_sales = px.bar(
        cate1_summary,
        x="CATE1",
        y="판매금액",
        text="판매금액라벨",
        color="CATE1",
        category_orders={"CATE1": CATE1_ORDER},
        color_discrete_map=CATE1_COLOR_MAP
    )

    fig_cate1_sales.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        textfont_size=15,
        textfont_color="#FFFFFF",
        width=0.42
    )

    fig_cate1_sales = apply_dark_chart_style(fig_cate1_sales, height=390, x_category_order=CATE1_ORDER)
    fig_cate1_sales.update_layout(bargap=0.45, showlegend=False)
    fig_cate1_sales.update_yaxes(title="판매금액")
    st.plotly_chart(fig_cate1_sales, use_container_width=True)

with right:
    fig_cate1_qty = px.bar(
        cate1_summary,
        x="CATE1",
        y="판매수량",
        text="판매수량",
        color="CATE1",
        category_orders={"CATE1": CATE1_ORDER},
        color_discrete_map=CATE1_COLOR_MAP
    )

    fig_cate1_qty.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont_size=15,
        textfont_color="#FFFFFF",
        width=0.42
    )

    fig_cate1_qty = apply_dark_chart_style(fig_cate1_qty, height=390, x_category_order=CATE1_ORDER)
    fig_cate1_qty.update_layout(bargap=0.45, showlegend=False)
    fig_cate1_qty.update_yaxes(title="판매수량")
    st.plotly_chart(fig_cate1_qty, use_container_width=True)

# =====================================================
# 11. CATE2 판매금액 / 판매수량
# =====================================================
st.markdown('<div class="section-title">③ CATE2 판매금액 / 판매수량</div>', unsafe_allow_html=True)

cate2_summary = filtered.groupby(["CATE1", "CATE2"], as_index=False, observed=True).agg({
    "판매금액": "sum",
    "판매수량": "sum"
})

cate2_summary = cate2_summary[cate2_summary["판매금액"] > 0].copy()
cate2_summary["CATE2"] = pd.Categorical(cate2_summary["CATE2"], categories=CATE2_ORDER, ordered=True)
cate2_summary = cate2_summary.sort_values("CATE2")
cate2_summary["판매금액라벨"] = cate2_summary["판매금액"].apply(format_million_label)

cate2_left, cate2_right = st.columns(2)

with cate2_left:
    fig_cate2_sales = px.bar(
        cate2_summary,
        x="CATE2",
        y="판매금액",
        text="판매금액라벨",
        color="CATE2",
        category_orders={"CATE2": CATE2_ORDER},
        color_discrete_map=CATE2_COLOR_MAP
    )

    fig_cate2_sales.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        textfont_size=14,
        textfont_color="#FFFFFF",
        width=0.45
    )

    fig_cate2_sales = apply_dark_chart_style(fig_cate2_sales, height=420, x_category_order=CATE2_ORDER)
    fig_cate2_sales.update_layout(bargap=0.40, showlegend=False)
    fig_cate2_sales.update_yaxes(title="판매금액")
    st.plotly_chart(fig_cate2_sales, use_container_width=True)

with cate2_right:
    fig_cate2_qty = px.bar(
        cate2_summary,
        x="CATE2",
        y="판매수량",
        text="판매수량",
        color="CATE2",
        category_orders={"CATE2": CATE2_ORDER},
        color_discrete_map=CATE2_COLOR_MAP
    )

    fig_cate2_qty.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont_size=14,
        textfont_color="#FFFFFF",
        width=0.45
    )

    fig_cate2_qty = apply_dark_chart_style(fig_cate2_qty, height=420, x_category_order=CATE2_ORDER)
    fig_cate2_qty.update_layout(bargap=0.40, showlegend=False)
    fig_cate2_qty.update_yaxes(title="판매수량")
    st.plotly_chart(fig_cate2_qty, use_container_width=True)

# =====================================================
# 12. CATE3 세부 카테고리 현황
# =====================================================
st.markdown('<div class="section-title">④ CATE3 세부 카테고리 현황</div>', unsafe_allow_html=True)

cate3_summary = filtered.groupby(["CATE1", "CATE2", "CATE3"], as_index=False, observed=True).agg({
    "TAG가": "max",
    "입고수량": "max",
    "판매금액": "sum",
    "판매수량": "sum",
    "할인율": "mean"
})

cate3_summary = cate3_summary[cate3_summary["판매금액"] > 0].copy()

cate3_summary["판매율"] = np.where(
    cate3_summary["입고수량"] > 0,
    cate3_summary["판매수량"] / cate3_summary["입고수량"],
    0
)

cate3_summary["재고수량"] = cate3_summary["입고수량"] - cate3_summary["판매수량"]
cate3_summary["재고수량"] = cate3_summary["재고수량"].clip(lower=0)

cate3_summary["평균판매가"] = np.where(
    cate3_summary["판매수량"] > 0,
    cate3_summary["판매금액"] / cate3_summary["판매수량"],
    0
)

cate3_summary["CATE1"] = pd.Categorical(cate3_summary["CATE1"], categories=CATE1_ORDER, ordered=True)
cate3_summary["CATE2"] = pd.Categorical(cate3_summary["CATE2"], categories=CATE2_ORDER, ordered=True)
cate3_summary["CATE3"] = pd.Categorical(cate3_summary["CATE3"], categories=CATE3_ORDER, ordered=True)

cate3_summary = cate3_summary.sort_values(["CATE1", "CATE2", "CATE3"]).reset_index(drop=True)
cate3_summary["판매금액라벨"] = cate3_summary["판매금액"].apply(format_million_label)

fig_cate3 = px.bar(
    cate3_summary,
    x="CATE3",
    y="판매금액",
    text="판매금액라벨",
    color="CATE2",
    category_orders={
        "CATE3": CATE3_ORDER,
        "CATE2": CATE2_ORDER
    },
    color_discrete_map=CATE2_COLOR_MAP
)

fig_cate3.update_traces(
    texttemplate="%{text}",
    textposition="outside",
    textfont_size=12,
    textfont_color="#FFFFFF",
    width=0.45
)

fig_cate3 = apply_dark_chart_style(fig_cate3, height=440, x_category_order=CATE3_ORDER)
fig_cate3.update_layout(bargap=0.38, legend_title_text="CATE2")
fig_cate3.update_yaxes(title="판매금액")
st.plotly_chart(fig_cate3, use_container_width=True)

# =====================================================
# 13. 상품별 BEST / WORST
# =====================================================
st.markdown('<div class="section-title">⑤ 상품별 BEST / WORST</div>', unsafe_allow_html=True)

product_summary = filtered.groupby(
    ["CATE1", "CATE2", "CATE3", "상품명"],
    as_index=False,
    observed=True
).agg({
    "TAG가": "max",
    "입고수량": "max",
    "판매금액": "sum",
    "판매수량": "sum",
    "할인율": "mean"
})

product_summary = product_summary[product_summary["입고수량"] > 0].copy()

product_summary["판매율"] = np.where(
    product_summary["입고수량"] > 0,
    product_summary["판매수량"] / product_summary["입고수량"],
    0
)

product_summary["재고수량"] = product_summary["입고수량"] - product_summary["판매수량"]
product_summary["재고수량"] = product_summary["재고수량"].clip(lower=0)

best_amount_items = product_summary.sort_values("판매금액", ascending=False).head(10)
best_rate_items = product_summary.sort_values("판매율", ascending=False).head(10)
worst_rate_items = product_summary.sort_values("판매율", ascending=True).head(10)

def make_product_display(input_df):
    display = input_df.copy()

    display["TAG가"] = display["TAG가"].apply(format_won)
    display["입고수량"] = display["입고수량"].apply(format_qty)
    display["판매수량"] = display["판매수량"].apply(format_qty)
    display["판매율"] = display["판매율"].apply(format_pct)
    display["할인율"] = display["할인율"].apply(format_pct)
    display["재고수량"] = display["재고수량"].apply(format_qty)
    display["판매금액"] = display["판매금액"].apply(format_won)

    return display[
        [
            "CATE1",
            "CATE2",
            "CATE3",
            "상품명",
            "TAG가",
            "입고수량",
            "판매수량",
            "판매율",
            "할인율",
            "재고수량",
            "판매금액"
        ]
    ]

tab1, tab2, tab3 = st.tabs(["🏆 금액 BEST", "🔥 판매율 BEST", "⚠️ 판매율 WORST"])

with tab1:
    st.dataframe(
        make_product_display(best_amount_items),
        use_container_width=True,
        height=380
    )

with tab2:
    st.dataframe(
        make_product_display(best_rate_items),
        use_container_width=True,
        height=380
    )

with tab3:
    st.dataframe(
        make_product_display(worst_rate_items),
        use_container_width=True,
        height=380
    )

# =====================================================
# 14. 카테고리 상세 테이블
# =====================================================
st.markdown('<div class="section-title">⑥ 카테고리 상세 테이블</div>', unsafe_allow_html=True)

detail_display = cate3_summary.copy()

detail_display["TAG가"] = detail_display["TAG가"].apply(format_won)
detail_display["입고수량"] = detail_display["입고수량"].apply(format_qty)
detail_display["판매수량"] = detail_display["판매수량"].apply(format_qty)
detail_display["판매율"] = detail_display["판매율"].apply(format_pct)
detail_display["할인율"] = detail_display["할인율"].apply(format_pct)
detail_display["재고수량"] = detail_display["재고수량"].apply(format_qty)
detail_display["판매금액"] = detail_display["판매금액"].apply(format_won)

st.dataframe(
    detail_display[
        [
            "CATE1",
            "CATE2",
            "CATE3",
            "TAG가",
            "입고수량",
            "판매수량",
            "판매율",
            "할인율",
            "재고수량",
            "판매금액"
        ]
    ],
    use_container_width=True,
    height=420
)

# =====================================================
# 15. 일자별 판매금액 / 판매수량 추이
# =====================================================
st.markdown('<div class="section-title">⑦ 일자별 판매금액 / 판매수량 추이</div>', unsafe_allow_html=True)

daily_trend = filtered.groupby("일자", as_index=False).agg({
    "판매금액": "sum",
    "판매수량": "sum"
})

fig_trend = go.Figure()

fig_trend.add_trace(
    go.Scatter(
        x=daily_trend["일자"],
        y=daily_trend["판매금액"],
        mode="lines+markers",
        name="판매금액",
        line=dict(color="#60A5FA", width=3),
        marker=dict(size=7)
    )
)

fig_trend.add_trace(
    go.Scatter(
        x=daily_trend["일자"],
        y=daily_trend["판매수량"],
        mode="lines+markers",
        name="판매수량",
        yaxis="y2",
        line=dict(color="#F59E0B", width=3),
        marker=dict(size=7)
    )
)

fig_trend.update_layout(
    height=430,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(size=14, color="#FFFFFF"),
    xaxis=dict(
        title=None,
        tickfont=dict(size=14, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    ),
    yaxis=dict(
        title="판매금액",
        tickfont=dict(size=13, color="#FFFFFF"),
        title_font=dict(size=15, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    ),
    yaxis2=dict(
        title="판매수량",
        overlaying="y",
        side="right",
        tickfont=dict(size=13, color="#FFFFFF"),
        title_font=dict(size=15, color="#FFFFFF"),
        showgrid=False
    ),
    legend=dict(
        orientation="h",
        y=-0.2,
        font=dict(size=13, color="#FFFFFF")
    )
)

st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# 16. 데이터 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑧ 데이터 다운로드</div>', unsafe_allow_html=True)

download_df = product_summary.copy()
csv = download_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 상품별 분석 CSV 다운로드",
    data=csv,
    file_name=f"product_category_analysis_{view_type}_{period_label}.csv",
    mime="text/csv"
)

# =====================================================
# 17. 안내
# =====================================================
with st.expander("📌 이 대시보드에서 보는 핵심"):
    st.markdown("""
    이 대시보드는 상품 카테고리별 판매금액과 판매수량을 일간/주간/월간 단위로 보는 용도입니다.

    현재 카테고리 구조:
    - CATE1: APP / ACC
    - CATE2: OUTER / INNER / BOTTOM / CAP / BAG / SHOES / ETC
    - CATE3: CATE1 → CATE2 순서에 맞춰 고정 정렬

    상품별 BEST/WORST 표:
    - 상품코드 제거
    - TAG가
    - 입고수량
    - 판매수량
    - 판매율
    - 할인율
    - 재고수량
    - 판매금액

    카테고리 상세 테이블:
    - TAG가
    - 입고수량
    - 판매수량
    - 판매율
    - 할인율
    - 재고수량
    - 판매금액
>>>>>>> 202e8a8b7b32446112832f6db9b4a6c848701843
    """)