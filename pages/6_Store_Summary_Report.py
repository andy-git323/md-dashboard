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
    page_title="Store Summary Report",
    page_icon="🏬",
    layout="wide"
)

# =====================================================
# 2. 기본 설정
# =====================================================
REGION_ORDER = ["A지역", "B지역", "C지역"]

STORE_ORDER = [
    "매장 1", "매장 2", "매장 3",
    "매장 4", "매장 5", "매장 6",
    "매장 7", "매장 8", "매장 9", "매장 10"
]

STORE_TO_REGION = {
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

REQUIRED_COLUMNS = [
    "일자",
    "지역",
    "매장",
    "일목표",
    "일매출",
    "방문객수",
    "구매건수"
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
    if bold:
        font_candidates = [
            "C:/Windows/Fonts/malgunbd.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_candidates = [
            "C:/Windows/Fonts/malgun.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size=size)

    return ImageFont.load_default()


# =====================================================
# 5. 샘플 매장 데이터 생성
# =====================================================
@st.cache_data
def create_sample_store_data():
    np.random.seed(24)

    today = datetime.today().date()
    start_date = today - timedelta(days=89)
    dates = pd.date_range(start=start_date, end=today, freq="D")

    data = []

    for store in STORE_ORDER:
        region = STORE_TO_REGION[store]

        if region == "A지역":
            base_target = np.random.randint(4_500_000, 7_000_000)
        elif region == "B지역":
            base_target = np.random.randint(5_000_000, 8_000_000)
        else:
            base_target = np.random.randint(4_000_000, 7_500_000)

        store_power = np.random.uniform(0.75, 1.20)

        for date in dates:
            weekend_boost = 1.25 if date.weekday() in [5, 6] else 1.0

            daily_target = int(base_target * weekend_boost)

            achievement_rate = np.random.normal(loc=store_power, scale=0.16)
            achievement_rate = max(0.35, min(1.45, achievement_rate))

            daily_sales = int(daily_target * achievement_rate)

            visitors = int(np.random.randint(120, 360) * weekend_boost)
            conversion_rate = np.random.uniform(0.18, 0.38)
            purchases = max(1, int(visitors * conversion_rate))

            avg_price = daily_sales / purchases if purchases > 0 else 0

            data.append({
                "일자": date,
                "지역": region,
                "매장": store,
                "일목표": daily_target,
                "일매출": daily_sales,
                "방문객수": visitors,
                "구매건수": purchases,
                "객단가": avg_price
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
def prepare_store_data(input_df):
    df_prepared = input_df.copy()
    df_prepared.columns = df_prepared.columns.astype(str).str.strip()

    missing_cols = [
        col for col in REQUIRED_COLUMNS
        if col not in df_prepared.columns
    ]

    if missing_cols:
        st.error(f"업로드 파일에 필요한 컬럼이 없습니다: {missing_cols}")
        st.info("필수 컬럼: 일자, 지역, 매장, 일목표, 일매출, 방문객수, 구매건수")
        st.stop()

    df_prepared["일자"] = pd.to_datetime(df_prepared["일자"], errors="coerce")

    if df_prepared["일자"].isna().any():
        st.error("일자 컬럼에 날짜로 변환할 수 없는 값이 있습니다.")
        st.stop()

    number_cols = ["일목표", "일매출", "방문객수", "구매건수"]

    for col in number_cols:
        df_prepared[col] = pd.to_numeric(df_prepared[col], errors="coerce").fillna(0)

    if "객단가" not in df_prepared.columns:
        df_prepared["객단가"] = np.where(
            df_prepared["구매건수"] > 0,
            df_prepared["일매출"] / df_prepared["구매건수"],
            0
        )
    else:
        df_prepared["객단가"] = pd.to_numeric(df_prepared["객단가"], errors="coerce").fillna(0)

    df_prepared["주차"] = df_prepared["일자"].dt.strftime("%Y-W%U")
    df_prepared["월"] = df_prepared["일자"].dt.strftime("%Y-%m")
    df_prepared["요일"] = df_prepared["일자"].dt.day_name()

    return df_prepared


def load_uploaded_store_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        uploaded_df = pd.read_csv(uploaded_file)
    else:
        excel_file = pd.ExcelFile(uploaded_file)

        if "매장판매데이터" in excel_file.sheet_names:
            uploaded_df = pd.read_excel(uploaded_file, sheet_name="매장판매데이터")
        else:
            uploaded_df = pd.read_excel(uploaded_file, sheet_name=excel_file.sheet_names[0])

    return uploaded_df


def create_store_summary_excel(summary_df, region_summary, store_summary, comments):
    output = BytesIO()

    comment_df = pd.DataFrame({
        "매장 자동 코멘트": comments
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, index=False, sheet_name="요약")
        region_summary.to_excel(writer, index=False, sheet_name="지역별요약")
        store_summary.to_excel(writer, index=False, sheet_name="매장별요약")
        comment_df.to_excel(writer, index=False, sheet_name="자동코멘트")

    output.seek(0)
    return output


def create_store_summary_png(
    view_type,
    period_label,
    total_target,
    total_sales,
    avg_progress,
    risk_store_count,
    top_region,
    top_region_progress,
    best_store,
    worst_store,
    comments
):
    width, height = 1600, 900

    bg_color = "#0B0F19"
    panel_color = "#111827"
    card_color = "#171B26"
    border_color = "#2A2F3A"
    point_blue = "#60A5FA"
    point_orange = "#F59E0B"
    point_red = "#EF4444"
    point_green = "#22C55E"
    white = "#FFFFFF"
    gray = "#D1D5DB"
    muted = "#9CA3AF"

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    title_font = get_font(44, bold=True)
    subtitle_font = get_font(20, bold=False)
    section_font = get_font(24, bold=True)
    kpi_label_font = get_font(18, bold=False)
    kpi_value_font = get_font(34, bold=True)
    small_font = get_font(15, bold=False)
    body_font = get_font(18, bold=False)
    body_bold_font = get_font(18, bold=True)

    # 상단 라인
    draw.rectangle([(0, 0), (1600, 8)], fill=point_green)

    # 우측 정보 박스
    draw.rounded_rectangle(
        [(1250, 36), (1525, 118)],
        radius=24,
        fill="#0F172A",
        outline="#1E293B",
        width=2
    )
    draw.text((1280, 58), "STORE DATA REPORT", fill=muted, font=small_font)
    draw.text((1280, 82), f"{view_type} · {period_label}", fill=white, font=body_bold_font)

    # 헤더
    draw.text((60, 42), "Store Weekly Summary", fill=white, font=title_font)
    draw.text(
        (60, 100),
        "Store Sales · Target Progress · Regional Performance",
        fill=gray,
        font=subtitle_font
    )

    draw.rounded_rectangle(
        [(60, 138), (390, 176)],
        radius=19,
        fill="#111827",
        outline="#263244",
        width=2
    )
    draw.text((82, 147), f"기준: {view_type} · {period_label}", fill=gray, font=small_font)

    # KPI 카드 함수
    def draw_kpi_card(x, y, w, h, label, value, sub, accent):
        draw.rounded_rectangle(
            [(x, y), (x + w, y + h)],
            radius=22,
            fill=card_color,
            outline=border_color,
            width=2
        )
        draw.rectangle([(x, y), (x + 8, y + h)], fill=accent)
        draw.text((x + 28, y + 22), label, fill=gray, font=kpi_label_font)
        draw.text((x + 28, y + 58), value, fill=white, font=kpi_value_font)
        draw.text((x + 28, y + 108), sub, fill=muted, font=small_font)

    kpi_y = 210
    kpi_w = 355
    kpi_h = 145
    gap = 24

    draw_kpi_card(
        60,
        kpi_y,
        kpi_w,
        kpi_h,
        "총 목표",
        format_won(total_target),
        f"{view_type} 기준",
        point_blue
    )

    draw_kpi_card(
        60 + (kpi_w + gap),
        kpi_y,
        kpi_w,
        kpi_h,
        "총 매출",
        format_won(total_sales),
        "실적 합계",
        "#93C5FD"
    )

    draw_kpi_card(
        60 + 2 * (kpi_w + gap),
        kpi_y,
        kpi_w,
        kpi_h,
        "평균 진도율",
        format_pct(avg_progress),
        "목표 대비",
        point_orange
    )

    draw_kpi_card(
        60 + 3 * (kpi_w + gap),
        kpi_y,
        kpi_w,
        kpi_h,
        "위험 매장",
        f"{risk_store_count:,}개",
        "진도율 80% 미만",
        point_red
    )

    # TOP / LOW 매장 요약
    draw.text((60, 395), "BEST / LOW Store Summary", fill=white, font=section_font)

    box_y = 438
    box_w = 710
    box_h = 180

    # BEST
    draw.rounded_rectangle(
        [(60, box_y), (60 + box_w, box_y + box_h)],
        radius=24,
        fill=panel_color,
        outline=border_color,
        width=2
    )

    draw.rounded_rectangle(
        [(84, box_y + 22), (250, box_y + 55)],
        radius=16,
        fill="#14532D"
    )
    draw.text((102, box_y + 29), "BEST STORE", fill=white, font=small_font)

    draw.text((84, box_y + 72), str(best_store["매장"]), fill=white, font=body_bold_font)

    best_lines = [
        f"지역      {best_store['지역']}",
        f"목표      {format_won(best_store['목표'])}",
        f"매출      {format_won(best_store['매출'])}",
        f"진도율    {format_pct(best_store['진도율'])}",
    ]

    y_cursor = box_y + 103
    for line in best_lines:
        draw.text((84, y_cursor), line, fill=gray, font=small_font)
        y_cursor += 24

    # LOW
    right_x = 830

    draw.rounded_rectangle(
        [(right_x, box_y), (right_x + box_w, box_y + box_h)],
        radius=24,
        fill=panel_color,
        outline=border_color,
        width=2
    )

    draw.rounded_rectangle(
        [(right_x + 24, box_y + 22), (right_x + 190, box_y + 55)],
        radius=16,
        fill="#7F1D1D"
    )
    draw.text((right_x + 42, box_y + 29), "LOW STORE", fill=white, font=small_font)

    draw.text((right_x + 24, box_y + 72), str(worst_store["매장"]), fill=white, font=body_bold_font)

    low_lines = [
        f"지역      {worst_store['지역']}",
        f"목표      {format_won(worst_store['목표'])}",
        f"매출      {format_won(worst_store['매출'])}",
        f"진도율    {format_pct(worst_store['진도율'])}",
    ]

    y_cursor = box_y + 103
    for line in low_lines:
        draw.text((right_x + 24, y_cursor), line, fill=gray, font=small_font)
        y_cursor += 24

    # 코멘트
    comment_y = 665
    draw.text((60, comment_y - 42), "Store Comment", fill=white, font=section_font)

    draw.rounded_rectangle(
        [(60, comment_y), (1540, 842)],
        radius=24,
        fill=card_color,
        outline=border_color,
        width=2
    )

    y_cursor = comment_y + 24

    for idx, comment in enumerate(comments[:4], start=1):
        draw.text((90, y_cursor), f"{idx}.", fill=point_green, font=body_bold_font)

        wrapped = textwrap.wrap(comment, width=86)
        line_x = 128

        for line in wrapped[:2]:
            draw.text((line_x, y_cursor), line, fill=gray, font=body_font)
            y_cursor += 25

        y_cursor += 8

    footer_left = f"TOP REGION: {top_region} · 진도율 {format_pct(top_region_progress)}"
    footer_right = "Generated by MD Allboard"

    draw.text((60, 862), footer_left, fill=muted, font=small_font)

    footer_right_width = draw.textlength(footer_right, font=small_font)
    draw.text((1540 - footer_right_width, 862), footer_right, fill=muted, font=small_font)

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
    "요약 리포트용 매장 데이터 업로드",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    uploaded_df = load_uploaded_store_file(uploaded_file)
    df = prepare_store_data(uploaded_df)
    st.sidebar.success("업로드 데이터 적용됨")
else:
    df = create_sample_store_data()
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
# 8. 매장 요약 데이터 생성
# =====================================================
store_summary = filtered.groupby(
    ["지역", "매장"],
    as_index=False
).agg({
    "일목표": "sum",
    "일매출": "sum",
    "방문객수": "sum",
    "구매건수": "sum"
})

store_summary = store_summary.rename(columns={
    "일목표": "목표",
    "일매출": "매출"
})

store_summary["진도율"] = np.where(
    store_summary["목표"] > 0,
    store_summary["매출"] / store_summary["목표"],
    0
)

store_summary["객단가"] = np.where(
    store_summary["구매건수"] > 0,
    store_summary["매출"] / store_summary["구매건수"],
    0
)

store_summary["전환율"] = np.where(
    store_summary["방문객수"] > 0,
    store_summary["구매건수"] / store_summary["방문객수"],
    0
)

region_summary = store_summary.groupby(
    "지역",
    as_index=False
).agg({
    "목표": "sum",
    "매출": "sum",
    "방문객수": "sum",
    "구매건수": "sum"
})

region_summary["진도율"] = np.where(
    region_summary["목표"] > 0,
    region_summary["매출"] / region_summary["목표"],
    0
)

region_summary["객단가"] = np.where(
    region_summary["구매건수"] > 0,
    region_summary["매출"] / region_summary["구매건수"],
    0
)

region_summary["전환율"] = np.where(
    region_summary["방문객수"] > 0,
    region_summary["구매건수"] / region_summary["방문객수"],
    0
)

if store_summary.empty:
    st.warning("요약 가능한 매장 데이터가 없습니다.")
    st.stop()

total_target = store_summary["목표"].sum()
total_sales = store_summary["매출"].sum()
avg_progress = total_sales / total_target if total_target > 0 else 0
store_count = store_summary["매장"].nunique()
region_count = store_summary["지역"].nunique()

risk_stores = store_summary[store_summary["진도율"] < 0.8]
good_stores = store_summary[store_summary["진도율"] >= 1.0]

best_store = store_summary.sort_values("진도율", ascending=False).iloc[0]
worst_store = store_summary.sort_values("진도율", ascending=True).iloc[0]

top_region_row = region_summary.sort_values("진도율", ascending=False).iloc[0]
top_region = top_region_row["지역"]
top_region_progress = top_region_row["진도율"]

# =====================================================
# 9. 자동 코멘트 생성
# =====================================================
comments = []

risk_ratio = len(risk_stores) / store_count if store_count > 0 else 0
good_ratio = len(good_stores) / store_count if store_count > 0 else 0

# 1. 전체 진도율
comments.append(
    f"평균 진도율: {format_pct(avg_progress)}"
)

# 2. BEST 지역
comments.append(
    f"BEST 지역: {top_region} / {format_pct(top_region_progress)}"
)

# 3. BEST 매장
comments.append(
    f"BEST 매장: {best_store['매장']} / {format_pct(best_store['진도율'])}"
)

# 4. LOW 매장
comments.append(
    f"LOW 매장: {worst_store['매장']} / {format_pct(worst_store['진도율'])}"
)

# 5. 위험 매장
if len(risk_stores) > 0:
    comments.append(
        f"위험 매장: {len(risk_stores)}개 / 전체 {risk_ratio * 100:.1f}%"
    )
else:
    comments.append(
        "위험 매장: 없음"
    )

# 6. 목표달성 매장
if len(good_stores) > 0:
    comments.append(
        f"목표달성: {len(good_stores)}개 / 전체 {good_ratio * 100:.1f}%"
    )
else:
    comments.append(
        "목표달성: 없음"
    )

# 7. 우선 액션
if avg_progress < 0.8:
    comments.append(
        "우선 액션: 전 매장 매출 보강"
    )
elif len(risk_stores) > 0:
    comments.append(
        "우선 액션: 하위 매장 집중 점검"
    )
elif len(good_stores) >= store_count * 0.5:
    comments.append(
        "우선 액션: 우수 매장 방식 확산"
    )
else:
    comments.append(
        "우선 액션: 진도율 균형 관리"
    )

# =====================================================
# 10. 헤더
# =====================================================
st.markdown('<div class="title">🏬 Store Weekly Summary</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">보고용 매장 핵심 요약 페이지 / 기준: {view_type} · {period_label}</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 11. KPI
# =====================================================
st.markdown('<div class="section-title">① 핵심 KPI</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card("총 목표", format_won(total_target), f"{view_type} 기준")

with c2:
    kpi_card("총 매출", format_won(total_sales), "실적 합계")

with c3:
    kpi_card("평균 진도율", format_pct(avg_progress), "목표 대비")

with c4:
    kpi_card("위험 매장", f"{len(risk_stores):,}개", "진도율 80% 미만")

c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card("분석 매장 수", f"{store_count:,}개", "대상 매장")

with c6:
    kpi_card("분석 지역 수", f"{region_count:,}개", "대상 지역")

with c7:
    kpi_card("BEST 지역", top_region, f"진도율 {format_pct(top_region_progress)}")

with c8:
    kpi_card("목표달성 매장", f"{len(good_stores):,}개", "진도율 100% 이상")

# =====================================================
# 12. BEST / LOW 요약
# =====================================================
st.markdown('<div class="section-title">② BEST / LOW 매장 요약</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">🏆 진도율 BEST 매장</div>
        <div class="summary-text">
            매장명: <b>{best_store['매장']}</b><br>
            지역: {best_store['지역']}<br>
            목표: {format_won(best_store['목표'])}<br>
            매출: {format_won(best_store['매출'])}<br>
            진도율: {format_pct(best_store['진도율'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">⚠️ 진도율 LOW 매장</div>
        <div class="summary-text">
            매장명: <b>{worst_store['매장']}</b><br>
            지역: {worst_store['지역']}<br>
            목표: {format_won(worst_store['목표'])}<br>
            매출: {format_won(worst_store['매출'])}<br>
            진도율: {format_pct(worst_store['진도율'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 13. 자동 코멘트
# =====================================================
st.markdown('<div class="section-title">③ Store 자동 코멘트</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">④ 지역 / 매장 상세 테이블</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📍 지역별 요약", "🏬 매장별 요약", "⚠️ 위험 매장"])


def display_store_table(input_df):
    display = input_df.copy()

    if "목표" in display.columns:
        display["목표"] = display["목표"].apply(format_won)
    if "매출" in display.columns:
        display["매출"] = display["매출"].apply(format_won)
    if "진도율" in display.columns:
        display["진도율"] = display["진도율"].apply(format_pct)
    if "객단가" in display.columns:
        display["객단가"] = display["객단가"].apply(format_won)
    if "전환율" in display.columns:
        display["전환율"] = display["전환율"].apply(format_pct)
    if "방문객수" in display.columns:
        display["방문객수"] = display["방문객수"].apply(lambda x: f"{x:,.0f}명")
    if "구매건수" in display.columns:
        display["구매건수"] = display["구매건수"].apply(lambda x: f"{x:,.0f}건")

    return display


with tab1:
    st.dataframe(
        display_store_table(region_summary),
        use_container_width=True,
        height=280
    )

with tab2:
    st.dataframe(
        display_store_table(store_summary.sort_values("진도율", ascending=False)),
        use_container_width=True,
        height=360
    )

with tab3:
    st.dataframe(
        display_store_table(risk_stores.sort_values("진도율", ascending=True)),
        use_container_width=True,
        height=320
    )

# =====================================================
# 15. 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑤ 보고용 다운로드</div>', unsafe_allow_html=True)

summary_df = pd.DataFrame({
    "항목": [
        "총 목표",
        "총 매출",
        "평균 진도율",
        "위험 매장 수",
        "분석 매장 수",
        "분석 지역 수",
        "BEST 지역",
        "목표달성 매장 수"
    ],
    "값": [
        total_target,
        total_sales,
        avg_progress,
        len(risk_stores),
        store_count,
        region_count,
        top_region,
        len(good_stores)
    ]
})

excel_file = create_store_summary_excel(
    summary_df=summary_df,
    region_summary=region_summary,
    store_summary=store_summary,
    comments=comments
)

st.download_button(
    label="📊 Store Summary 엑셀 다운로드",
    data=excel_file,
    file_name=f"store_summary_report_{view_type}_{period_label}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

png_file = create_store_summary_png(
    view_type=view_type,
    period_label=period_label,
    total_target=total_target,
    total_sales=total_sales,
    avg_progress=avg_progress,
    risk_store_count=len(risk_stores),
    top_region=top_region,
    top_region_progress=top_region_progress,
    best_store=best_store,
    worst_store=worst_store,
    comments=comments
)

st.download_button(
    label="🖼️ Store Summary 이미지 다운로드",
    data=png_file,
    file_name=f"store_summary_report_{view_type}_{period_label}.png",
    mime="image/png"
)

st.caption("Store Weekly Summary · 보고용 매장 핵심 요약 페이지")