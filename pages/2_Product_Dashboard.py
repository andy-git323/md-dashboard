import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO

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

def create_product_template_excel():
    sample_data = pd.DataFrame({
        "일자": ["2026-05-01", "2026-05-01", "2026-05-01"],
        "CATE1": ["APP", "APP", "ACC"],
        "CATE2": ["OUTER", "INNER", "CAP"],
        "CATE3": ["JACKET", "T-SHIRT", "BALL CAP"],
        "상품명": ["JACKET ITEM 1", "T-SHIRT ITEM 1", "BALL CAP ITEM 1"],
        "TAG가": [129000, 39000, 49000],
        "입고수량": [500, 800, 600],
        "판매수량": [20, 50, 30],
        "판매금액": [2322000, 1755000, 1323000],
        "할인율": [0.10, 0.10, 0.10],
        "실판매가": [116100, 35100, 44100]
    })

    guide_data = pd.DataFrame({
        "컬럼명": [
            "일자", "CATE1", "CATE2", "CATE3", "상품명",
            "TAG가", "입고수량", "판매수량", "판매금액", "할인율", "실판매가"
        ],
        "설명": [
            "판매 일자",
            "대분류: APP / ACC",
            "중분류: OUTER / INNER / BOTTOM / CAP / BAG / SHOES / ETC",
            "세부 카테고리",
            "상품명",
            "정상 판매가",
            "해당 상품의 총 입고수량",
            "해당 기간 판매수량",
            "해당 기간 판매금액",
            "할인율: 0.1 또는 10 모두 가능",
            "실제 판매단가, 없으면 자동 계산 가능"
        ],
        "필수여부": [
            "필수", "필수", "필수", "필수", "필수",
            "필수", "필수", "필수", "필수", "필수", "선택"
        ]
    })

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        sample_data.to_excel(writer, index=False, sheet_name="상품판매데이터")
        guide_data.to_excel(writer, index=False, sheet_name="업로드가이드")

    output.seek(0)
    return output

def create_product_report_excel(cate3_summary, product_summary, period_label, view_type):
    output = BytesIO()

    cate3_report = cate3_summary.copy()
    product_report = product_summary.copy()

    # 카테고리 상세 리포트 정리
    if not cate3_report.empty:
        cate3_report["판매율"] = np.where(
            cate3_report["입고수량"] > 0,
            cate3_report["판매수량"] / cate3_report["입고수량"],
            0
        )

        cate3_report["재고수량"] = cate3_report["입고수량"] - cate3_report["판매수량"]
        cate3_report["재고수량"] = cate3_report["재고수량"].clip(lower=0)

        cate3_report = cate3_report[
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
        ]

    # 상품별 리포트 정리
    if not product_report.empty:
        product_report["판매율"] = np.where(
            product_report["입고수량"] > 0,
            product_report["판매수량"] / product_report["입고수량"],
            0
        )

        product_report["재고수량"] = product_report["입고수량"] - product_report["판매수량"]
        product_report["재고수량"] = product_report["재고수량"].clip(lower=0)

        product_report = product_report[
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

    # 요약 시트
    summary_report = pd.DataFrame({
        "구분": [
            "조회 기준",
            "조회 기간",
            "총 판매금액",
            "총 판매수량",
            "상품 수",
            "카테고리 수"
        ],
        "값": [
            view_type,
            period_label,
            product_report["판매금액"].sum() if not product_report.empty else 0,
            product_report["판매수량"].sum() if not product_report.empty else 0,
            product_report["상품명"].nunique() if "상품명" in product_report.columns else 0,
            cate3_report["CATE3"].nunique() if "CATE3" in cate3_report.columns else 0
        ]
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_report.to_excel(writer, index=False, sheet_name="요약")
        cate3_report.to_excel(writer, index=False, sheet_name="카테고리상세")
        product_report.sort_values("판매금액", ascending=False).to_excel(
            writer,
            index=False,
            sheet_name="상품별_금액순"
        )
        product_report.sort_values("판매율", ascending=False).to_excel(
            writer,
            index=False,
            sheet_name="상품별_판매율순"
        )
        product_report.sort_values("판매율", ascending=True).to_excel(
            writer,
            index=False,
            sheet_name="상품별_LOW"
        )

    output.seek(0)
    return output
def generate_md_product_comments(product_summary, cate3_summary, view_type, period_label):
    comments = []

    if product_summary.empty:
        return [
            "데이터 없음",
            "필터 조건 확인 필요"
        ]

    total_sales = product_summary["판매금액"].sum()
    total_qty = product_summary["판매수량"].sum()
    total_items = product_summary["상품명"].nunique()

    product_summary = product_summary.copy()

    if "판매율" not in product_summary.columns:
        product_summary["판매율"] = np.where(
            product_summary["입고수량"] > 0,
            product_summary["판매수량"] / product_summary["입고수량"],
            0
        )

    if "재고수량" not in product_summary.columns:
        product_summary["재고수량"] = product_summary["입고수량"] - product_summary["판매수량"]
        product_summary["재고수량"] = product_summary["재고수량"].clip(lower=0)

    cate2_sales = (
        product_summary.groupby("CATE2", observed=True)["판매금액"]
        .sum()
        .sort_values(ascending=False)
    )

    top_cate2 = cate2_sales.index[0]
    top_cate2_share = cate2_sales.iloc[0] / total_sales if total_sales > 0 else 0

    top_item = product_summary.sort_values("판매금액", ascending=False).iloc[0]
    low_item = product_summary.sort_values("판매율", ascending=True).iloc[0]

    stock_risk = product_summary[
        (product_summary["판매율"] < 0.3) &
        (product_summary["재고수량"] >= 300)
    ]

    discount_risk = product_summary[
        (product_summary["할인율"] >= 0.15) &
        (product_summary["판매율"] < 0.4)
    ]

    reorder_candidates = product_summary[
        (product_summary["판매율"] >= 0.8) &
        (product_summary["재고수량"] <= 50)
    ]

    comments.append(
        f"매출 중심: {top_cate2} {top_cate2_share * 100:.1f}%"
    )

    comments.append(
        f"TOP 상품: {top_item['상품명']} / {format_won(top_item['판매금액'])}"
    )

    if len(stock_risk) > 0:
        comments.append(
            f"재고주의: {len(stock_risk)}개"
        )
    else:
        comments.append(
            "재고주의: 없음"
        )

    if len(discount_risk) > 0:
        comments.append(
            f"할인주의: {len(discount_risk)}개"
        )
    else:
        comments.append(
            "할인주의: 없음"
        )

    if len(reorder_candidates) > 0:
        reorder_item = reorder_candidates.sort_values("판매율", ascending=False).iloc[0]
        comments.append(
            f"리오더 후보: {reorder_item['상품명']}"
        )
    else:
        comments.append(
            "리오더 후보: 없음"
        )

    comments.append(
        f"LOW 상품: {low_item['상품명']} / 판매율 {format_pct(low_item['판매율'])}"
    )

    if len(stock_risk) > 0:
        comments.append("우선 액션: 재고 소진")
    elif len(discount_risk) > 0:
        comments.append("우선 액션: 할인 효율 점검")
    elif len(reorder_candidates) > 0:
        comments.append("우선 액션: 리오더 검토")
    else:
        comments.append("우선 액션: TOP 상품 확대")

    return comments

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


# =====================================================
# 6. 데이터 불러오기: 업로드 파일 or 샘플 데이터
# =====================================================
REQUIRED_COLUMNS = [
    "일자",
    "CATE1",
    "CATE2",
    "CATE3",
    "상품명",
    "TAG가",
    "입고수량",
    "판매수량",
    "판매금액",
    "할인율"
]


def prepare_product_data(input_df):
    df_prepared = input_df.copy()

    # 컬럼명 앞뒤 공백 제거
    df_prepared.columns = df_prepared.columns.astype(str).str.strip()

    # 필수 컬럼 확인
    missing_cols = [
        col for col in REQUIRED_COLUMNS
        if col not in df_prepared.columns
    ]

    if missing_cols:
        st.error(f"업로드 파일에 필요한 컬럼이 없습니다: {missing_cols}")
        st.info("""
        필요한 컬럼:
        일자, CATE1, CATE2, CATE3, 상품명, TAG가, 입고수량, 판매수량, 판매금액, 할인율
        """)
        st.stop()

    # 날짜 변환
    df_prepared["일자"] = pd.to_datetime(df_prepared["일자"], errors="coerce")

    if df_prepared["일자"].isna().any():
        st.error("일자 컬럼에 날짜로 변환할 수 없는 값이 있습니다.")
        st.stop()

    # 숫자 컬럼 변환
    number_cols = ["TAG가", "입고수량", "판매수량", "판매금액", "할인율"]

    for col in number_cols:
        df_prepared[col] = pd.to_numeric(df_prepared[col], errors="coerce").fillna(0)

    # 할인율이 10, 15 같은 값으로 들어온 경우 0.10, 0.15로 변환
    if df_prepared["할인율"].max() > 1:
        df_prepared["할인율"] = df_prepared["할인율"] / 100

    # 실판매가 컬럼이 없으면 계산해서 생성
    if "실판매가" not in df_prepared.columns:
        df_prepared["실판매가"] = np.where(
            df_prepared["판매수량"] > 0,
            df_prepared["판매금액"] / df_prepared["판매수량"],
            df_prepared["TAG가"] * (1 - df_prepared["할인율"])
        )

    # 상품코드 컬럼이 없으면 임시 생성
    if "상품코드" not in df_prepared.columns:
        df_prepared["상품코드"] = (
            df_prepared["CATE2"].astype(str).str[:2]
            + "-"
            + df_prepared["CATE3"].astype(str).str[:2]
            + "-"
            + df_prepared.groupby(["CATE2", "CATE3", "상품명"]).ngroup().astype(str)
        )

    # 주차 / 월 / 요일 생성
    df_prepared["주차"] = df_prepared["일자"].dt.strftime("%Y-W%U")
    df_prepared["월"] = df_prepared["일자"].dt.strftime("%Y-%m")
    df_prepared["요일"] = df_prepared["일자"].dt.day_name()

    # 카테고리 순서 적용
    df_prepared["CATE1"] = pd.Categorical(
        df_prepared["CATE1"],
        categories=CATE1_ORDER,
        ordered=True
    )

    df_prepared["CATE2"] = pd.Categorical(
        df_prepared["CATE2"],
        categories=CATE2_ORDER,
        ordered=True
    )

    df_prepared["CATE3"] = pd.Categorical(
        df_prepared["CATE3"],
        categories=CATE3_ORDER,
        ordered=True
    )

    return df_prepared


def load_uploaded_product_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        uploaded_df = pd.read_csv(uploaded_file)
    else:
        excel_file = pd.ExcelFile(uploaded_file)

        if "상품판매데이터" in excel_file.sheet_names:
            uploaded_df = pd.read_excel(uploaded_file, sheet_name="상품판매데이터")
        else:
            uploaded_df = pd.read_excel(uploaded_file, sheet_name=excel_file.sheet_names[0])

    return uploaded_df


st.sidebar.markdown("---")
st.sidebar.subheader("📁 데이터 업로드")

template_file = create_product_template_excel()

st.sidebar.download_button(
    label="📄 상품 업로드 양식 다운로드",
    data=template_file,
    file_name="product_category_upload_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

uploaded_file = st.sidebar.file_uploader(
    "상품 판매 데이터 업로드",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    uploaded_df = load_uploaded_product_file(uploaded_file)
    df = prepare_product_data(uploaded_df)
    st.sidebar.success("업로드 데이터 적용됨")
else:
    df = create_sample_product_data()
    st.sidebar.info("샘플 데이터 사용 중")

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
# 업로드 데이터 요약 / 미리보기
# =====================================================
with st.expander("📌 현재 적용 데이터 확인", expanded=False):
    data_min_date = df["일자"].min().date()
    data_max_date = df["일자"].max().date()
    row_count = len(df)
    item_count = df["상품명"].nunique()
    cate2_count = df["CATE2"].nunique()
    total_upload_sales = df["판매금액"].sum()
    total_upload_qty = df["판매수량"].sum()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("데이터 기간", f"{data_min_date} ~ {data_max_date}")

    with c2:
        st.metric("전체 행 수", f"{row_count:,}행")

    with c3:
        st.metric("상품 수", f"{item_count:,}개")

    with c4:
        st.metric("CATE2 수", f"{cate2_count:,}개")

    c5, c6 = st.columns(2)

    with c5:
        st.metric("전체 판매금액", format_won(total_upload_sales))

    with c6:
        st.metric("전체 판매수량", format_qty(total_upload_qty))

    st.markdown("#### 데이터 미리보기")
    st.dataframe(
        df.head(20),
        use_container_width=True,
        height=300
    )
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

# =====================================================
# MD 자동 코멘트
# =====================================================
st.markdown('<div class="section-title">📌 MD 자동 코멘트</div>', unsafe_allow_html=True)

md_comments = generate_md_product_comments(
    product_summary=product_summary,
    cate3_summary=cate3_summary,
    view_type=view_type,
    period_label=period_label
)

comment_lines = ""

for idx, comment in enumerate(md_comments, start=1):
    comment_lines += (
        f'<p style="color:#E5E7EB; font-size:18px; line-height:1.75; margin-bottom:15px;">'
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

report_file = create_product_report_excel(
    cate3_summary=cate3_summary,
    product_summary=product_summary,
    period_label=period_label,
    view_type=view_type
)

st.download_button(
    label="📊 상품 분석 리포트 엑셀 다운로드",
    data=report_file,
    file_name=f"product_analysis_report_{view_type}_{period_label}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

csv = product_summary.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 상품별 원본 요약 CSV 다운로드",
    data=csv,
    file_name=f"product_summary_{view_type}_{period_label}.csv",
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
    """)