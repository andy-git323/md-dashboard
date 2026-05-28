<<<<<<< HEAD
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta

st.set_page_config(page_title="26 MD 스케줄", layout="wide")

today = datetime.today()

# ── 런칭일 & 고정 발주/입고일 ──
launch = {
    "INNER":  datetime(2026, 9, 15),
    "BOTTOM": datetime(2026, 9, 22),
    "OUTER":  datetime(2026, 9, 29),
}

lead = {
    "INNER":  {"기획": 4, "샘플": 3, "생산": 6, "입고": 1},
    "BOTTOM": {"기획": 4, "샘플": 3, "생산": 7, "입고": 1},
    "OUTER":  {"기획": 4, "샘플": 5, "생산": 8, "입고": 1},
}

colors = {
    "기획": "rgb(99, 110, 250)",
    "샘플": "rgb(239, 85, 59)",
    "생산": "rgb(0, 204, 150)",
    "입고": "rgb(255, 161, 90)",
    "판매": "rgb(171, 99, 250)",
}

stages = ["기획", "샘플", "생산", "입고", "판매"]

# ── 날짜 계산 ──
schedule = {}
for cat, launch_date in launch.items():
    s = {}
    s["입고_종료"]  = launch_date
    s["입고_시작"]  = launch_date - timedelta(weeks=lead[cat]["입고"])
    s["발주일"]     = s["입고_시작"] - timedelta(weeks=lead[cat]["생산"]) # 발주 = 생산시작
    s["생산_시작"]  = s["발주일"]
    s["생산_종료"]  = s["입고_시작"]
    s["샘플_종료"]  = s["생산_시작"]
    s["샘플_시작"]  = s["샘플_종료"] - timedelta(weeks=lead[cat]["샘플"])
    s["기획_종료"]  = s["샘플_시작"]
    s["기획_시작"]  = s["기획_종료"] - timedelta(weeks=lead[cat]["기획"])
    s["판매_시작"]  = launch_date
    s["판매_종료"]  = launch_date + timedelta(weeks=8)
    schedule[cat] = s

stage_keys = {
    "기획": ("기획_시작", "기획_종료"),
    "샘플": ("샘플_시작", "샘플_종료"),
    "생산": ("생산_시작", "생산_종료"),
    "입고": ("입고_시작", "입고_종료"),
    "판매": ("판매_시작", "판매_종료"),
}

def get_stage_status(start, end):
    if today > end:
        return "done"
    elif today >= start:
        return "active"
    else:
        return "pending"

def days_label(d):
    if d < 0:
        return f"✅ {abs(d)}일 전 완료"
    elif d == 0:
        return "🔥 오늘!"
    else:
        return f"D-{d}"

# ════════════════════════════════════
# HEADER
# ════════════════════════════════════
st.title("📅 26 FW MD 스케줄")
st.caption(f"기준일: {today.strftime('%Y-%m-%d')}")
st.divider()

# ════════════════════════════════════
# ① 발주 / 입고 — 항상 고정 표시
# ════════════════════════════════════
st.subheader("🔑 핵심 일정 — 발주 & 입고")

col1, col2, col3 = st.columns(3)
for col, (cat, s) in zip([col1, col2, col3], schedule.items()):
    with col:
        d_order   = (s["발주일"] - today).days
        d_inbound = (s["입고_시작"] - today).days

        st.markdown(f"### {cat}")

        # 발주
        order_color = "🔴" if d_order <= 7 and d_order >= 0 else ("✅" if d_order < 0 else "🟡")
        if d_order < 0:
            st.success(f"{order_color} **발주** ✅ 완료\n\n{s['발주일'].strftime('%m월 %d일')}")
        elif d_order <= 7:
            st.error(f"{order_color} **발주** 🚨 D-{d_order}\n\n{s['발주일'].strftime('%m월 %d일')}")
        elif d_order <= 21:
            st.warning(f"{order_color} **발주** ⚠️ D-{d_order}\n\n{s['발주일'].strftime('%m월 %d일')}")
        else:
            st.info(f"📌 **발주** D-{d_order}\n\n{s['발주일'].strftime('%m월 %d일')}")

        # 입고
        if d_inbound < 0:
            st.success(f"✅ **입고** 완료\n\n{s['입고_시작'].strftime('%m월 %d일')}")
        elif d_inbound <= 7:
            st.error(f"🚨 **입고** D-{d_inbound}\n\n{s['입고_시작'].strftime('%m월 %d일')}")
        elif d_inbound <= 21:
            st.warning(f"⚠️ **입고** D-{d_inbound}\n\n{s['입고_시작'].strftime('%m월 %d일')}")
        else:
            st.info(f"📌 **입고** D-{d_inbound}\n\n{s['입고_시작'].strftime('%m월 %d일')}")

st.divider()

# ════════════════════════════════════
# ② 지금 당장 할 일
# ════════════════════════════════════
st.subheader("🚨 지금 당장 할 일")

action_items = []
for cat, s in schedule.items():
    for stage in stages:
        sk, ek = stage_keys[stage]
        status = get_stage_status(s[sk], s[ek])
        if status == "active":
            end = s[ek]
            d_left = (end - today).days
            action_items.append({
                "cat": cat,
                "stage": stage,
                "종료일": end.strftime("%m월 %d일"),
                "d_left": d_left
            })

if action_items:
    cols = st.columns(len(action_items))
    for i, item in enumerate(sorted(action_items, key=lambda x: x["d_left"])):
        with cols[i]:
            if item["d_left"] <= 7:
                st.error(
                    f"**{item['cat']}**\n\n"
                    f"🔥 {item['stage']} 진행중\n\n"
                    f"마감 {item['종료일']}\n\n"
                    f"**D-{item['d_left']}**"
                )
            elif item["d_left"] <= 14:
                st.warning(
                    f"**{item['cat']}**\n\n"
                    f"⚠️ {item['stage']} 진행중\n\n"
                    f"마감 {item['종료일']}\n\n"
                    f"**D-{item['d_left']}**"
                )
            else:
                st.info(
                    f"**{item['cat']}**\n\n"
                    f"🔄 {item['stage']} 진행중\n\n"
                    f"마감 {item['종료일']}\n\n"
                    f"**D-{item['d_left']}**"
                )
else:
    st.success("✅ 현재 진행중인 단계 없음")

st.divider()

# ════════════════════════════════════
# ③ 카테고리별 전체 진행 상태
# ════════════════════════════════════
st.subheader("📊 카테고리별 진행 현황")

for cat, s in schedule.items():
    st.markdown(f"**{cat}** — 런칭 D-{(launch[cat] - today).days}")
    cols = st.columns(5)
    for i, stage in enumerate(stages):
        sk, ek = stage_keys[stage]
        start = s[sk]
        end   = s[ek]
        status = get_stage_status(start, end)
        with cols[i]:
            if status == "done":
                st.markdown(
                    f"<div style='background:#1a4a2e;padding:12px;border-radius:10px;text-align:center;border:1px solid #2ecc71'>"
                    f"<div style='font-size:20px'>✅</div>"
                    f"<div style='color:#2ecc71;font-weight:bold'>{stage}</div>"
                    f"<div style='color:#aaa;font-size:11px'>{start.strftime('%m/%d')}~{end.strftime('%m/%d')}</div>"
                    f"<div style='color:#2ecc71;font-size:11px'>완료</div>"
                    f"</div>", unsafe_allow_html=True
                )
            elif status == "active":
                d_left = (end - today).days
                st.markdown(
                    f"<div style='background:#4a3a00;padding:12px;border-radius:10px;text-align:center;border:2px solid #f39c12'>"
                    f"<div style='font-size:20px'>🔄</div>"
                    f"<div style='color:#f39c12;font-weight:bold'>{stage}</div>"
                    f"<div style='color:#aaa;font-size:11px'>{start.strftime('%m/%d')}~{end.strftime('%m/%d')}</div>"
                    f"<div style='color:#f39c12;font-size:11px'>진행중 D-{d_left}</div>"
                    f"</div>", unsafe_allow_html=True
                )
            else:
                d_start = (start - today).days
                st.markdown(
                    f"<div style='background:#1a1a2e;padding:12px;border-radius:10px;text-align:center;border:1px solid #444'>"
                    f"<div style='font-size:20px'>⚪</div>"
                    f"<div style='color:#888;font-weight:bold'>{stage}</div>"
                    f"<div style='color:#666;font-size:11px'>{start.strftime('%m/%d')}~{end.strftime('%m/%d')}</div>"
                    f"<div style='color:#666;font-size:11px'>D-{d_start} 후 시작</div>"
                    f"</div>", unsafe_allow_html=True
                )
    st.markdown("<br>", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════
# ④ 간트차트
# ════════════════════════════════════
st.subheader("📈 전체 일정 흐름")

gantt_data = []
for cat, s in schedule.items():
    for stage in stages:
        sk, ek = stage_keys[stage]
        gantt_data.append({
            "Task": cat,
            "Start": s[sk],
            "Finish": s[ek],
            "Resource": stage
        })

df = pd.DataFrame(gantt_data)
fig = ff.create_gantt(
    df, colors=colors, index_col="Resource",
    show_colorbar=True, group_tasks=True, showgrid_x=True,
)
fig.add_vline(
    x=today.timestamp() * 1000,
    line_width=2, line_dash="dash", line_color="red",
    annotation_text="오늘", annotation_position="top"
)
fig.update_layout(height=350, font_size=13)
=======
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta

st.set_page_config(page_title="26 FW MD 스케줄", layout="wide")

today = datetime.today()

# ── 런칭일 & 고정 발주/입고일 ──
launch = {
    "INNER":  datetime(2026, 9, 15),
    "BOTTOM": datetime(2026, 9, 22),
    "OUTER":  datetime(2026, 9, 29),
}

lead = {
    "INNER":  {"기획": 4, "샘플": 3, "생산": 6, "입고": 1},
    "BOTTOM": {"기획": 4, "샘플": 3, "생산": 7, "입고": 1},
    "OUTER":  {"기획": 4, "샘플": 5, "생산": 8, "입고": 1},
}

colors = {
    "기획": "rgb(99, 110, 250)",
    "샘플": "rgb(239, 85, 59)",
    "생산": "rgb(0, 204, 150)",
    "입고": "rgb(255, 161, 90)",
    "판매": "rgb(171, 99, 250)",
}

stages = ["기획", "샘플", "생산", "입고", "판매"]

# ── 날짜 계산 ──
schedule = {}
for cat, launch_date in launch.items():
    s = {}
    s["입고_종료"]  = launch_date
    s["입고_시작"]  = launch_date - timedelta(weeks=lead[cat]["입고"])
    s["발주일"]     = s["입고_시작"] - timedelta(weeks=lead[cat]["생산"]) # 발주 = 생산시작
    s["생산_시작"]  = s["발주일"]
    s["생산_종료"]  = s["입고_시작"]
    s["샘플_종료"]  = s["생산_시작"]
    s["샘플_시작"]  = s["샘플_종료"] - timedelta(weeks=lead[cat]["샘플"])
    s["기획_종료"]  = s["샘플_시작"]
    s["기획_시작"]  = s["기획_종료"] - timedelta(weeks=lead[cat]["기획"])
    s["판매_시작"]  = launch_date
    s["판매_종료"]  = launch_date + timedelta(weeks=8)
    schedule[cat] = s

stage_keys = {
    "기획": ("기획_시작", "기획_종료"),
    "샘플": ("샘플_시작", "샘플_종료"),
    "생산": ("생산_시작", "생산_종료"),
    "입고": ("입고_시작", "입고_종료"),
    "판매": ("판매_시작", "판매_종료"),
}

def get_stage_status(start, end):
    if today > end:
        return "done"
    elif today >= start:
        return "active"
    else:
        return "pending"

def days_label(d):
    if d < 0:
        return f"✅ {abs(d)}일 전 완료"
    elif d == 0:
        return "🔥 오늘!"
    else:
        return f"D-{d}"

# ════════════════════════════════════
# HEADER
# ════════════════════════════════════
st.title("📅 26 FW MD 스케줄")
st.caption(f"기준일: {today.strftime('%Y-%m-%d')}")
st.divider()

# ════════════════════════════════════
# ① 발주 / 입고 — 항상 고정 표시
# ════════════════════════════════════
st.subheader("🔑 핵심 일정 — 발주 & 입고")

col1, col2, col3 = st.columns(3)
for col, (cat, s) in zip([col1, col2, col3], schedule.items()):
    with col:
        d_order   = (s["발주일"] - today).days
        d_inbound = (s["입고_시작"] - today).days

        st.markdown(f"### {cat}")

        # 발주
        order_color = "🔴" if d_order <= 7 and d_order >= 0 else ("✅" if d_order < 0 else "🟡")
        if d_order < 0:
            st.success(f"{order_color} **발주** ✅ 완료\n\n{s['발주일'].strftime('%m월 %d일')}")
        elif d_order <= 7:
            st.error(f"{order_color} **발주** 🚨 D-{d_order}\n\n{s['발주일'].strftime('%m월 %d일')}")
        elif d_order <= 21:
            st.warning(f"{order_color} **발주** ⚠️ D-{d_order}\n\n{s['발주일'].strftime('%m월 %d일')}")
        else:
            st.info(f"📌 **발주** D-{d_order}\n\n{s['발주일'].strftime('%m월 %d일')}")

        # 입고
        if d_inbound < 0:
            st.success(f"✅ **입고** 완료\n\n{s['입고_시작'].strftime('%m월 %d일')}")
        elif d_inbound <= 7:
            st.error(f"🚨 **입고** D-{d_inbound}\n\n{s['입고_시작'].strftime('%m월 %d일')}")
        elif d_inbound <= 21:
            st.warning(f"⚠️ **입고** D-{d_inbound}\n\n{s['입고_시작'].strftime('%m월 %d일')}")
        else:
            st.info(f"📌 **입고** D-{d_inbound}\n\n{s['입고_시작'].strftime('%m월 %d일')}")

st.divider()

# ════════════════════════════════════
# ② 지금 당장 할 일
# ════════════════════════════════════
st.subheader("🚨 지금 당장 할 일")

action_items = []
for cat, s in schedule.items():
    for stage in stages:
        sk, ek = stage_keys[stage]
        status = get_stage_status(s[sk], s[ek])
        if status == "active":
            end = s[ek]
            d_left = (end - today).days
            action_items.append({
                "cat": cat,
                "stage": stage,
                "종료일": end.strftime("%m월 %d일"),
                "d_left": d_left
            })

if action_items:
    cols = st.columns(len(action_items))
    for i, item in enumerate(sorted(action_items, key=lambda x: x["d_left"])):
        with cols[i]:
            if item["d_left"] <= 7:
                st.error(
                    f"**{item['cat']}**\n\n"
                    f"🔥 {item['stage']} 진행중\n\n"
                    f"마감 {item['종료일']}\n\n"
                    f"**D-{item['d_left']}**"
                )
            elif item["d_left"] <= 14:
                st.warning(
                    f"**{item['cat']}**\n\n"
                    f"⚠️ {item['stage']} 진행중\n\n"
                    f"마감 {item['종료일']}\n\n"
                    f"**D-{item['d_left']}**"
                )
            else:
                st.info(
                    f"**{item['cat']}**\n\n"
                    f"🔄 {item['stage']} 진행중\n\n"
                    f"마감 {item['종료일']}\n\n"
                    f"**D-{item['d_left']}**"
                )
else:
    st.success("✅ 현재 진행중인 단계 없음")

st.divider()

# ════════════════════════════════════
# ③ 카테고리별 전체 진행 상태
# ════════════════════════════════════
st.subheader("📊 카테고리별 진행 현황")

for cat, s in schedule.items():
    st.markdown(f"**{cat}** — 런칭 D-{(launch[cat] - today).days}")
    cols = st.columns(5)
    for i, stage in enumerate(stages):
        sk, ek = stage_keys[stage]
        start = s[sk]
        end   = s[ek]
        status = get_stage_status(start, end)
        with cols[i]:
            if status == "done":
                st.markdown(
                    f"<div style='background:#1a4a2e;padding:12px;border-radius:10px;text-align:center;border:1px solid #2ecc71'>"
                    f"<div style='font-size:20px'>✅</div>"
                    f"<div style='color:#2ecc71;font-weight:bold'>{stage}</div>"
                    f"<div style='color:#aaa;font-size:11px'>{start.strftime('%m/%d')}~{end.strftime('%m/%d')}</div>"
                    f"<div style='color:#2ecc71;font-size:11px'>완료</div>"
                    f"</div>", unsafe_allow_html=True
                )
            elif status == "active":
                d_left = (end - today).days
                st.markdown(
                    f"<div style='background:#4a3a00;padding:12px;border-radius:10px;text-align:center;border:2px solid #f39c12'>"
                    f"<div style='font-size:20px'>🔄</div>"
                    f"<div style='color:#f39c12;font-weight:bold'>{stage}</div>"
                    f"<div style='color:#aaa;font-size:11px'>{start.strftime('%m/%d')}~{end.strftime('%m/%d')}</div>"
                    f"<div style='color:#f39c12;font-size:11px'>진행중 D-{d_left}</div>"
                    f"</div>", unsafe_allow_html=True
                )
            else:
                d_start = (start - today).days
                st.markdown(
                    f"<div style='background:#1a1a2e;padding:12px;border-radius:10px;text-align:center;border:1px solid #444'>"
                    f"<div style='font-size:20px'>⚪</div>"
                    f"<div style='color:#888;font-weight:bold'>{stage}</div>"
                    f"<div style='color:#666;font-size:11px'>{start.strftime('%m/%d')}~{end.strftime('%m/%d')}</div>"
                    f"<div style='color:#666;font-size:11px'>D-{d_start} 후 시작</div>"
                    f"</div>", unsafe_allow_html=True
                )
    st.markdown("<br>", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════
# ④ 간트차트
# ════════════════════════════════════
st.subheader("📈 전체 일정 흐름")

gantt_data = []
for cat, s in schedule.items():
    for stage in stages:
        sk, ek = stage_keys[stage]
        gantt_data.append({
            "Task": cat,
            "Start": s[sk],
            "Finish": s[ek],
            "Resource": stage
        })

df = pd.DataFrame(gantt_data)
fig = ff.create_gantt(
    df, colors=colors, index_col="Resource",
    show_colorbar=True, group_tasks=True, showgrid_x=True,
)
fig.add_vline(
    x=today.timestamp() * 1000,
    line_width=2, line_dash="dash", line_color="red",
    annotation_text="오늘", annotation_position="top"
)
fig.update_layout(height=350, font_size=13)
>>>>>>> 202e8a8b7b32446112832f6db9b4a6c848701843
st.plotly_chart(fig, use_container_width=True)