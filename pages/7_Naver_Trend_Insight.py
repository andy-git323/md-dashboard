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


def format_month_week(date_value):
    date_value = pd.to_datetime(date_value)
    week_num = ((date_value.day - 1) // 7) + 1
    return f"{date_value.month}월 {week_num}주차"


def shift_date_to_year(date_value, target_year):
    date_value = pd.to_datetime(date_value)

    try:
        return date_value.replace(year=target_year)
    except ValueError:
        return date_value + pd.DateOffset(years=target_year - date_value.year)


def get_trend_points(df):
    df = df.sort_values("기간").reset_index(drop=True)

    if df.empty:
        return None, None, None

    peak_idx = df["관심도"].idxmax()
    peak_row = df.loc[peak_idx]

    max_value = df["관심도"].max()
    avg_value = df["관심도"].mean()
    active_threshold = max(max_value * 0.35, avg_value * 1.1)

    before_peak = df[df["기간"] <= peak_row["기간"]]
    active_before = before_peak[before_peak["관심도"] >= active_threshold]

    if not active_before.empty:
        rising_row = active_before.iloc[0]
    else:
        rising_row = df.iloc[0]

    after_peak = df[df["기간"] > peak_row["기간"]]
    decline_candidates = after_peak[after_peak["관심도"] <= max_value * 0.6]

    if not decline_candidates.empty:
        decline_row = decline_candidates.iloc[0]
    else:
        decline_row = df.iloc[-1]

    return rising_row, peak_row, decline_row


def make_seasonal_planning(last_year_df, summary_df, target_year):
    if last_year_df is None or last_year_df.empty:
        return pd.DataFrame()

    planning_rows = []

    for group_name, group_df in last_year_df.groupby("키워드그룹"):
        group_df = group_df.sort_values("기간").reset_index(drop=True)

        if group_df.empty:
            continue

        rising_row, peak_row, decline_row = get_trend_points(group_df)

        if rising_row is None:
            continue

        rising_start_date = pd.to_datetime(rising_row["기간"])
        peak_date = pd.to_datetime(peak_row["기간"])
        decline_start_date = pd.to_datetime(decline_row["기간"])

        duration_weeks = max(
            1,
            int((decline_start_date - rising_start_date).days / 7)
        )

        peak_this_year = shift_date_to_year(peak_date, target_year)
        rising_this_year = shift_date_to_year(rising_start_date, target_year)
        decline_this_year = shift_date_to_year(decline_start_date, target_year)

        planning_start = peak_this_year - pd.DateOffset(months=6)
        sourcing_deadline = peak_this_year - pd.DateOffset(months=3)
        content_start = rising_this_year - pd.DateOffset(weeks=2)

        current_row = summary_df[summary_df["키워드그룹"] == group_name]

        if not current_row.empty:
            current_score = float(current_row.iloc[0]["Action Score"])
            current_decision = current_row.iloc[0]["판단"]
            md_category = current_row.iloc[0]["MD카테고리"]
            sub_category = current_row.iloc[0]["세부카테고리"]
            basic_action = current_row.iloc[0]["기본액션"]
        else:
            current_score = 0
            current_decision = "확인 필요"
            md_category = "ETC"
            sub_category = "기타"
            basic_action = "추가 검토"

        if duration_weeks >= 8 and current_score >= 60:
            repeat_level = "높음"
        elif duration_weeks >= 6 or current_score >= 50:
            repeat_level = "중간"
        else:
            repeat_level = "낮음"

        if duration_weeks >= 10:
            trend_type = "시즌 지속형"
        elif duration_weeks >= 5:
            trend_type = "시즌 단기형"
        else:
            trend_type = "단기 반응형"

        planning_rows.append({
            "키워드그룹": group_name,
            "MD카테고리": md_category,
            "세부카테고리": sub_category,
            "작년 상승 시작": format_month_week(rising_start_date),
            "작년 피크": format_month_week(peak_date),
            "작년 하락 시작": format_month_week(decline_start_date),
            "트렌드 지속": f"{duration_weeks}주",
            "트렌드 유형": trend_type,
            "올해 기획 시작": planning_start.strftime("%Y-%m-%d"),
            "올해 소싱/발주 마감": sourcing_deadline.strftime("%Y-%m-%d"),
            "올해 콘텐츠 시작": content_start.strftime("%Y-%m-%d"),
            "올해 판매 집중": f"{rising_this_year.strftime('%m/%d')} ~ {decline_this_year.strftime('%m/%d')}",
            "현재 Action Score": current_score,
            "현재 판단": current_decision,
            "반복 가능성": repeat_level,
            "권장 액션": basic_action
        })

    seasonal_df = pd.DataFrame(planning_rows)

    if not seasonal_df.empty:
        repeat_order = {
            "높음": 3,
            "중간": 2,
            "낮음": 1
        }

        seasonal_df["반복점수"] = seasonal_df["반복 가능성"].map(repeat_order).fillna(0)

        seasonal_df = seasonal_df.sort_values(
            ["반복점수", "현재 Action Score"],
            ascending=[False, False]
        ).drop(columns=["반복점수"]).reset_index(drop=True)

    return seasonal_df


def make_md_comments(summary_df):
    comments = []

    if summary_df.empty:
        return ["데이터 없음"]

    top_action = summary_df.sort_values("Action Score", ascending=False).iloc[0]

    rising_df = summary_df[summary_df["상태"].isin(["상승", "급상승"])]
    falling_df = summary_df[summary_df["상태"].isin(["하락", "급하락"])]
    monitor_df = summary_df[summary_df["판단"].isin(["즉시 검토", "모니터링"])]

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

    season_candidates = (
        summary_df["시즌"]
        .value_counts()
        .head(2)
        .index
        .tolist()
    )
    season_text = " / ".join(season_candidates)

    if not rising_df.empty:
        rising_keywords = ", ".join(rising_df["키워드그룹"].head(3).tolist())
    else:
        rising_keywords = "없음"

    if not falling_df.empty:
        falling_keywords = ", ".join(falling_df["키워드그룹"].head(3).tolist())
    else:
        falling_keywords = "없음"

    comments.append(f"상품기획: {category_text} 중심 검토")
    comments.append(f"시즌 방향: {season_text} 키워드 확인")
    comments.append(f"상승 키워드: {rising_keywords}")
    comments.append(f"주의 키워드: {falling_keywords}")

    if len(monitor_df) > 0:
        comments.append(f"우선 검토: {len(monitor_df)}개 키워드")
    else:
        comments.append("우선 검토: 신규 확대보다 관찰")

    if top_action["판단"] == "즉시 검토":
        comments.append("소싱 방향: 빠른 샘플 / 소량 테스트")
    elif top_action["판단"] == "모니터링":
        comments.append("소싱 방향: 즉시 발주보다 반응 추적")
    else:
        comments.append("소싱 방향: 물량 확대 보류")

    comments.append("콘텐츠 방향: 상승 키워드 중심 스타일링 노출")
    comments.append("다음 액션: 상위 2개 키워드만 우선 검토")

    return comments


def create_excel_download(trend_df, summary_df, comments, seasonal_df=None):
    output = BytesIO()

    comment_df = pd.DataFrame({
        "MD 코멘트": comments
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        trend_df.to_excel(writer, index=False, sheet_name="트렌드데이터")
        summary_df.to_excel(writer, index=False, sheet_name="요약")

        if seasonal_df is not None and not seasonal_df.empty:
            seasonal_df.to_excel(writer, index=False, sheet_name="시즌패턴")

        comment_df.to_excel(writer, index=False, sheet_name="MD코멘트")

    output.seek(0)
    return output


# =====================================================
# 7. 사이드바 입력
# =====================================================
st.sidebar.markdown("---")
st.sidebar.title("🔎 Naver Trend 설정")

keyword_presets = {
    "시즌 의류 트렌드": """버뮤다팬츠: 버뮤다팬츠, 여성 버뮤다팬츠, 반바지
크롭셔츠: 크롭셔츠, 여성 셔츠, 여름 셔츠
슬리브리스: 슬리브리스, 나시, 여성 나시
카고팬츠: 카고팬츠, 여성 카고팬츠
플리츠스커트: 플리츠스커트, 여성 스커트""",

    "굿즈 / 키링 트렌드": """인형키링: 인형키링, 키링, 백참
키캡키링: 키캡키링, 키캡 키링
스트레스볼: 스트레스볼, 스퀴시, 말랑이
파우치: 파우치, 미니파우치, 화장품 파우치
폰꾸: 폰꾸, 핸드폰꾸미기, 폰스트랩""",

    "장마 / 여름 트렌드": """레인부츠: 레인부츠, 장화, 여성 레인부츠
우산: 우산, 장우산, 미니우산
방수백: 방수백, 방수 가방
샌들: 샌들, 여성 샌들, 여름 샌들
린넨셔츠: 린넨셔츠, 여성 린넨셔츠""",

    "간절기 아우터 트렌드": """바람막이: 바람막이, 여성 바람막이, 윈드브레이커
가디건: 가디건, 여성 가디건
트렌치코트: 트렌치코트, 여성 트렌치코트
자켓: 자켓, 여성 자켓, 봄 자켓
후드집업: 후드집업, 여성 후드집업""",

    "프래그런스 / 뷰티 트렌드": """향수: 향수, 여자 향수, 니치향수
디퓨저: 디퓨저, 실내 디퓨저
핸드크림: 핸드크림, 퍼퓸 핸드크림
립밤: 립밤, 컬러립밤
바디미스트: 바디미스트, 퍼퓸 바디미스트"""
}

preset_name = st.sidebar.selectbox(
    "키워드 프리셋",
    list(keyword_presets.keys()),
    index=0
)

if "naver_keyword_preset" not in st.session_state:
    st.session_state["naver_keyword_preset"] = preset_name
    st.session_state["naver_keyword_text"] = keyword_presets[preset_name]

if st.session_state["naver_keyword_preset"] != preset_name:
    st.session_state["naver_keyword_preset"] = preset_name
    st.session_state["naver_keyword_text"] = keyword_presets[preset_name]

keyword_text = st.sidebar.text_area(
    "키워드 그룹 입력",
    key="naver_keyword_text",
    height=210
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
    '<div class="subtitle">네이버 데이터랩 검색어 트렌드를 가져와 전년도 시즌 패턴과 올해 MD 적용 타이밍까지 분석합니다.</div>',
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

    last_year = end_date.year - 1
    last_year_start = f"{last_year}-01-01"
    last_year_end = f"{last_year}-12-31"

    last_year_result, last_year_error = call_naver_datalab_api(
        client_id=client_id,
        client_secret=client_secret,
        start_date=last_year_start,
        end_date=last_year_end,
        time_unit="week",
        keyword_groups=keyword_groups,
        device=device_label,
        gender=gender_label,
        ages=age_options[age_label]
    )

    if last_year_error:
        last_year_df = pd.DataFrame()
        st.warning("전년도 시즌 패턴 데이터 조회에 실패했습니다. 현재 트렌드 분석만 표시됩니다.")
    else:
        last_year_df = convert_api_result_to_df(last_year_result)

    st.session_state["naver_trend_df"] = trend_df
    st.session_state["naver_last_year_df"] = last_year_df
    st.session_state["naver_keyword_groups"] = keyword_groups
    st.session_state["naver_period"] = f"{start_date} ~ {end_date}"
    st.session_state["naver_time_unit_label"] = time_unit_label
    st.session_state["naver_target_year"] = end_date.year

# =====================================================
# 11. 결과 표시
# =====================================================
if "naver_trend_df" not in st.session_state:
    st.info("왼쪽에서 키워드와 기간을 설정한 뒤 `네이버 트렌드 조회` 버튼을 눌러주세요.")
    st.stop()

trend_df = st.session_state["naver_trend_df"]
last_year_df = st.session_state.get("naver_last_year_df", pd.DataFrame())

summary_df = make_trend_summary(trend_df)
comments = make_md_comments(summary_df)

target_year = st.session_state.get("naver_target_year", datetime.today().year)
seasonal_df = make_seasonal_planning(last_year_df, summary_df, target_year)

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

<div class="insight-action">우선 액션: {top_action['기본액션']}</div>
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
# 16. 전년도 시즌 패턴 분석
# =====================================================
st.markdown('<div class="section-title">⑤ 전년도 시즌 패턴 분석</div>', unsafe_allow_html=True)

if seasonal_df.empty:
    st.info("전년도 시즌 패턴 데이터가 없습니다. 조회 조건을 확인해주세요.")
else:
    st.dataframe(
        seasonal_df[
            [
                "키워드그룹",
                "MD카테고리",
                "세부카테고리",
                "작년 상승 시작",
                "작년 피크",
                "작년 하락 시작",
                "트렌드 지속",
                "트렌드 유형",
                "반복 가능성"
            ]
        ],
        use_container_width=True,
        height=300
    )

# =====================================================
# 17. 전년도 vs 올해 키워드 관심도 비교
# =====================================================
if not seasonal_df.empty and not last_year_df.empty:
    st.markdown('<div class="section-title">⑤-1 전년도 vs 올해 키워드 관심도 비교</div>', unsafe_allow_html=True)

    keyword_list = sorted(last_year_df["키워드그룹"].dropna().unique().tolist())

    selected_keyword_compare = st.selectbox(
        "비교할 키워드 선택",
        keyword_list,
        index=0,
        key="compare_keyword_select"
    )

    selected_last_year_df = last_year_df[
        last_year_df["키워드그룹"] == selected_keyword_compare
    ].copy()

    selected_this_year_df = trend_df[
        trend_df["키워드그룹"] == selected_keyword_compare
    ].copy()

    selected_last_year_df = selected_last_year_df.sort_values("기간").reset_index(drop=True)
    selected_this_year_df = selected_this_year_df.sort_values("기간").reset_index(drop=True)

    if not selected_last_year_df.empty and not selected_this_year_df.empty:
        selected_last_year_df["비교순번"] = range(1, len(selected_last_year_df) + 1)
        selected_this_year_df["비교순번"] = range(1, len(selected_this_year_df) + 1)

        selected_last_year_df["라벨"] = pd.to_datetime(selected_last_year_df["기간"]).dt.strftime("%m-%d")
        selected_this_year_df["라벨"] = pd.to_datetime(selected_this_year_df["기간"]).dt.strftime("%m-%d")

        selected_last_year_df["구분"] = "전년도"
        selected_this_year_df["구분"] = "올해"

        compare_df = pd.concat(
            [selected_last_year_df, selected_this_year_df],
            ignore_index=True
        )

        last_rise, last_peak, last_decline = get_trend_points(selected_last_year_df)
        this_rise, this_peak, this_decline = get_trend_points(selected_this_year_df)

        fig_compare = px.line(
            compare_df,
            x="비교순번",
            y="관심도",
            color="구분",
            markers=True,
            custom_data=["라벨", "구분"]
        )

        fig_compare.update_traces(
            line=dict(width=4),
            marker=dict(size=7),
            hovertemplate="<b>%{customdata[1]}</b><br>기준일: %{customdata[0]}<br>관심도: %{y}<extra></extra>"
        )

        fig_compare.for_each_trace(
            lambda t: t.update(
                line_color="#7CB7FF" if t.name == "전년도" else "#F59E0B",
                marker_color="#7CB7FF" if t.name == "전년도" else "#F59E0B"
            )
        )

        fig_compare.add_scatter(
            x=[last_rise["비교순번"]],
            y=[last_rise["관심도"]],
            mode="markers+text",
            marker=dict(size=14, color="#22C55E"),
            text=["전년 상승"],
            textposition="top center",
            textfont=dict(color="#FFFFFF", size=12),
            name="전년 상승"
        )

        fig_compare.add_scatter(
            x=[last_peak["비교순번"]],
            y=[last_peak["관심도"]],
            mode="markers+text",
            marker=dict(size=15, color="#38BDF8"),
            text=["전년 PEAK"],
            textposition="top center",
            textfont=dict(color="#FFFFFF", size=12),
            name="전년 PEAK"
        )

        fig_compare.add_scatter(
            x=[last_decline["비교순번"]],
            y=[last_decline["관심도"]],
            mode="markers+text",
            marker=dict(size=14, color="#60A5FA"),
            text=["전년 하락"],
            textposition="top center",
            textfont=dict(color="#FFFFFF", size=12),
            name="전년 하락"
        )

        fig_compare.add_scatter(
            x=[this_rise["비교순번"]],
            y=[this_rise["관심도"]],
            mode="markers+text",
            marker=dict(size=14, color="#84CC16"),
            text=["올해 상승"],
            textposition="bottom center",
            textfont=dict(color="#FFFFFF", size=12),
            name="올해 상승"
        )

        fig_compare.add_scatter(
            x=[this_peak["비교순번"]],
            y=[this_peak["관심도"]],
            mode="markers+text",
            marker=dict(size=15, color="#F97316"),
            text=["올해 PEAK"],
            textposition="bottom center",
            textfont=dict(color="#FFFFFF", size=12),
            name="올해 PEAK"
        )

        fig_compare.add_scatter(
            x=[this_decline["비교순번"]],
            y=[this_decline["관심도"]],
            mode="markers+text",
            marker=dict(size=14, color="#EF4444"),
            text=["올해 하락"],
            textposition="bottom center",
            textfont=dict(color="#FFFFFF", size=12),
            name="올해 하락"
        )

        fig_compare = apply_dark_chart_style(
            fig_compare,
            height=500,
            y_title="검색 관심도"
        )

        fig_compare.update_layout(
            title=dict(
                text=f"{selected_keyword_compare} | 전년도 vs 올해 관심도 비교",
                font=dict(size=20, color="#FFFFFF")
            ),
            xaxis=dict(
                title="주차 흐름 비교",
                tickfont=dict(color="#FFFFFF"),
                title_font=dict(color="#FFFFFF"),
                gridcolor="#262730",
                zerolinecolor="#262730"
            ),
            yaxis=dict(
                title="검색 관심도",
                tickfont=dict(color="#FFFFFF"),
                title_font=dict(color="#FFFFFF"),
                gridcolor="#262730",
                zerolinecolor="#262730"
            ),
            legend=dict(
                orientation="h",
                y=-0.25,
                font=dict(size=12, color="#FFFFFF")
            )
        )

        st.plotly_chart(fig_compare, use_container_width=True)

        rise_gap = int(this_rise["비교순번"] - last_rise["비교순번"])
        peak_gap = int(this_peak["비교순번"] - last_peak["비교순번"])
        peak_diff = round(float(this_peak["관심도"] - last_peak["관심도"]), 1)

        if rise_gap < 0:
            rise_comment = f"올해 상승 시작이 전년도보다 {abs(rise_gap)}주 빠릅니다."
        elif rise_gap > 0:
            rise_comment = f"올해 상승 시작이 전년도보다 {rise_gap}주 늦습니다."
        else:
            rise_comment = "올해 상승 시작 시점이 전년도와 유사합니다."

        if peak_gap < 0:
            peak_timing_comment = f"올해 피크가 전년도보다 {abs(peak_gap)}주 빠릅니다."
        elif peak_gap > 0:
            peak_timing_comment = f"올해 피크가 전년도보다 {peak_gap}주 늦습니다."
        else:
            peak_timing_comment = "올해 피크 시점은 전년도와 유사합니다."

        if peak_diff > 0:
            peak_size_comment = f"올해 피크 강도는 전년도보다 {peak_diff}p 높습니다."
        elif peak_diff < 0:
            peak_size_comment = f"올해 피크 강도는 전년도보다 {abs(peak_diff)}p 낮습니다."
        else:
            peak_size_comment = "올해 피크 강도는 전년도와 비슷합니다."

        st.markdown(f"""
        <div class="comment-box">
            <p class="comment-line"><b style="color:#FFFFFF;">1.</b> 전년 상승 시작: {last_rise['라벨']} / 올해 상승 시작: {this_rise['라벨']}</p>
            <p class="comment-line"><b style="color:#FFFFFF;">2.</b> {rise_comment}</p>
            <p class="comment-line"><b style="color:#FFFFFF;">3.</b> 전년 피크: {last_peak['라벨']} ({last_peak['관심도']:.1f}) / 올해 피크: {this_peak['라벨']} ({this_peak['관심도']:.1f})</p>
            <p class="comment-line"><b style="color:#FFFFFF;">4.</b> {peak_timing_comment}</p>
            <p class="comment-line"><b style="color:#FFFFFF;">5.</b> {peak_size_comment}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("선택한 키워드의 전년도 또는 올해 데이터가 부족합니다.")

# =====================================================
# 18. 올해 MD 적용 캘린더
# =====================================================
st.markdown('<div class="section-title">⑥ 올해 MD 적용 캘린더</div>', unsafe_allow_html=True)

if seasonal_df.empty:
    st.info("올해 적용 캘린더를 생성할 전년도 패턴 데이터가 없습니다.")
else:
    st.dataframe(
        seasonal_df[
            [
                "키워드그룹",
                "올해 기획 시작",
                "올해 소싱/발주 마감",
                "올해 콘텐츠 시작",
                "올해 판매 집중",
                "현재 Action Score",
                "현재 판단",
                "권장 액션"
            ]
        ],
        use_container_width=True,
        height=300
    )

# =====================================================
# 19. 요약 테이블
# =====================================================
st.markdown('<div class="section-title">⑦ 키워드별 상승/하락 요약</div>', unsafe_allow_html=True)

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
# 20. MD 코멘트
# =====================================================
st.markdown('<div class="section-title">⑧ MD 적용 코멘트</div>', unsafe_allow_html=True)

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
# 21. 원본 데이터
# =====================================================
with st.expander("📌 원본 트렌드 데이터 확인", expanded=False):
    st.write(f"조회 기간: {period_text}")
    st.write(f"조회 단위: {unit_text}")
    st.dataframe(
        trend_df,
        use_container_width=True,
        height=360
    )

    if last_year_df is not None and not last_year_df.empty:
        st.markdown("#### 전년도 트렌드 데이터")
        st.dataframe(
            last_year_df,
            use_container_width=True,
            height=360
        )

# =====================================================
# 22. 다운로드
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑨ 다운로드</div>', unsafe_allow_html=True)

excel_file = create_excel_download(
    trend_df=trend_df,
    summary_df=summary_df,
    comments=comments,
    seasonal_df=seasonal_df
)

st.download_button(
    label="📥 Naver Trend Insight 엑셀 다운로드",
    data=excel_file,
    file_name="naver_trend_insight.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Naver Trend Insight · Search Trend / Seasonal Pattern / MD Planning")