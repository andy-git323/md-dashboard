import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import streamlit.components.v1 as components

# =====================================================
# 1. PAGE SETTING
# =====================================================
st.set_page_config(
    page_title="MD Schedule",
    page_icon="📅",
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

    .task-box {
        background-color: #171B26;
        border: 1px solid #2A2F3A;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .task-title {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .task-text {
        color: #D1D5DB;
        font-size: 14px;
        line-height: 1.6;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. FORMAT FUNCTIONS
# =====================================================
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


def get_status_color(status):
    if status == "완료":
        return "#22C55E"
    elif status == "진행중":
        return "#60A5FA"
    elif status == "주의":
        return "#F59E0B"
    elif status == "위험":
        return "#EF4444"
    else:
        return "#6B7280"


def get_event_color(event_type):
    color_map = {
        "기획": "#2563EB",
        "디자인": "#7C3AED",
        "샘플": "#8B5CF6",
        "품평": "#F59E0B",
        "발주": "#F97316",
        "생산": "#EF4444",
        "입고": "#DC2626",
        "촬영": "#22C55E",
        "런칭": "#EAB308",
        "DROP": "#06B6D4",
        "체크": "#64748B"
    }
    return color_map.get(event_type, "#64748B")


def make_event_pill(text, event_type):
    color = get_event_color(event_type)
    return f'<span class="event-pill" style="background-color:{color};">{text}</span>'


# =====================================================
# 4. SIDEBAR SETTINGS
# =====================================================
st.sidebar.markdown("---")
st.sidebar.title("⚙️ Schedule 설정")

season_name = st.sidebar.selectbox(
    "시즌 선택",
    ["26FW", "26SS", "27SS"],
    index=0
)

launch_date = st.sidebar.date_input(
    "메인 런칭일",
    value=datetime(2026, 9, 1).date()
)

selected_today = st.sidebar.date_input(
    "현재 기준일",
    value=datetime.today().date()
)

drop_count = st.sidebar.slider(
    "DROP 수",
    min_value=2,
    max_value=6,
    value=4,
    step=1
)

calendar_month = st.sidebar.selectbox(
    "캘린더 표시 월",
    [f"2026-{month:02d}" for month in range(1, 13)],
    index=8
)

# =====================================================
# 5. SCHEDULE DATA
# =====================================================
base_launch = pd.to_datetime(launch_date)

schedule_steps = [
    {
        "단계": "시장조사 / 트렌드 리서치",
        "유형": "기획",
        "시작": base_launch - timedelta(days=150),
        "종료": base_launch - timedelta(days=125),
        "담당": "MD",
        "중요도": "높음"
    },
    {
        "단계": "시즌 콘셉트 / 상품 방향 설정",
        "유형": "기획",
        "시작": base_launch - timedelta(days=125),
        "종료": base_launch - timedelta(days=105),
        "담당": "MD / 디자인",
        "중요도": "높음"
    },
    {
        "단계": "라인업 / SKU 설계",
        "유형": "기획",
        "시작": base_launch - timedelta(days=105),
        "종료": base_launch - timedelta(days=88),
        "담당": "MD",
        "중요도": "높음"
    },
    {
        "단계": "디자인 개발 / 샘플 의뢰",
        "유형": "디자인",
        "시작": base_launch - timedelta(days=88),
        "종료": base_launch - timedelta(days=65),
        "담당": "디자인 / 생산",
        "중요도": "높음"
    },
    {
        "단계": "1차 샘플 확인 / 수정",
        "유형": "샘플",
        "시작": base_launch - timedelta(days=65),
        "종료": base_launch - timedelta(days=48),
        "담당": "MD / 디자인 / 생산",
        "중요도": "중간"
    },
    {
        "단계": "품평 / 최종 발주 결정",
        "유형": "품평",
        "시작": base_launch - timedelta(days=48),
        "종료": base_launch - timedelta(days=38),
        "담당": "MD / 대표 / 생산",
        "중요도": "높음"
    },
    {
        "단계": "생산 진행",
        "유형": "생산",
        "시작": base_launch - timedelta(days=38),
        "종료": base_launch - timedelta(days=12),
        "담당": "생산",
        "중요도": "높음"
    },
    {
        "단계": "입고 / 검수",
        "유형": "입고",
        "시작": base_launch - timedelta(days=15),
        "종료": base_launch - timedelta(days=5),
        "담당": "물류 / MD",
        "중요도": "높음"
    },
    {
        "단계": "촬영 / 콘텐츠 준비",
        "유형": "촬영",
        "시작": base_launch - timedelta(days=20),
        "종료": base_launch - timedelta(days=3),
        "담당": "콘텐츠 / MD",
        "중요도": "중간"
    },
    {
        "단계": "런칭 / 판매 시작",
        "유형": "런칭",
        "시작": base_launch,
        "종료": base_launch + timedelta(days=7),
        "담당": "전체",
        "중요도": "높음"
    },
]

schedule_df = pd.DataFrame(schedule_steps)
schedule_df["시작"] = pd.to_datetime(schedule_df["시작"])
schedule_df["종료"] = pd.to_datetime(schedule_df["종료"])
schedule_df["기간"] = (schedule_df["종료"] - schedule_df["시작"]).dt.days + 1

today_ts = pd.to_datetime(selected_today)

def calc_status(row):
    if today_ts > row["종료"]:
        return "완료"
    elif row["시작"] <= today_ts <= row["종료"]:
        return "진행중"
    elif 0 <= (row["시작"] - today_ts).days <= 14:
        return "주의"
    else:
        return "예정"

schedule_df["상태"] = schedule_df.apply(calc_status, axis=1)
schedule_df["상태색"] = schedule_df["상태"].apply(get_status_color)

# DROP DATA
drop_rows = []

for i in range(1, drop_count + 1):
    start = base_launch + timedelta(days=(i - 1) * 28)
    end = start + timedelta(days=27)

    if i == 1:
        theme = "시즌 런칭 / 메인 아이템"
    elif i == 2:
        theme = "반응 상품 확장 / 추가 컬러"
    elif i == 3:
        theme = "기온 대응 / 핵심 판매 구간"
    elif i == 4:
        theme = "시즌 후반 / 재고 소진"
    else:
        theme = "추가 운영 / 리오더 대응"

    if today_ts > end:
        status = "완료"
    elif start <= today_ts <= end:
        status = "진행중"
    elif 0 <= (start - today_ts).days <= 14:
        status = "주의"
    else:
        status = "예정"

    drop_rows.append({
        "DROP": f"DROP{i}",
        "유형": "DROP",
        "시작": start,
        "종료": end,
        "운영기간": f"{start.strftime('%m/%d')} ~ {end.strftime('%m/%d')}",
        "운영 테마": theme,
        "상태": status,
        "상태색": get_status_color(status)
    })

drop_df = pd.DataFrame(drop_rows)

# =====================================================
# 6. CALENDAR EVENT DATA
# =====================================================
calendar_events = []

for _, row in schedule_df.iterrows():
    calendar_events.append({
        "일자": row["시작"].date(),
        "이벤트": f"{row['단계']} 시작",
        "유형": row["유형"],
        "구분": "업무"
    })
    calendar_events.append({
        "일자": row["종료"].date(),
        "이벤트": f"{row['단계']} 마감",
        "유형": row["유형"],
        "구분": "업무"
    })

for _, row in drop_df.iterrows():
    calendar_events.append({
        "일자": row["시작"].date(),
        "이벤트": f"{row['DROP']} 시작",
        "유형": "DROP",
        "구분": "DROP"
    })
    calendar_events.append({
        "일자": row["종료"].date(),
        "이벤트": f"{row['DROP']} 종료",
        "유형": "DROP",
        "구분": "DROP"
    })

check_events = [
    {
        "일자": (base_launch + timedelta(days=7)).date(),
        "이벤트": "런칭 1주차 판매 반응 체크",
        "유형": "체크",
        "구분": "체크"
    },
    {
        "일자": (base_launch + timedelta(days=14)).date(),
        "이벤트": "리오더 / 추가 생산 판단",
        "유형": "체크",
        "구분": "체크"
    },
    {
        "일자": (base_launch + timedelta(days=21)).date(),
        "이벤트": "부진 상품 소진 전략 점검",
        "유형": "체크",
        "구분": "체크"
    },
    {
        "일자": (base_launch + timedelta(days=35)).date(),
        "이벤트": "DROP2 반응 체크",
        "유형": "체크",
        "구분": "체크"
    },
]

calendar_events.extend(check_events)
events_df = pd.DataFrame(calendar_events)
events_df["일자"] = pd.to_datetime(events_df["일자"]).dt.date

# =====================================================
# 7. CALENDAR RENDER FUNCTION
# =====================================================
def render_month_calendar(year, month, events_df, today_date):
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    day_names = ["월", "화", "수", "목", "금", "토", "일"]

    html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            background-color: #0E1117;
            font-family: Arial, sans-serif;
        }}

        .calendar-wrap {{
            background-color: #111827;
            border: 1px solid #2A2F3A;
            border-radius: 18px;
            padding: 18px;
            box-sizing: border-box;
        }}

        .calendar-title {{
            color: #FFFFFF;
            font-size: 22px;
            font-weight: 850;
            margin-bottom: 14px;
        }}

        .calendar-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 8px;
            table-layout: fixed;
        }}

        .calendar-th {{
            color: #D1D5DB;
            font-size: 14px;
            font-weight: 700;
            text-align: center;
            padding: 8px;
        }}

        .calendar-td {{
            background-color: #171B26;
            border: 1px solid #2A2F3A;
            border-radius: 14px;
            height: 128px;
            vertical-align: top;
            padding: 10px;
            box-sizing: border-box;
        }}

        .calendar-td-empty {{
            background-color: transparent;
            border: 1px solid transparent;
            height: 128px;
        }}

        .calendar-day {{
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 800;
            margin-bottom: 6px;
        }}

        .calendar-today {{
            color: #60A5FA;
            font-size: 14px;
            font-weight: 900;
            margin-bottom: 6px;
        }}

        .event-pill {{
            display: block;
            color: #FFFFFF;
            font-size: 11px;
            line-height: 1.25;
            padding: 4px 6px;
            border-radius: 8px;
            margin-bottom: 4px;
            white-space: normal;
        }}
    </style>
    </head>
    <body>
    <div class="calendar-wrap">
        <div class="calendar-title">{year}년 {month}월 MD Calendar</div>
        <table class="calendar-table">
            <thead>
                <tr>
    """

    for day_name in day_names:
        html += f'<th class="calendar-th">{day_name}</th>'

    html += """
                </tr>
            </thead>
            <tbody>
    """

    for week in month_days:
        html += "<tr>"

        for day in week:
            if day == 0:
                html += '<td class="calendar-td-empty"></td>'
            else:
                current_date = datetime(year, month, day).date()
                day_events = events_df[events_df["일자"] == current_date]

                if current_date == today_date:
                    day_label = f'<div class="calendar-today">{day} · TODAY</div>'
                else:
                    day_label = f'<div class="calendar-day">{day}</div>'

                event_html = ""

                for _, event in day_events.head(4).iterrows():
                    event_html += make_event_pill(event["이벤트"], event["유형"])

                if len(day_events) > 4:
                    event_html += f'<span class="event-pill" style="background-color:#374151;">+{len(day_events) - 4} more</span>'

                html += f"""
                <td class="calendar-td">
                    {day_label}
                    {event_html}
                </td>
                """

        html += "</tr>"

    html += """
            </tbody>
        </table>
    </div>
    </body>
    </html>
    """

    return html

# =====================================================
# 8. HEADER
# =====================================================
st.markdown(f'<div class="title">📅 MD Schedule</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">{season_name} 시즌 일정 관리 · 기준일: {selected_today} · 런칭일: {launch_date}</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# 9. KPI
# =====================================================
season_start = schedule_df["시작"].min()
season_end = drop_df["종료"].max()
total_days = (season_end - season_start).days + 1
days_to_launch = (base_launch - today_ts).days
completed_steps = len(schedule_df[schedule_df["상태"] == "완료"])
active_steps = len(schedule_df[schedule_df["상태"] == "진행중"])
warning_steps = len(schedule_df[schedule_df["상태"] == "주의"])

st.markdown('<div class="section-title">① 시즌 일정 요약</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("시즌 전체 기간", f"{total_days}일", f"{season_start.date()} ~ {season_end.date()}")

with k2:
    kpi_card("런칭 D-DAY", f"D{days_to_launch:+d}", "메인 런칭 기준")

with k3:
    kpi_card("완료 단계", f"{completed_steps}개", "업무 단계 기준")

with k4:
    kpi_card("진행/주의 단계", f"{active_steps + warning_steps}개", "현재 관리 필요")

k5, k6, k7, k8 = st.columns(4)

with k5:
    kpi_card("DROP 수", f"{drop_count}개", "운영 드랍 수")

with k6:
    kpi_card("진행중 단계", f"{active_steps}개", "현재 진행 업무")

with k7:
    kpi_card("주의 단계", f"{warning_steps}개", "2주 내 시작 업무")

with k8:
    kpi_card("현재 기준일", str(selected_today), "사용자 선택 기준")

# =====================================================
# 10. MONTHLY CALENDAR
# =====================================================
st.markdown('<div class="section-title">② 월간 캘린더 뷰</div>', unsafe_allow_html=True)

selected_year = int(calendar_month.split("-")[0])
selected_month = int(calendar_month.split("-")[1])

calendar_html = render_month_calendar(
    selected_year,
    selected_month,
    events_df,
    selected_today
)

components.html(
    calendar_html,
    height=780,
    scrolling=True
)

# =====================================================
# 11. THIS WEEK TASKS
# =====================================================
st.markdown('<div class="section-title">③ 이번 주 핵심 업무</div>', unsafe_allow_html=True)

week_start = today_ts.date() - timedelta(days=today_ts.weekday())
week_end = week_start + timedelta(days=6)

this_week_events = events_df[
    (events_df["일자"] >= week_start) &
    (events_df["일자"] <= week_end)
].copy()

active_work = schedule_df[
    (schedule_df["시작"].dt.date <= week_end) &
    (schedule_df["종료"].dt.date >= week_start)
].copy()

tw1, tw2 = st.columns(2)

with tw1:
    task_text = ""

    if not active_work.empty:
        for _, row in active_work.head(5).iterrows():
            task_text += f"- {row['단계']} ({row['상태']})<br>"
    else:
        task_text = "이번 주에 겹치는 주요 업무 단계가 없습니다."

    st.markdown(f"""
    <div class="task-box">
        <div class="task-title">이번 주 진행 업무</div>
        <div class="task-text">{task_text}</div>
    </div>
    """, unsafe_allow_html=True)

with tw2:
    event_text = ""

    if not this_week_events.empty:
        for _, row in this_week_events.head(6).iterrows():
            event_text += f"- {row['일자']} · {row['이벤트']}<br>"
    else:
        event_text = "이번 주 등록된 주요 일정 이벤트가 없습니다."

    st.markdown(f"""
    <div class="task-box">
        <div class="task-title">이번 주 체크 일정</div>
        <div class="task-text">{event_text}</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 12. SCHEDULE TABLE
# =====================================================
st.markdown('<div class="section-title">④ 업무 단계별 일정</div>', unsafe_allow_html=True)

schedule_display = schedule_df.copy()
schedule_display["시작"] = schedule_display["시작"].dt.strftime("%Y-%m-%d")
schedule_display["종료"] = schedule_display["종료"].dt.strftime("%Y-%m-%d")

st.dataframe(
    schedule_display[
        [
            "단계",
            "유형",
            "시작",
            "종료",
            "기간",
            "담당",
            "중요도",
            "상태"
        ]
    ],
    use_container_width=True,
    height=390
)

# =====================================================
# 13. GANTT CHART
# =====================================================
st.markdown('<div class="section-title">⑤ 시즌 업무 Gantt Chart</div>', unsafe_allow_html=True)

gantt_df = schedule_df.copy()

fig_gantt = px.timeline(
    gantt_df,
    x_start="시작",
    x_end="종료",
    y="단계",
    color="유형",
    hover_data=["담당", "중요도", "상태", "기간"],
    color_discrete_map={
        "기획": "#2563EB",
        "디자인": "#7C3AED",
        "샘플": "#8B5CF6",
        "품평": "#F59E0B",
        "발주": "#F97316",
        "생산": "#EF4444",
        "입고": "#DC2626",
        "촬영": "#22C55E",
        "런칭": "#EAB308",
    }
)

fig_gantt.update_yaxes(
    autorange="reversed",
    title=None
)

fig_gantt.update_xaxes(
    title=None,
    tickformat="%m/%d"
)

fig_gantt.update_layout(
    height=520,
    margin=dict(l=20, r=20, t=30, b=30),
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(size=14, color="#FFFFFF"),
    legend=dict(
        font=dict(size=12, color="#FFFFFF"),
        bgcolor="rgba(0,0,0,0)",
        orientation="h",
        y=-0.18
    ),
    xaxis=dict(
        tickfont=dict(size=13, color="#E5E7EB"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    ),
    yaxis=dict(
        tickfont=dict(size=13, color="#E5E7EB"),
        gridcolor="#262730",
        zerolinecolor="#262730"
    )
)

fig_gantt.add_vline(
    x=today_ts,
    line_width=2,
    line_dash="dash",
    line_color="#FF4D4F"
)

fig_gantt.add_annotation(
    x=today_ts,
    y=1.08,
    xref="x",
    yref="paper",
    text="TODAY",
    showarrow=False,
    font=dict(size=12, color="#FF4D4F"),
    bgcolor="#171B26",
    bordercolor="#FF4D4F",
    borderwidth=1
)
fig_gantt.add_vline(
    x=today_ts,
    line_width=2,
    line_dash="dash",
    line_color="#FF4D4F"
)

fig_gantt.add_annotation(
    x=today_ts,
    y=1.08,
    xref="x",
    yref="paper",
    text="TODAY",
    showarrow=False,
    font=dict(size=12, color="#FF4D4F"),
    bgcolor="#171B26",
    bordercolor="#FF4D4F",
    borderwidth=1
)
st.plotly_chart(fig_gantt, use_container_width=True)

# =====================================================
# 14. DROP CALENDAR
# =====================================================
st.markdown('<div class="section-title">⑥ DROP별 운영 캘린더</div>', unsafe_allow_html=True)

drop_display = drop_df.copy()
drop_display["시작"] = drop_display["시작"].dt.strftime("%Y-%m-%d")
drop_display["종료"] = drop_display["종료"].dt.strftime("%Y-%m-%d")

st.dataframe(
    drop_display[
        [
            "DROP",
            "시작",
            "종료",
            "운영기간",
            "운영 테마",
            "상태"
        ]
    ],
    use_container_width=True,
    height=260
)

fig_drop = go.Figure()

for _, row in drop_df.iterrows():
    duration = (row["종료"] - row["시작"]).days + 1
    fig_drop.add_trace(
        go.Bar(
            x=[duration],
            y=[row["DROP"]],
            base=row["시작"],
            orientation="h",
            marker_color=row["상태색"],
            text=row["DROP"],
            textposition="inside",
            name=row["DROP"],
            hovertemplate=(
                f"<b>{row['DROP']}</b><br>"
                f"{row['운영기간']}<br>"
                f"{row['운영 테마']}<br>"
                f"상태: {row['상태']}<extra></extra>"
            )
        )
    )

fig_drop.update_layout(showlegend=False)
fig_drop.update_xaxes(type="date")
fig_drop = apply_dark_chart_style(fig_drop, height=360)
st.plotly_chart(fig_drop, use_container_width=True)

# =====================================================
# 15. AUTO COMMENT
# =====================================================
st.markdown('<div class="section-title">⑦ MD 일정 자동 코멘트</div>', unsafe_allow_html=True)

comments = []

if days_to_launch > 0:
    comments.append(
        f"메인 런칭까지 {days_to_launch}일 남았습니다. 현재 기준으로 런칭 전 준비 일정의 지연 여부를 주기적으로 점검해야 합니다."
    )
elif days_to_launch == 0:
    comments.append(
        "오늘은 메인 런칭일입니다. 상품 오픈, 콘텐츠 노출, 재고 반영, 가격 설정을 최종 확인해야 합니다."
    )
else:
    comments.append(
        f"메인 런칭 후 {abs(days_to_launch)}일이 경과했습니다. 현재는 판매 반응, 재고 소진, 리오더 가능성을 점검해야 합니다."
    )

if active_steps > 0:
    active_names = ", ".join(schedule_df[schedule_df["상태"] == "진행중"]["단계"].head(3).tolist())
    comments.append(
        f"현재 진행 중인 주요 업무는 {active_names}입니다. 해당 단계는 일정 지연 시 후속 업무에 직접 영향을 줄 수 있습니다."
    )

if warning_steps > 0:
    warning_names = ", ".join(schedule_df[schedule_df["상태"] == "주의"]["단계"].head(3).tolist())
    comments.append(
        f"2주 내 시작 예정인 주의 업무는 {warning_names}입니다. 담당자와 사전 준비 여부를 확인하는 것이 좋습니다."
    )

current_drop = drop_df[drop_df["상태"] == "진행중"]

if not current_drop.empty:
    current_drop_name = current_drop.iloc[0]["DROP"]
    comments.append(
        f"현재 운영 중인 DROP은 {current_drop_name}입니다. 판매 반응과 재고 흐름을 기준으로 다음 DROP 상품 구성을 조정할 수 있습니다."
    )
else:
    next_drop = drop_df[drop_df["상태"].isin(["주의", "예정"])].head(1)
    if not next_drop.empty:
        comments.append(
            f"다음 운영 예정 DROP은 {next_drop.iloc[0]['DROP']}입니다. 런칭 전 상품 이미지, 가격, 입고 일정을 미리 점검해야 합니다."
        )

comments.append(
    "MD Schedule은 기획, 생산, 입고, 콘텐츠, 런칭 일정이 서로 연결되어 있으므로, 지연 가능성이 있는 단계는 단독으로 보지 말고 후속 일정까지 함께 확인해야 합니다."
)

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
# 16. DOWNLOAD
# =====================================================
st.divider()
st.markdown('<div class="section-title">⑧ 데이터 다운로드</div>', unsafe_allow_html=True)

schedule_csv = schedule_display.to_csv(index=False).encode("utf-8-sig")
drop_csv = drop_display.to_csv(index=False).encode("utf-8-sig")
events_csv = events_df.to_csv(index=False).encode("utf-8-sig")

d1, d2, d3 = st.columns(3)

with d1:
    st.download_button(
        label="📥 업무 단계별 일정 CSV",
        data=schedule_csv,
        file_name=f"{season_name}_md_schedule_steps.csv",
        mime="text/csv"
    )

with d2:
    st.download_button(
        label="📥 DROP 운영 일정 CSV",
        data=drop_csv,
        file_name=f"{season_name}_drop_schedule.csv",
        mime="text/csv"
    )

with d3:
    st.download_button(
        label="📥 캘린더 이벤트 CSV",
        data=events_csv,
        file_name=f"{season_name}_calendar_events.csv",
        mime="text/csv"
    )

st.caption("MD Schedule · Calendar / Season / DROP / Production Schedule")