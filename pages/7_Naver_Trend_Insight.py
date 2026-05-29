import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import urllib.request
import urllib.error
import json
from datetime import datetime, timedelta
from io import BytesIO

# =====================================================
# 1. 페이지 설정
# =====================================================
st.set_page_config(
    page_title="Naver Trend Insight",
    page_icon="🔎",
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

    .title {
        font-size: 38px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 15px;
        color: #E5E7EB;
        margin-bottom: 20px;
        line-height: 1.6;
    }

    .section-title {
        font-size: 24px;
        font-weight: 850;
        color: #FFFFFF;
        margin-top: 28px;
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

    .comment-box {
        background-color: #171B26;
        border: 1px solid #2A2F3A;
        border-radius: 18px;
        padding: 22px 26px;
        margin-top: 10px;
        margin-bottom: 26px;
    }

    .comment-line {
        color: #E5E7EB;
        font-size: 15px;
        line-height: 1.75;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. 공통 함수
# =====================================================
def kpi_card(label, value, sub_text=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)


def format_pct(value):
    try:
        return f"{float(value):.1f}%"
    except:
        return "0.0%"


def apply_dark_chart_style(fig, height=430):
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=20, b=20),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(size=14, color="#FFFFFF"),
        xaxis=dict(
            title=None,
            tickfont=dict(size=13, color="#E5E7EB"),
            gridcolor="#262730",
            zerolinecolor="#262730"
        ),
        yaxis=dict(
            title="검색 관심도",
            tickfont=dict(size=13, color="#E5E7EB"),
            title_font=dict(size=14, color="#FFFFFF"),
            gridcolor="#262730",
            zerolinecolor="#262730"
        ),
        legend=dict(
            font=dict(size=12, color="#FFFFFF"),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.25
        )
    )
    return fig


def get_naver_secrets():
    try:
        client_id = st.secrets["NAVER_CLIENT_ID"]
        client_secret = st.secrets["NAVER_CLIENT_SECRET"]
        return client_id, client_secret
    except Exception:
        return None, None


def parse_keyword_groups(raw_text):
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    groups = []

    for line in lines:
        # 예: 레인부츠: 레인부츠, 장화, 여성 레인부츠
        if ":" in line:
            group_name, keyword_text = line.split(":", 1)
            group_name = group_name.strip()
            keywords = [
                keyword.strip()
                for keyword in keyword_text.split(",")
                if keyword.strip()
            ]
        else:
            group_name = line
            keywords = [line]

        if group_name and keywords:
            groups.append({
                "groupName": group_name,
                "keywords": keywords[:20]
            })

    return groups[:5]


def call_naver_datalab_api(
    client_id,
    client_secret,
    start_date,
    end_date,
    time_unit,
    keyword_groups,
    device=None,
    gender=None,
    ages=None
):
    url = "https://openapi.naver.com/v1/datalab/search"

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }

    if device and device != "전체":
        body["device"] = device

    if gender and gender != "전체":
        body["gender"] = gender

    if ages:
        body["ages"] = ages

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")

    data = json.dumps(body).encode("utf-8")

    try:
        response = urllib.request.urlopen(request, data=data, timeout=15)
        response_body = response.read().decode("utf-8")
        return json.loads(response_body), None

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return None, f"HTTP Error {e.code}: {error_body}"

    except Exception as e:
        return None, str(e)


def convert_api_result_to_df(api_result):
    rows = []

    for result in api_result.get("results", []):
        group_name = result.get("title", "")
        keywords = ", ".join(result.get("keywords", []))

        for item in result.get("data", []):
            rows.append({
                "키워드그룹": group_name,
                "검색어": keywords,
                "기간": item.get("period"),
                "관심도": item.get("ratio", 0)
            })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["기간"] = pd.to_datetime(df["기간"])
        df["관심도"] = pd.to_numeric(df["관심도"], errors="coerce").fillna(0)

    return df


def make_trend_summary(trend_df):
    summary_rows = []

    for group_name, group_df in trend_df.groupby("키워드그룹"):
        group_df = group_df.sort_values("기간").reset_index(drop=True)

        n = len(group_df)
        window = max(1, int(n * 0.2))

        start_avg = group_df.head(window)["관심도"].mean()
        end_avg = group_df.tail(window)["관심도"].mean()
        max_value = group_df["관심도"].max()
        avg_value = group_df["관심도"].mean()

        change = end_avg - start_avg
        change_rate = (change / start_avg * 100) if start_avg > 0 else 0

        if change_rate >= 30:
            status = "급상승"
        elif change_rate >= 10:
            status = "상승"
        elif change_rate <= -30:
            status = "급하락"
        elif change_rate <= -10:
            status = "하락"
        else:
            status = "유지"

        summary_rows.append({
            "키워드그룹": group_name,
            "초반평균": start_avg,
            "최근평균": end_avg,
            "변화폭": change,
            "변화율": change_rate,
            "최고관심도": max_value,
            "평균관심도": avg_value,
            "상태": status
        })

    summary_df = pd.DataFrame(summary_rows)

    if not summary_df.empty:
        summary_df = summary_df.sort_values(
            ["변화율", "최근평균"],
            ascending=[False, False]
        ).reset_index(drop=True)

    return summary_df


def make_md_comments(summary_df):
    comments = []

    if summary_df.empty:
        return ["데이터 없음"]

    top_rising = summary_df.sort_values("변화율", ascending=False).iloc[0]
    top_interest = summary_df.sort_values("최근평균", ascending=False).iloc[0]
    falling_df = summary_df[summary_df["상태"].isin(["하락", "급하락"])]
    rising_df = summary_df[summary_df["상태"].isin(["상승", "급상승"])]

    comments.append(
        f"급상승 키워드: {top_rising['키워드그룹']} / {top_rising['변화율']:.1f}%"
    )

    comments.append(
        f"관심도 TOP: {top_interest['키워드그룹']} / {top_interest['최근평균']:.1f}"
    )

    if len(rising_df) > 0:
        comments.append(
            f"상승 키워드: {len(rising_df)}개"
        )
    else:
        comments.append(
            "상승 키워드: 없음"
        )

    if len(falling_df) > 0:
        comments.append(
            f"하락 키워드: {len(falling_df)}개"
        )
    else:
        comments.append(
            "하락 키워드: 없음"
        )

    status = top_rising["상태"]
    keyword = top_rising["키워드그룹"]

    if status in ["급상승", "상승"]:
        comments.append(
            f"MD 적용: {keyword} 상품화 검토"
        )
    elif status in ["급하락", "하락"]:
        comments.append(
            f"MD 적용: {keyword} 물량 보수적 운영"
        )
    else:
        comments.append(
            f"MD 적용: {keyword} 반응 유지 관찰"
        )

    comments.append(
        "우선 액션: 상승 키워드 상품/콘텐츠 연결"
    )

    return comments


def create_excel_download(trend_df, summary_df, comments):
    output = BytesIO()

    comment_df = pd.DataFrame({
        "MD 코멘트": comments
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        trend_df.to_excel(writer, index=False, sheet_name="트렌드데이터")
        summary_df.to_excel(writer, index=False, sheet_name="요약")
        comment_df.to_excel(writer, index=False, sheet_name="MD코멘트")

    output.seek(0)
    return output


# =====================================================
# 4. 사이드바 입력
# =====================================================
st.sidebar.markdown("---")
st.sidebar.title("🔎 Naver Trend 설정")

default_keywords = """레인부츠: 레인부츠, 장화, 여성 레인부츠
바람막이: 바람막이, 여성 바람막이
버뮤다팬츠: 버뮤다팬츠, 여성 버뮤다팬츠
인형키링: 인형키링, 키링, 백참
크롭셔츠: 크롭셔츠, 여성 셔츠"""

keyword_text = st.sidebar.text_area(
    "키워드 그룹 입력",
    value=default_keywords,
    height=180
)

today = datetime.today().date()
default_start = today - timedelta(days=90)

start_date = st.sidebar.date_input(
    "시작일",
    value=default_start
)

end_date = st.sidebar.date_input(
    "종료일",
    value=today
)

time_unit_label = st.sidebar.radio(
    "조회 단위",
    ["일간", "주간", "월간"],
    horizontal=True
)

time_unit_map = {
    "일간": "date",
    "주간": "week",
    "월간": "month"
}

time_unit = time_unit_map[time_unit_label]

device_label = st.sidebar.selectbox(
    "기기",
    ["전체", "pc", "mo"],
    index=0
)

gender_label = st.sidebar.selectbox(
    "성별",
    ["전체", "m", "f"],
    index=0
)

age_options = {
    "전체": [],
    "10대": ["1", "2"],
    "20대": ["3", "4"],
    "30대": ["5", "6"],
    "40대": ["7", "8"],
    "50대+": ["9", "10", "11"]
}

age_label = st.sidebar.selectbox(
    "연령",
    list(age_options.keys()),
    index=0
)

run_button = st.sidebar.button("네이버 트렌드 조회", type="primary")

# =====================================================
# 5. 헤더
# =====================================================
st.markdown('<div class="title">🔎 Naver Trend Insight</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">네이버 데이터랩 검색어 트렌드를 가져와 키워드 상승/하락을 보고, MD 적용 방향으로 변환하는 페이지입니다.</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 6. API 키 확인
# =====================================================
client_id, client_secret = get_naver_secrets()

if not client_id or not client_secret:
    st.error("네이버 API 키가 없습니다. `.streamlit/secrets.toml`에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET을 넣어주세요.")
    st.stop()

keyword_groups = parse_keyword_groups(keyword_text)

if not keyword_groups:
    st.warning("키워드를 1개 이상 입력해주세요.")
    st.stop()

if len(keyword_groups) > 5:
    st.warning("네이버 데이터랩 검색어 그룹은 최대 5개까지만 사용하도록 제한했습니다.")

# =====================================================
# 7. API 호출
# =====================================================
if run_button:
    with st.spinner("네이버 데이터랩 API 호출 중..."):
        api_result, error = call_naver_datalab_api(
            client_id=client_id,
            client_secret=client_secret,
            start_date=str(start_date),
            end_date=str(end_date),
            time_unit=time_unit,
            keyword_groups=keyword_groups,
            device=device_label,
            gender=gender_label,
            ages=age_options[age_label]
        )

    if error:
        st.error("네이버 API 호출 실패")
        st.code(error)
        st.stop()

    trend_df = convert_api_result_to_df(api_result)

    if trend_df.empty:
        st.warning("조회 결과가 없습니다. 키워드나 기간을 확인해주세요.")
        st.stop()

    st.session_state["naver_trend_df"] = trend_df
    st.session_state["naver_keyword_groups"] = keyword_groups
    st.session_state["naver_period"] = f"{start_date} ~ {end_date}"
    st.session_state["naver_time_unit_label"] = time_unit_label

# =====================================================
# 8. 결과 표시
# =====================================================
if "naver_trend_df" not in st.session_state:
    st.info("왼쪽에서 키워드와 기간을 설정한 뒤 `네이버 트렌드 조회` 버튼을 눌러주세요.")
    st.stop()

trend_df = st.session_state["naver_trend_df"]
summary_df = make_trend_summary(trend_df)
comments = make_md_comments(summary_df)

period_text = st.session_state.get("naver_period", "")
unit_text = st.session_state.get("naver_time_unit_label", "")

# =====================================================
# 9. KPI
# =====================================================
top_rising = summary_df.sort_values("변화율", ascending=False).iloc[0]
top_interest = summary_df.sort_values("최근평균", ascending=False).iloc[0]
rising_count = len(summary_df[summary_df["상태"].isin(["상승", "급상승"])])
falling_count = len(summary_df[summary_df["상태"].isin(["하락", "급하락"])])

st.markdown('<div class="section-title">① 트렌드 핵심 요약</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card("급상승 키워드", top_rising["키워드그룹"], f"변화율 {top_rising['변화율']:.1f}%")

with c2:
    kpi_card("관심도 TOP", top_interest["키워드그룹"], f"최근평균 {top_interest['최근평균']:.1f}")

with c3:
    kpi_card("상승 키워드", f"{rising_count}개", "상승/급상승 기준")

with c4:
    kpi_card("하락 키워드", f"{falling_count}개", "하락/급하락 기준")

# =====================================================
# 10. 그래프
# =====================================================
st.markdown('<div class="section-title">② 키워드 트렌드 그래프</div>', unsafe_allow_html=True)

fig = px.line(
    trend_df,
    x="기간",
    y="관심도",
    color="키워드그룹",
    markers=True
)

fig.update_traces(
    line=dict(width=3),
    marker=dict(size=7)
)

fig = apply_dark_chart_style(fig, height=480)
st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 11. 요약 테이블
# =====================================================
st.markdown('<div class="section-title">③ 키워드별 상승/하락 요약</div>', unsafe_allow_html=True)

display_summary = summary_df.copy()
display_summary["초반평균"] = display_summary["초반평균"].map(lambda x: f"{x:.1f}")
display_summary["최근평균"] = display_summary["최근평균"].map(lambda x: f"{x:.1f}")
display_summary["변화폭"] = display_summary["변화폭"].map(lambda x: f"{x:.1f}")
display_summary["변화율"] = display_summary["변화율"].map(lambda x: f"{x:.1f}%")
display_summary["최고관심도"] = display_summary["최고관심도"].map(lambda x: f"{x:.1f}")
display_summary["평균관심도"] = display_summary["평균관심도"].map(lambda x: f"{x:.1f}")

st.dataframe(
    display_summary,
    use_container_width=True,
    height=300
)

# =====================================================
# 12. MD 코멘트
# =====================================================
st.markdown('<div class="section-title">④ MD 적용 코멘트</div>', unsafe_allow_html=True)

comment_lines = ""

for idx, comment in enumerate(comments, start=1):
    comment_lines += (
        f'<p class="comment-line">'
        f'<b style="color:#FFFFFF;">{idx}.</b> {comment}'
        f'</p>'
    )

comment_box = f"""
<div class="comment-box">
    {comment_lines}
</div>
"""

st.markdown(comment_box, unsafe_allow_html=True)

# =====================================================
# 13. 원본 데이터
# =====================================================
with st.expander("📌 원본 트렌드 데이터 확인", expanded=False):
    st.write(f"조회 기간: {period_text}")
    st.write(f"조회 단위: {unit_text}")
    st.dataframe(
        trend_df,
        use_container_width=True,
        height=360
    )

# =====================================================
# 14. 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑤ 다운로드</div>', unsafe_allow_html=True)

excel_file = create_excel_download(
    trend_df=trend_df,
    summary_df=summary_df,
    comments=comments
)

st.download_button(
    label="📥 Naver Trend Insight 엑셀 다운로드",
    data=excel_file,
    file_name="naver_trend_insight.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Naver Trend Insight · Search Trend / Keyword Change / MD Action")