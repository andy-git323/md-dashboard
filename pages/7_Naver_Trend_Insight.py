import streamlit as st
import pandas as pd
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

    .insight-card {
        background: linear-gradient(135deg, #171B26 0%, #111827 100%);
        border: 1px solid #2A2F3A;
        border-radius: 22px;
        padding: 26px 30px;
        margin-top: 10px;
        margin-bottom: 28px;
        box-shadow: 0px 4px 16px rgba(0,0,0,0.28);
    }

    .insight-label {
        font-size: 13px;
        color: #9CA3AF;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }

    .insight-title {
        font-size: 30px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 16px;
    }

    .insight-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-top: 18px;
    }

    .insight-item {
        background-color: #0E1117;
        border: 1px solid #2A2F3A;
        border-radius: 14px;
        padding: 14px 16px;
    }

    .insight-item-label {
        font-size: 12px;
        color: #9CA3AF;
        margin-bottom: 6px;
    }

    .insight-item-value {
        font-size: 17px;
        font-weight: 800;
        color: #FFFFFF;
    }

    .insight-action {
        margin-top: 18px;
        background-color: #1F2937;
        border-left: 5px solid #F59E0B;
        padding: 16px 18px;
        border-radius: 12px;
        color: #FFFFFF;
        font-size: 17px;
        font-weight: 800;
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


def apply_dark_chart_style(fig, height=430, y_title="검색 관심도"):
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
            title=y_title,
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


# =====================================================
# 4. MD 매핑 함수
# =====================================================
def get_md_mapping(keyword):
    keyword = str(keyword).lower()

    mapping_rules = [
        {
            "keywords": ["레인부츠", "장화", "rain"],
            "category": "SHOES",
            "sub_category": "RAIN BOOTS",
            "season": "장마 / 여름",
            "action": "소량 테스트"
        },
        {
            "keywords": ["바람막이", "윈드브레이커", "windbreaker"],
            "category": "OUTER",
            "sub_category": "WINDBREAKER",
            "season": "봄 / 가을",
            "action": "간절기 상품 검토"
        },
        {
            "keywords": ["버뮤다", "버뮤다팬츠", "쇼츠", "반바지"],
            "category": "BOTTOM",
            "sub_category": "SHORTS",
            "season": "여름",
            "action": "하의 실루엣 반영"
        },
        {
            "keywords": ["키링", "인형키링", "백참", "bag charm"],
            "category": "GOODS",
            "sub_category": "KEYRING",
            "season": "상시",
            "action": "굿즈 테스트"
        },
        {
            "keywords": ["크롭", "크롭셔츠", "셔츠"],
            "category": "TOP",
            "sub_category": "SHIRT",
            "season": "봄 / 여름",
            "action": "스타일링 반응 확인"
        },
        {
            "keywords": ["가디건", "니트"],
            "category": "TOP",
            "sub_category": "KNIT",
            "season": "봄 / 가을",
            "action": "간절기 TOP 검토"
        },
        {
            "keywords": ["후드", "후드티", "맨투맨", "스웨트"],
            "category": "TOP",
            "sub_category": "SWEAT",
            "season": "가을 / 겨울",
            "action": "기본물 운영 검토"
        },
        {
            "keywords": ["가방", "백", "토트백", "숄더백"],
            "category": "ACC",
            "sub_category": "BAG",
            "season": "상시",
            "action": "ACC 확장 검토"
        },
        {
            "keywords": ["향수", "디퓨저", "프래그런스", "fragrance"],
            "category": "BEAUTY",
            "sub_category": "FRAGRANCE",
            "season": "상시",
            "action": "라이프스타일 확장"
        }
    ]

    for rule in mapping_rules:
        for word in rule["keywords"]:
            if word in keyword:
                return {
                    "MD카테고리": rule["category"],
                    "세부카테고리": rule["sub_category"],
                    "시즌": rule["season"],
                    "기본액션": rule["action"]
                }

    return {
        "MD카테고리": "ETC",
        "세부카테고리": "기타",
        "시즌": "확인 필요",
        "기본액션": "추가 검토"
    }


def get_season_fit_score(season_text, today_date):
    month = today_date.month
    season_text = str(season_text)

    if month in [3, 4, 5]:
        current_season = "봄"
    elif month in [6, 7, 8]:
        current_season = "여름"
    elif month in [9, 10, 11]:
        current_season = "가을"
    else:
        current_season = "겨울"

    if "상시" in season_text:
        return 80

    if current_season in season_text:
        return 100

    next_season_map = {
        "봄": "여름",
        "여름": "가을",
        "가을": "겨울",
        "겨울": "봄"
    }

    next_season = next_season_map.get(current_season)

    if next_season and next_season in season_text:
        return 85

    if "확인 필요" in season_text:
        return 50

    return 50


def calculate_action_score(recent_avg, change_rate, season_score):
    interest_score = min(max(float(recent_avg), 0), 100)
    change_score = min(max((float(change_rate) + 100) / 2, 0), 100)

    action_score = (
        interest_score * 0.4 +
        change_score * 0.4 +
        season_score * 0.2
    )

    return round(action_score, 1)


def get_action_decision(action_score):
    if action_score >= 80:
        return "즉시 검토"
    elif action_score >= 60:
        return "모니터링"
    elif action_score >= 40:
        return "보류"
    else:
        return "제외"


# =====================================================
# 5. 네이버 API
# =====================================================
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


# =====================================================
# 6. 분석 함수
# =====================================================
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

        md_mapping = get_md_mapping(group_name)

        season_score = get_season_fit_score(
            md_mapping["시즌"],
            datetime.today().date()
        )

        action_score = calculate_action_score(
            recent_avg=end_avg,
            change_rate=change_rate,
            season_score=season_score
        )

        action_decision = get_action_decision(action_score)

        summary_rows.append({
            "키워드그룹": group_name,
            "MD카테고리": md_mapping["MD카테고리"],
            "세부카테고리": md_mapping["세부카테고리"],
            "시즌": md_mapping["시즌"],
            "기본액션": md_mapping["기본액션"],
            "상태": status,
            "Action Score": action_score,
            "판단": action_decision,
            "시즌적합도": season_score,
            "초반평균": start_avg,
            "최근평균": end_avg,
            "변화폭": change,
            "변화율": change_rate,
            "최고관심도": max_value,
            "평균관심도": avg_value
        })

    summary_df = pd.DataFrame(summary_rows)

    if not summary_df.empty:
        summary_df = summary_df.sort_values(
            ["Action Score", "변화율", "최근평균"],
            ascending=[False, False, False]
        ).reset_index(drop=True)

    return summary_df


def make_md_comments(summary_df):
    comments = []

    if summary_df.empty:
        return ["데이터 없음"]

    top_action = summary_df.sort_values("Action Score", ascending=False).iloc[0]

    rising_df = summary_df[summary_df["상태"].isin(["상승", "급상승"])]
    falling_df = summary_df[summary_df["상태"].isin(["하락", "급하락"])]
    monitor_df = summary_df[summary_df["판단"].isin(["즉시 검토", "모니터링"])]

    # 카테고리 요약
    if not monitor_df.empty:
        main_categories = (
            monitor_df["MD카테고리"]
            .value_counts()
            .head(2)
            .index
            .tolist()
        )
        category_text = " / ".join(main_categories)
    else:
        category_text = top_action["MD카테고리"]

    # 시즌 요약
    season_candidates = (
        summary_df["시즌"]
        .value_counts()
        .head(2)
        .index
        .tolist()
    )
    season_text = " / ".join(season_candidates)

    # 상승 키워드 요약
    if not rising_df.empty:
        rising_keywords = ", ".join(rising_df["키워드그룹"].head(3).tolist())
    else:
        rising_keywords = "없음"

    # 하락 키워드 요약
    if not falling_df.empty:
        falling_keywords = ", ".join(falling_df["키워드그룹"].head(3).tolist())
    else:
        falling_keywords = "없음"

    comments.append(
        f"상품기획: {category_text} 중심 검토"
    )

    comments.append(
        f"시즌 방향: {season_text} 키워드 확인"
    )

    comments.append(
        f"상승 키워드: {rising_keywords}"
    )

    comments.append(
        f"주의 키워드: {falling_keywords}"
    )

    if len(monitor_df) > 0:
        comments.append(
            f"우선 검토: {len(monitor_df)}개 키워드"
        )
    else:
        comments.append(
            "우선 검토: 신규 확대보다 관찰"
        )

    if top_action["판단"] == "즉시 검토":
        comments.append(
            "소싱 방향: 빠른 샘플 / 소량 테스트"
        )
    elif top_action["판단"] == "모니터링":
        comments.append(
            "소싱 방향: 즉시 발주보다 반응 추적"
        )
    else:
        comments.append(
            "소싱 방향: 물량 확대 보류"
        )

    comments.append(
        "콘텐츠 방향: 상승 키워드 중심 스타일링 노출"
    )

    comments.append(
        "다음 액션: 상위 2개 키워드만 우선 검토"
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
# 7. 사이드바 입력
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
# 8. 헤더
# =====================================================
st.markdown('<div class="title">🔎 Naver Trend Insight</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">네이버 데이터랩 검색어 트렌드를 가져와 키워드 상승/하락을 보고, MD 적용 방향으로 변환하는 페이지입니다.</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 9. API 키 확인
# =====================================================
client_id, client_secret = get_naver_secrets()

if not client_id or not client_secret:
    st.error("네이버 API 키가 없습니다. `.streamlit/secrets.toml`에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET을 넣어주세요.")
    st.stop()

keyword_groups = parse_keyword_groups(keyword_text)

if not keyword_groups:
    st.warning("키워드를 1개 이상 입력해주세요.")
    st.stop()

# =====================================================
# 10. API 호출
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
# 11. 결과 표시
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
# 12. KPI
# =====================================================
top_action = summary_df.sort_values("Action Score", ascending=False).iloc[0]
top_rising = summary_df.sort_values("변화율", ascending=False).iloc[0]
top_interest = summary_df.sort_values("최근평균", ascending=False).iloc[0]
lowest_action = summary_df.sort_values("Action Score", ascending=True).iloc[0]

rising_count = len(summary_df[summary_df["상태"].isin(["상승", "급상승"])])
falling_count = len(summary_df[summary_df["상태"].isin(["하락", "급하락"])])

st.markdown('<div class="section-title">① 트렌드 핵심 요약</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(
        "Action TOP",
        top_action["키워드그룹"],
        f"{top_action['Action Score']:.1f}점 / {top_action['판단']}"
    )

with c2:
    kpi_card(
        "급상승 키워드",
        top_rising["키워드그룹"],
        f"변화율 {top_rising['변화율']:.1f}%"
    )

with c3:
    kpi_card(
        "관심도 TOP",
        top_interest["키워드그룹"],
        f"최근평균 {top_interest['최근평균']:.1f}"
    )

with c4:
    kpi_card(
        "상승 / 하락",
        f"{rising_count} / {falling_count}",
        "상승·급상승 / 하락·급하락"
    )

# =====================================================
# 13. 오늘의 MD 인사이트
# =====================================================
st.markdown('<div class="section-title">② 오늘의 MD 인사이트</div>', unsafe_allow_html=True)

insight_html = f"""
<div class="insight-card">
<div class="insight-label">TODAY TREND INSIGHT</div>
<div class="insight-title">{top_action['키워드그룹']} 중심으로 검토</div>

<div class="insight-grid">

<div class="insight-item">
<div class="insight-item-label">Action Score</div>
<div class="insight-item-value">{top_action['Action Score']:.1f}점</div>
</div>

<div class="insight-item">
<div class="insight-item-label">판단</div>
<div class="insight-item-value">{top_action['판단']}</div>
</div>

<div class="insight-item">
<div class="insight-item-label">적용 카테고리</div>
<div class="insight-item-value">{top_action['MD카테고리']} / {top_action['세부카테고리']}</div>
</div>

<div class="insight-item">
<div class="insight-item-label">시즌 연결</div>
<div class="insight-item-value">{top_action['시즌']}</div>
</div>

<div class="insight-item">
<div class="insight-item-label">급상승 키워드</div>
<div class="insight-item-value">{top_rising['키워드그룹']} / {top_rising['변화율']:.1f}%</div>
</div>

<div class="insight-item">
<div class="insight-item-label">주의 키워드</div>
<div class="insight-item-value">{lowest_action['키워드그룹']} / {lowest_action['Action Score']:.1f}점</div>
</div>

</div>

<div class="insight-action">
우선 액션: {top_action['기본액션']}
</div>
</div>
"""

st.markdown(insight_html, unsafe_allow_html=True)

# =====================================================
# 14. 키워드 트렌드 그래프
# =====================================================
st.markdown('<div class="section-title">③ 키워드 트렌드 그래프</div>', unsafe_allow_html=True)

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

fig = apply_dark_chart_style(fig, height=480, y_title="검색 관심도")
st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 15. Action Score 랭킹 차트
# =====================================================
st.markdown('<div class="section-title">④ MD Action Score Ranking</div>', unsafe_allow_html=True)

fig_score = px.bar(
    summary_df.sort_values("Action Score", ascending=True),
    x="Action Score",
    y="키워드그룹",
    color="판단",
    orientation="h",
    text="Action Score",
    color_discrete_map={
        "즉시 검토": "#EF4444",
        "모니터링": "#F59E0B",
        "보류": "#60A5FA",
        "제외": "#6B7280"
    }
)

fig_score.update_traces(
    texttemplate="%{text:.1f}점",
    textposition="outside",
    textfont=dict(color="#FFFFFF", size=14)
)

fig_score = apply_dark_chart_style(fig_score, height=360, y_title="키워드")
fig_score.update_layout(
    xaxis=dict(
        title="Action Score",
        range=[0, 105],
        tickfont=dict(size=13, color="#E5E7EB"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    ),
    yaxis=dict(
        title=None,
        tickfont=dict(size=14, color="#FFFFFF"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    )
)

st.plotly_chart(fig_score, use_container_width=True)

# =====================================================
# 16. 요약 테이블
# =====================================================
st.markdown('<div class="section-title">⑤ 키워드별 상승/하락 요약</div>', unsafe_allow_html=True)

display_summary = summary_df.copy()

display_summary["Action Score"] = display_summary["Action Score"].map(lambda x: f"{x:.1f}점")
display_summary["시즌적합도"] = display_summary["시즌적합도"].map(lambda x: f"{x:.0f}점")
display_summary["초반평균"] = display_summary["초반평균"].map(lambda x: f"{x:.1f}")
display_summary["최근평균"] = display_summary["최근평균"].map(lambda x: f"{x:.1f}")
display_summary["변화폭"] = display_summary["변화폭"].map(lambda x: f"{x:.1f}")
display_summary["변화율"] = display_summary["변화율"].map(lambda x: f"{x:.1f}%")
display_summary["최고관심도"] = display_summary["최고관심도"].map(lambda x: f"{x:.1f}")
display_summary["평균관심도"] = display_summary["평균관심도"].map(lambda x: f"{x:.1f}")

summary_columns = [
    "키워드그룹",
    "MD카테고리",
    "세부카테고리",
    "시즌",
    "기본액션",
    "상태",
    "Action Score",
    "판단",
    "시즌적합도",
    "초반평균",
    "최근평균",
    "변화폭",
    "변화율",
    "최고관심도",
    "평균관심도"
]

st.dataframe(
    display_summary[summary_columns],
    use_container_width=True,
    height=360
)

# =====================================================
# 17. MD 코멘트
# =====================================================
st.markdown('<div class="section-title">⑥ MD 적용 코멘트</div>', unsafe_allow_html=True)

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
# 18. 원본 데이터
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
# 19. 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑦ 다운로드</div>', unsafe_allow_html=True)

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