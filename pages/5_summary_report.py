import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# =====================================================
# 1. 페이지 설정
# =====================================================
st.set_page_config(
    page_title="MD Summary Report",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# 2. 기본 설정
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

# =====================================================
# 3. 스타일
# =====================================================
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }

    .title {
        font-size: 38px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 15px;
        color: #D1D5DB;
        margin-bottom: 22px;
        line-height: 1.6;
    }

    .section-title {
        font-size: 24px;
        font-weight: 850;
        color: #FFFFFF;
        margin-top: 26px;
        margin-bottom: 14px;
    }

    .kpi-card {
        background-color: #171B26;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #2A2F3A;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.25);
        min-height: 120px;
    }

    .kpi-label {
        font-size: 14px;
        color: #D1D5DB;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 900;
        color: #FFFFFF;
    }

    .kpi-sub {
        font-size: 13px;
        color: #9CA3AF;
        margin-top: 8px;
    }

    .summary-card {
        background-color: #171B26;
        padding: 22px 26px;
        border-radius: 18px;
        border: 1px solid #2A2F3A;
        margin-bottom: 16px;
    }

    .summary-title {
        font-size: 18px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 8px;
    }

    .summary-text {
        font-size: 15px;
        color: #D1D5DB;
        line-height: 1.7;
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


def kpi_card(label, value, sub_text=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)


def get_font(size=24, bold=False):
    font_candidates = []

    if bold:
        font_candidates = [
            "C:/Windows/Fonts/malgunbd.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_candidates = [
            "C:/Windows/Fonts/malgun.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size=size)

    return ImageFont.load_default()


def draw_card(draw, x, y, w, h, title, value, sub_text=""):
    bg_color = "#171B26"
    border_color = "#2A2F3A"
    title_color = "#D1D5DB"
    value_color = "#FFFFFF"
    sub_color = "#9CA3AF"

    draw.rounded_rectangle(
        [(x, y), (x + w, y + h)],
        radius=20,
        fill=bg_color,
        outline=border_color,
        width=2
    )

    title_font = get_font(20, bold=False)
    value_font = get_font(36, bold=True)
    sub_font = get_font(16, bold=False)

    draw.text((x + 24, y + 20), str(title), fill=title_color, font=title_font)
    draw.text((x + 24, y + 55), str(value), fill=value_color, font=value_font)
    draw.text((x + 24, y + 105), str(sub_text), fill=sub_color, font=sub_font)


# =====================================================
# 5. 샘플 데이터 생성
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

    return df


# =====================================================
# 6. 업로드 데이터 처리
# =====================================================
def prepare_product_data(input_df):
    df_prepared = input_df.copy()
    df_prepared.columns = df_prepared.columns.astype(str).str.strip()

    missing_cols = [
        col for col in REQUIRED_COLUMNS
        if col not in df_prepared.columns
    ]

    if missing_cols:
        st.error(f"업로드 파일에 필요한 컬럼이 없습니다: {missing_cols}")
        st.stop()

    df_prepared["일자"] = pd.to_datetime(df_prepared["일자"], errors="coerce")

    if df_prepared["일자"].isna().any():
        st.error("일자 컬럼에 날짜로 변환할 수 없는 값이 있습니다.")
        st.stop()

    number_cols = ["TAG가", "입고수량", "판매수량", "판매금액", "할인율"]

    for col in number_cols:
        df_prepared[col] = pd.to_numeric(df_prepared[col], errors="coerce").fillna(0)

    if df_prepared["할인율"].max() > 1:
        df_prepared["할인율"] = df_prepared["할인율"] / 100

    if "실판매가" not in df_prepared.columns:
        df_prepared["실판매가"] = np.where(
            df_prepared["판매수량"] > 0,
            df_prepared["판매금액"] / df_prepared["판매수량"],
            df_prepared["TAG가"] * (1 - df_prepared["할인율"])
        )

    if "상품코드" not in df_prepared.columns:
        df_prepared["상품코드"] = "-"

    df_prepared["주차"] = df_prepared["일자"].dt.strftime("%Y-W%U")
    df_prepared["월"] = df_prepared["일자"].dt.strftime("%Y-%m")
    df_prepared["요일"] = df_prepared["일자"].dt.day_name()

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


def create_summary_report_excel(summary_df, top_items, low_items, comments):
    output = BytesIO()

    comment_df = pd.DataFrame({
        "MD 자동 코멘트": comments
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, index=False, sheet_name="요약")
        top_items.to_excel(writer, index=False, sheet_name="TOP상품")
        low_items.to_excel(writer, index=False, sheet_name="LOW상품")
        comment_df.to_excel(writer, index=False, sheet_name="MD코멘트")

    output.seek(0)
    return output


def create_summary_report_png(
    view_type,
    period_label,
    total_sales,
    total_qty,
    total_items,
    stock_risk_count,
    top_cate2,
    top_cate2_share,
    best_item,
    worst_item,
    comments
):
    width, height = 1600, 900
    bg_color = "#0E1117"
    title_color = "#FFFFFF"
    sub_color = "#D1D5DB"
    card_bg = "#171B26"
    border_color = "#2A2F3A"

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    title_font = get_font(42, bold=True)
    subtitle_font = get_font(20, bold=False)
    section_font = get_font(26, bold=True)
    text_font = get_font(18, bold=False)
    text_bold_font = get_font(18, bold=True)

    # 헤더
    draw.text((60, 40), "MD Weekly Summary", fill=title_color, font=title_font)
    draw.text(
        (60, 95),
        f"기준: {view_type} · {period_label}",
        fill=sub_color,
        font=subtitle_font
    )

    # KPI 제목
    draw.text((60, 145), "핵심 KPI", fill=title_color, font=section_font)

    # KPI 카드
    card_y = 190
    card_w = 350
    card_h = 130
    gap = 20

    draw_card(draw, 60, card_y, card_w, card_h, "총 판매금액", format_won(total_sales), f"{view_type} 기준")
    draw_card(draw, 60 + (card_w + gap), card_y, card_w, card_h, "판매수량", format_qty(total_qty), "총 판매수량")
    draw_card(draw, 60 + 2 * (card_w + gap), card_y, card_w, card_h, "상품 수", f"{total_items:,}개", "분석 상품 수")
    draw_card(draw, 60 + 3 * (card_w + gap), card_y, card_w, card_h, "재고주의", f"{stock_risk_count:,}개", "판매율 낮음 + 재고 높음")

    # TOP/LOW 제목
    draw.text((60, 350), "TOP / LOW 요약", fill=title_color, font=section_font)

    left_x = 60
    right_x = 820
    box_y = 395
    box_w = 720
    box_h = 160

    draw.rounded_rectangle(
        [(left_x, box_y), (left_x + box_w, box_y + box_h)],
        radius=20, fill=card_bg, outline=border_color, width=2
    )
    draw.rounded_rectangle(
        [(right_x, box_y), (right_x + box_w, box_y + box_h)],
        radius=20, fill=card_bg, outline=border_color, width=2
    )

    draw.text((left_x + 24, box_y + 20), "판매금액 TOP 상품", fill=title_color, font=text_bold_font)
    top_lines = [
        f"상품명: {best_item['상품명']}",
        f"카테고리: {best_item['CATE2']} / {best_item['CATE3']}",
        f"판매금액: {format_won(best_item['판매금액'])}",
        f"판매수량: {format_qty(best_item['판매수량'])}",
        f"판매율: {format_pct(best_item['판매율'])}",
    ]
    y_cursor = box_y + 55
    for line in top_lines:
        draw.text((left_x + 24, y_cursor), line, fill=sub_color, font=text_font)
        y_cursor += 24

    draw.text((right_x + 24, box_y + 20), "판매율 LOW 상품", fill=title_color, font=text_bold_font)
    low_lines = [
        f"상품명: {worst_item['상품명']}",
        f"카테고리: {worst_item['CATE2']} / {worst_item['CATE3']}",
        f"판매금액: {format_won(worst_item['판매금액'])}",
        f"재고수량: {format_qty(worst_item['재고수량'])}",
        f"판매율: {format_pct(worst_item['판매율'])}",
    ]
    y_cursor = box_y + 55
    for line in low_lines:
        draw.text((right_x + 24, y_cursor), line, fill=sub_color, font=text_font)
        y_cursor += 24

    # 코멘트 제목
    draw.text((60, 590), "MD 자동 코멘트", fill=title_color, font=section_font)

    comment_x = 60
    comment_y = 635
    comment_w = 1480
    comment_h = 210

    draw.rounded_rectangle(
        [(comment_x, comment_y), (comment_x + comment_w, comment_y + comment_h)],
        radius=20, fill=card_bg, outline=border_color, width=2
    )

    y_cursor = comment_y + 22
    for idx, comment in enumerate(comments[:5], start=1):
        wrapped = textwrap.wrap(f"{idx}. {comment}", width=85)
        for line in wrapped:
            draw.text((comment_x + 24, y_cursor), line, fill=sub_color, font=text_font)
            y_cursor += 24
        y_cursor += 8

    footer_text = f"TOP CATE2: {top_cate2} / 비중: {format_pct(top_cate2_share)}"
    draw.text((60, 860), footer_text, fill="#9CA3AF", font=get_font(16, bold=False))

    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output


# =====================================================
# 7. 사이드바
# =====================================================
st.sidebar.markdown("---")
st.sidebar.subheader("📁 데이터 업로드")

uploaded_file = st.sidebar.file_uploader(
    "요약 리포트용 상품 데이터 업로드",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    uploaded_df = load_uploaded_product_file(uploaded_file)
    df = prepare_product_data(uploaded_df)
    st.sidebar.success("업로드 데이터 적용됨")
else:
    df = create_sample_product_data()
    st.sidebar.info("샘플 데이터 사용 중")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ 조회 조건")

view_type = st.sidebar.radio(
    "조회 기준",
    ["일간", "주간", "월간"],
    horizontal=True
)

if view_type == "일간":
    date_list = sorted(df["일자"].dt.date.unique())
    selected_date = st.sidebar.selectbox(
        "일자 선택",
        date_list,
        index=len(date_list) - 1
    )
    filtered = df[df["일자"].dt.date == selected_date]
    period_label = str(selected_date)

elif view_type == "주간":
    week_list = sorted(df["주차"].unique())
    selected_week = st.sidebar.selectbox(
        "주차 선택",
        week_list,
        index=len(week_list) - 1
    )
    filtered = df[df["주차"] == selected_week]
    period_label = selected_week

else:
    month_list = sorted(df["월"].unique())
    selected_month = st.sidebar.selectbox(
        "월 선택",
        month_list,
        index=len(month_list) - 1
    )
    filtered = df[df["월"] == selected_month]
    period_label = selected_month

if filtered.empty:
    st.warning("선택된 기간에 데이터가 없습니다.")
    st.stop()

# =====================================================
# 8. 상품 요약 데이터 생성
# =====================================================
product_summary = filtered.groupby(
    ["CATE1", "CATE2", "CATE3", "상품명"],
    as_index=False
).agg({
    "TAG가": "max",
    "입고수량": "max",
    "판매금액": "sum",
    "판매수량": "sum",
    "할인율": "mean"
})

product_summary = product_summary[product_summary["입고수량"] > 0].copy()

if product_summary.empty:
    st.warning("요약 가능한 상품 데이터가 없습니다.")
    st.stop()

product_summary["판매율"] = np.where(
    product_summary["입고수량"] > 0,
    product_summary["판매수량"] / product_summary["입고수량"],
    0
)

product_summary["재고수량"] = product_summary["입고수량"] - product_summary["판매수량"]
product_summary["재고수량"] = product_summary["재고수량"].clip(lower=0)

total_sales = product_summary["판매금액"].sum()
total_qty = product_summary["판매수량"].sum()
total_items = product_summary["상품명"].nunique()
avg_sell_through = product_summary["판매율"].mean()

stock_risk_items = product_summary[
    (product_summary["판매율"] < 0.3) &
    (product_summary["재고수량"] >= 300)
]

discount_risk_items = product_summary[
    (product_summary["할인율"] >= 0.15) &
    (product_summary["판매율"] < 0.4)
]

reorder_items = product_summary[
    (product_summary["판매율"] >= 0.8) &
    (product_summary["재고수량"] <= 50)
]

top_cate2_summary = (
    product_summary.groupby("CATE2")["판매금액"]
    .sum()
    .sort_values(ascending=False)
)

top_cate2 = top_cate2_summary.index[0]
top_cate2_sales = top_cate2_summary.iloc[0]
top_cate2_share = top_cate2_sales / total_sales if total_sales > 0 else 0

top_items = product_summary.sort_values("판매금액", ascending=False).head(10)
best_rate_items = product_summary.sort_values("판매율", ascending=False).head(10)
low_items = product_summary.sort_values("판매율", ascending=True).head(10)

best_item = top_items.iloc[0]
worst_item = low_items.iloc[0]

# =====================================================
# 9. 자동 코멘트 생성
# =====================================================
comments = []

comments.append(
    f"{view_type} 기준 {period_label} 기간에는 '{top_cate2}' 카테고리가 "
    f"전체 판매금액의 {top_cate2_share * 100:.1f}%를 차지하며 가장 높은 매출 비중을 보였습니다."
)

if len(stock_risk_items) > 0:
    comments.append(
        f"판매율이 낮고 재고가 많은 재고주의 상품이 {len(stock_risk_items)}개 확인됩니다. "
        "해당 상품은 소진 전략과 노출 강화가 필요합니다."
    )
else:
    comments.append(
        "판매율 30% 미만이면서 재고수량이 높은 재고주의 상품은 크게 부각되지 않습니다."
    )

if len(discount_risk_items) > 0:
    comments.append(
        f"할인율 15% 이상이지만 판매율이 낮은 할인주의 상품이 {len(discount_risk_items)}개 있습니다. "
        "가격 할인만으로 반응이 약한 상품은 상품력과 스타일링 점검이 필요합니다."
    )

if len(reorder_items) > 0:
    comments.append(
        f"판매율 80% 이상이면서 재고가 낮은 추가 발주 후보가 {len(reorder_items)}개 있습니다. "
        "추가 생산 또는 유사 상품 확대를 검토할 수 있습니다."
    )

comments.append(
    f"전체 기준으로 총 {total_items}개 상품에서 {total_qty:,.0f}개가 판매되었고, "
    f"총 판매금액은 {format_won(total_sales)}입니다."
)

# =====================================================
# 10. 헤더
# =====================================================
st.markdown('<div class="title">📊 MD Weekly Summary</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">보고용 핵심 요약 페이지 / 기준: {view_type} · {period_label}</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 11. KPI
# =====================================================
st.markdown('<div class="section-title">① 핵심 KPI</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card("총 판매금액", format_won(total_sales), f"{view_type} 기준")

with c2:
    kpi_card("판매수량", format_qty(total_qty), "총 판매수량")

with c3:
    kpi_card("상품 수", f"{total_items:,}개", "분석 상품 수")

with c4:
    kpi_card("재고주의", f"{len(stock_risk_items):,}개", "판매율 낮음 + 재고 높음")

c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card("TOP CATE2", top_cate2, f"비중 {format_pct(top_cate2_share)}")

with c6:
    kpi_card("평균 판매율", format_pct(avg_sell_through), "상품 평균")

with c7:
    kpi_card("할인주의", f"{len(discount_risk_items):,}개", "할인율 높음 + 판매율 낮음")

with c8:
    kpi_card("추가발주 후보", f"{len(reorder_items):,}개", "판매율 높음 + 재고 낮음")

# =====================================================
# 12. TOP / LOW 요약
# =====================================================
st.markdown('<div class="section-title">② TOP / LOW 요약</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">🏆 판매금액 TOP 상품</div>
        <div class="summary-text">
            상품명: <b>{best_item['상품명']}</b><br>
            카테고리: {best_item['CATE2']} / {best_item['CATE3']}<br>
            판매금액: {format_won(best_item['판매금액'])}<br>
            판매수량: {format_qty(best_item['판매수량'])}<br>
            판매율: {format_pct(best_item['판매율'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">⚠️ 판매율 LOW 상품</div>
        <div class="summary-text">
            상품명: <b>{worst_item['상품명']}</b><br>
            카테고리: {worst_item['CATE2']} / {worst_item['CATE3']}<br>
            판매금액: {format_won(worst_item['판매금액'])}<br>
            재고수량: {format_qty(worst_item['재고수량'])}<br>
            판매율: {format_pct(worst_item['판매율'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 13. MD 자동 코멘트
# =====================================================
st.markdown('<div class="section-title">③ MD 자동 코멘트</div>', unsafe_allow_html=True)

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
# 14. 상세 표
# =====================================================
st.markdown('<div class="section-title">④ 상세 TOP / LOW 테이블</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏆 판매금액 TOP", "🔥 판매율 BEST", "⚠️ 판매율 LOW"])


def display_table(input_df):
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


with tab1:
    st.dataframe(display_table(top_items), use_container_width=True, height=320)

with tab2:
    st.dataframe(display_table(best_rate_items), use_container_width=True, height=320)

with tab3:
    st.dataframe(display_table(low_items), use_container_width=True, height=320)

# =====================================================
# 15. 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑤ 보고용 다운로드</div>', unsafe_allow_html=True)

summary_df = pd.DataFrame({
    "항목": [
        "총 판매금액",
        "판매수량",
        "상품 수",
        "재고주의 상품 수",
        "TOP CATE2",
        "평균 판매율",
        "할인주의 상품 수",
        "추가발주 후보 수"
    ],
    "값": [
        total_sales,
        total_qty,
        total_items,
        len(stock_risk_items),
        top_cate2,
        avg_sell_through,
        len(discount_risk_items),
        len(reorder_items)
    ]
})

report_file = create_summary_report_excel(
    summary_df=summary_df,
    top_items=top_items,
    low_items=low_items,
    comments=comments
)

st.download_button(
    label="📊 Summary Report 엑셀 다운로드",
    data=report_file,
    file_name=f"summary_report_{view_type}_{period_label}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

png_file = create_summary_report_png(
    view_type=view_type,
    period_label=period_label,
    total_sales=total_sales,
    total_qty=total_qty,
    total_items=total_items,
    stock_risk_count=len(stock_risk_items),
    top_cate2=top_cate2,
    top_cate2_share=top_cate2_share,
    best_item=best_item,
    worst_item=worst_item,
    comments=comments
)

st.download_button(
    label="🖼️ Summary Report 이미지 다운로드",
    data=png_file,
    file_name=f"summary_report_{view_type}_{period_label}.png",
    mime="image/png"
)

st.caption("MD Weekly Summary · 보고용 핵심 요약 페이지")