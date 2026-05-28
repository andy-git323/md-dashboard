import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

st.set_page_config(
    page_title="수주 스타일 대시보드",
    page_icon="👗",
    layout="wide"
)

@st.cache_data
def load_data():
    df_raw = pd.read_excel("C:/Users/andy3/OneDrive/Desktop/수주 스타일.xlsx", header=None)
    header_row = df_raw[df_raw.apply(
        lambda r: r.astype(str).str.contains('ITEM').any(), axis=1)].index[0]
    df = pd.read_excel("C:/Users/andy3/OneDrive/Desktop/수주 스타일.xlsx", header=header_row)
    df.columns = ['_', '대구분', 'ITEM', '대표Item', '시즌', 'MAIN품번',
                  '스타일명', '대표품번', '컬러', 'TEAM', 'MLB컬러', 'RMB_Price']
    df = df[df['대구분'].isin(['의류', '액세서리'])].copy()
    df['RMB_Price'] = pd.to_numeric(df['RMB_Price'], errors='coerce')
    df = df.dropna(subset=['RMB_Price'])
    
    # 가격대 분류
    def price_group(p):
        if p < 500: return "저가 (500↓)"
        elif p < 1000: return "중저가 (500~1000)"
        elif p < 2000: return "중가 (1000~2000)"
        elif p < 3000: return "중고가 (2000~3000)"
        else: return "고가 (3000↑)"
    df['가격대'] = df['RMB_Price'].apply(price_group)
    return df

df = load_data()

# ── 페이지 선택 ──
page = st.sidebar.selectbox(
    "📌 페이지 선택",
    ["📊 전체 현황", "🔍 ITEM 비교 분석", "📋 스타일 검색", "📈 네이버 트렌드", "🏪 경쟁사 분석"]
)

st.sidebar.divider()

# ══════════════════════════════
# 페이지 1: 전체 현황
# ══════════════════════════════
if page == "📊 전체 현황":
    
    # 필터
    st.sidebar.header("🔍 필터")
    selected_category = st.sidebar.multiselect(
        "대구분", options=df['대구분'].unique(), default=df['대구분'].unique())
    selected_season = st.sidebar.multiselect(
        "시즌", options=df['시즌'].unique(), default=df['시즌'].unique())
    price_range = st.sidebar.slider(
        "RMB 가격 범위",
        min_value=int(df['RMB_Price'].min()),
        max_value=int(df['RMB_Price'].max()),
        value=(int(df['RMB_Price'].min()), int(df['RMB_Price'].max()))
    )

    filtered = df[
        (df['대구분'].isin(selected_category)) &
        (df['시즌'].isin(selected_season)) &
        (df['RMB_Price'].between(*price_range))
    ]

    st.title("👗 수주 스타일 현황 대시보드")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y.%m.%d %H:%M')}")
    st.divider()

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 스타일", f"{len(filtered):,}개")
    with col2:
        st.metric("ITEM 종류", f"{filtered['ITEM'].nunique()}개")
    with col3:
        st.metric("평균 RMB", f"{filtered['RMB_Price'].mean():.0f}")
    with col4:
        cloth = len(filtered[filtered['대구분']=='의류'])
        acc = len(filtered[filtered['대구분']=='액세서리'])
        st.metric("의류 / 액세서리", f"{cloth} / {acc}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 ITEM별 스타일 수")
        item_count = filtered.groupby('ITEM').size().sort_values(ascending=True).reset_index()
        item_count.columns = ['ITEM', '스타일수']
        fig1 = px.bar(item_count, x='스타일수', y='ITEM', orientation='h',
                      color='스타일수', color_continuous_scale='Viridis',
                      template='plotly_dark')
        fig1.update_layout(showlegend=False, coloraxis_showscale=False,
                           margin=dict(l=0,r=0,t=0,b=0), height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("🍩 시즌별 구성")
        season_count = filtered.groupby('시즌').size().reset_index()
        season_count.columns = ['시즌', '스타일수']
        fig2 = px.pie(season_count, values='스타일수', names='시즌',
                      hole=0.5, color_discrete_sequence=['#C8A96E','#4ECDC4','#FF6B6B'],
                      template='plotly_dark')
        fig2.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=400)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("💰 ITEM별 평균 RMB")
        price_by_item = filtered.groupby('ITEM')['RMB_Price'].mean().sort_values(
            ascending=False).reset_index().head(10)
        price_by_item.columns = ['ITEM', '평균가격']
        fig3 = px.bar(price_by_item, x='ITEM', y='평균가격',
                      color='평균가격', color_continuous_scale='Oranges',
                      template='plotly_dark')
        fig3.update_layout(showlegend=False, coloraxis_showscale=False,
                           margin=dict(l=0,r=0,t=0,b=0), height=350)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("💎 가격대별 분포")
        price_order = ["저가 (500↓)", "중저가 (500~1000)", "중가 (1000~2000)",
                       "중고가 (2000~3000)", "고가 (3000↑)"]
        price_dist = filtered.groupby('가격대').size().reindex(price_order, fill_value=0).reset_index()
        price_dist.columns = ['가격대', '스타일수']
        fig4 = px.bar(price_dist, x='가격대', y='스타일수',
                      color='스타일수', color_continuous_scale='Teal',
                      template='plotly_dark')
        fig4.update_layout(showlegend=False, coloraxis_showscale=False,
                           margin=dict(l=0,r=0,t=0,b=0), height=350)
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════
# 페이지 2: ITEM 비교 분석
# ══════════════════════════════
elif page == "🔍 ITEM 비교 분석":

    st.title("🔍 ITEM 상세 비교 분석")
    st.caption("두 개의 ITEM을 선택해서 나란히 비교해보세요")
    st.divider()

    item_list = sorted(df['ITEM'].unique())

    col_a, col_b = st.columns(2)
    with col_a:
        item_a = st.selectbox("ITEM A 선택", item_list, index=0)
    with col_b:
        item_b = st.selectbox("ITEM B 선택", item_list, index=1)

    df_a = df[df['ITEM'] == item_a]
    df_b = df[df['ITEM'] == item_b]

    st.divider()

    # ── KPI 비교 ──
    st.subheader("📌 핵심 지표 비교")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"**구분**")
        st.markdown("총 스타일")
        st.markdown("평균 RMB")
        st.markdown("최저가")
        st.markdown("최고가")
        st.markdown("시즌 수")
        st.markdown("컬러 수")

    with col2:
        st.markdown(f"**{item_a}**")
        st.markdown(f"🔵 {len(df_a)}개")
        st.markdown(f"🔵 {df_a['RMB_Price'].mean():.0f}")
        st.markdown(f"🔵 {df_a['RMB_Price'].min():.0f}")
        st.markdown(f"🔵 {df_a['RMB_Price'].max():.0f}")
        st.markdown(f"🔵 {df_a['시즌'].nunique()}개")
        st.markdown(f"🔵 {df_a['컬러'].nunique()}개")

    with col3:
        st.markdown("**vs**")
        for _ in range(6):
            st.markdown("—")

    with col4:
        st.markdown(f"**{item_b}**")
        st.markdown(f"🔴 {len(df_b)}개")
        st.markdown(f"🔴 {df_b['RMB_Price'].mean():.0f}")
        st.markdown(f"🔴 {df_b['RMB_Price'].min():.0f}")
        st.markdown(f"🔴 {df_b['RMB_Price'].max():.0f}")
        st.markdown(f"🔴 {df_b['시즌'].nunique()}개")
        st.markdown(f"🔴 {df_b['컬러'].nunique()}개")

    with col5:
        st.markdown("**차이**")
        diff_style = len(df_a) - len(df_b)
        diff_price = df_a['RMB_Price'].mean() - df_b['RMB_Price'].mean()
        st.markdown(f"{'▲' if diff_style>0 else '▼'} {abs(diff_style)}")
        st.markdown(f"{'▲' if diff_price>0 else '▼'} {abs(diff_price):.0f}")
        st.markdown("—")
        st.markdown("—")
        st.markdown("—")
        st.markdown("—")

    st.divider()

    # ── 차트 비교 ──
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🍩 시즌 구성 비교")
        season_a = df_a.groupby('시즌').size().reset_index()
        season_a.columns = ['시즌', '수']
        season_a['ITEM'] = item_a
        season_b = df_b.groupby('시즌').size().reset_index()
        season_b.columns = ['시즌', '수']
        season_b['ITEM'] = item_b
        season_combined = pd.concat([season_a, season_b])
        fig_s = px.bar(season_combined, x='시즌', y='수', color='ITEM',
                       barmode='group',
                       color_discrete_map={item_a: '#4ECDC4', item_b: '#FF6B6B'},
                       template='plotly_dark')
        fig_s.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=300)
        st.plotly_chart(fig_s, use_container_width=True)

    with col2:
        st.subheader("💰 가격 분포 비교")
        fig_p = go.Figure()
        fig_p.add_trace(go.Box(
            y=df_a['RMB_Price'], name=item_a,
            marker_color='#4ECDC4', boxmean=True))
        fig_p.add_trace(go.Box(
            y=df_b['RMB_Price'], name=item_b,
            marker_color='#FF6B6B', boxmean=True))
        fig_p.update_layout(
            template='plotly_dark',
            margin=dict(l=0,r=0,t=0,b=0), height=300)
        st.plotly_chart(fig_p, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader(f"🎨 {item_a} 컬러 구성")
        color_a = df_a.groupby('컬러').size().sort_values(
            ascending=False).head(10).reset_index()
        color_a.columns = ['컬러', '수']
        fig_ca = px.bar(color_a, x='컬러', y='수',
                        color_discrete_sequence=['#4ECDC4'],
                        template='plotly_dark')
        fig_ca.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=280)
        st.plotly_chart(fig_ca, use_container_width=True)

    with col4:
        st.subheader(f"🎨 {item_b} 컬러 구성")
        color_b = df_b.groupby('컬러').size().sort_values(
            ascending=False).head(10).reset_index()
        color_b.columns = ['컬러', '수']
        fig_cb = px.bar(color_b, x='컬러', y='수',
                        color_discrete_sequence=['#FF6B6B'],
                        template='plotly_dark')
        fig_cb.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=280)
        st.plotly_chart(fig_cb, use_container_width=True)

    st.divider()

    # ── 스타일 목록 비교 ──
    st.subheader("📋 스타일 목록 비교")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f"**{item_a} ({len(df_a)}개)**")
        st.dataframe(
            df_a[['시즌','MAIN품번','스타일명','컬러','RMB_Price']].reset_index(drop=True),
            use_container_width=True, height=300)
    with col_r:
        st.markdown(f"**{item_b} ({len(df_b)}개)**")
        st.dataframe(
            df_b[['시즌','MAIN품번','스타일명','컬러','RMB_Price']].reset_index(drop=True),
            use_container_width=True, height=300)

# ══════════════════════════════
# 페이지 3: 스타일 검색
# ══════════════════════════════
elif page == "📋 스타일 검색":

    st.title("📋 스타일 검색")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 스타일명 검색", placeholder="예: 패딩, 셔츠...")
    with col2:
        item_filter = st.selectbox("ITEM", ['전체'] + sorted(df['ITEM'].unique()))
    with col3:
        season_filter = st.selectbox("시즌", ['전체'] + list(df['시즌'].unique()))

    col4, col5 = st.columns(2)
    with col4:
        category_filter = st.selectbox("대구분", ['전체'] + list(df['대구분'].unique()))
    with col5:
        price_filter = st.selectbox("가격대", ['전체',
            "저가 (500↓)", "중저가 (500~1000)", "중가 (1000~2000)",
            "중고가 (2000~3000)", "고가 (3000↑)"])

    result = df.copy()
    if search:
        result = result[result['스타일명'].str.contains(search, na=False)]
    if item_filter != '전체':
        result = result[result['ITEM'] == item_filter]
    if season_filter != '전체':
        result = result[result['시즌'] == season_filter]
    if category_filter != '전체':
        result = result[result['대구분'] == category_filter]
    if price_filter != '전체':
        result = result[result['가격대'] == price_filter]

    st.divider()

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("검색 결과", f"{len(result):,}개")
    with col_b:
        st.metric("평균 RMB", f"{result['RMB_Price'].mean():.0f}" if len(result) > 0 else "0")
    with col_c:
        st.metric("ITEM 종류", f"{result['ITEM'].nunique()}개")

    st.dataframe(
        result[['대구분','ITEM','시즌','MAIN품번','스타일명','컬러','가격대','RMB_Price']].reset_index(drop=True),
        use_container_width=True, height=500
    )

    # 다운로드 버튼
    csv = result.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 검색 결과 CSV 다운로드",
        data=csv,
        file_name=f"검색결과_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

    # ══════════════════════════════
# 페이지 4: 네이버 트렌드
# ══════════════════════════════
elif page == "📈 네이버 트렌드":

    st.title("📈 키워드 트렌드 비교 분석")
    st.caption("네이버 검색어 트렌드 기반 — 브랜드/아이템 비교")
    st.divider()

    from datetime import timedelta

    # ── 프리셋 ──
    PRESETS = {
        "브랜드 비교 (스포츠)": "MLB, 나이키, 아디다스, 데상트, 언더아머",
        "모자 아이템 비교":     "볼캡, 버킷햇, 비니, 캡모자",
        "의류 아이템 비교":     "티셔츠, 원피스, 바람막이, 와이드팬츠, 반바지",
        "신발 아이템 비교":     "스니커즈, 러닝화, 슬리퍼, 샌들",
        "직접 입력":            "",
    }

    AGE_MAP = {
        "10대": "1", "20대": "2", "30대": "3",
        "40대": "4", "50대": "5", "60대↑": "6"
    }

    # ── 설정 ──
    col1, col2 = st.columns([2, 1])
    with col1:
        preset = st.selectbox("📌 프리셋 선택", list(PRESETS.keys()))
    with col2:
        period = st.selectbox("기간", ["최근 1달", "최근 3달", "최근 6달", "최근 1년"])
        days = {"최근 1달": 30, "최근 3달": 90, "최근 6달": 180, "최근 1년": 365}[period]

    # 키워드 입력
    default_kw = PRESETS[preset]
    keywords_input = st.text_input(
        "키워드 입력 (쉼표로 구분, 최대 5개)",
        value=default_kw,
        placeholder="예: MLB, 나이키, 아디다스"
    )

    col3, col4 = st.columns(2)
    with col3:
        selected_gender = st.selectbox(
            "성별",
            ["전체", "여성", "남성"],
            format_func=lambda x: {"전체":"👥 전체","여성":"👩 여성","남성":"👨 남성"}[x]
        )
        gender_code = {"전체": "", "여성": "f", "남성": "m"}[selected_gender]
    with col4:
        selected_ages = st.multiselect(
            "연령대",
            list(AGE_MAP.keys()),
            default=["20대", "30대"]
        )
        age_codes = [AGE_MAP[a] for a in selected_ages]

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    st.caption(f"조회 기간: {start_date} ~ {end_date}")

    if st.button("🔍 트렌드 분석", type="primary"):

        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()][:5]
        if not keywords:
            st.error("키워드를 입력해주세요!")
            st.stop()

        with st.spinner("트렌드 데이터 수집 중..."):

            url = "https://openapi.naver.com/v1/datalab/search"
            headers = {
                "X-Naver-Client-Id": "SDsJUtriFW46zhbycKwN",
                "X-Naver-Client-Secret": "hYRXPdJtq4",
                "Content-Type": "application/json"
            }
            body = {
                "startDate": start_date,
                "endDate": end_date,
                "timeUnit": "week",
                "keywordGroups": [
                    {"groupName": kw, "keywords": [kw]}
                    for kw in keywords
                ],
                "device": "mo",
                "gender": gender_code,
                "ages": age_codes if age_codes else []
            }

            res = requests.post(url, headers=headers, data=json.dumps(body))
            result = res.json()

        if "results" not in result or not result["results"]:
            st.error(f"데이터 조회 실패: {result}")
            st.stop()

        # 데이터 정리
        trend_data = []
        for item in result["results"]:
            for point in item.get("data", []):
                trend_data.append({
                    "키워드": item["title"],
                    "날짜": point["period"],
                    "트렌드지수": point["ratio"]
                })

        if not trend_data:
            st.warning("데이터가 없어요. 키워드나 기간을 바꿔보세요!")
            st.stop()

        df_trend = pd.DataFrame(trend_data)
        df_trend["날짜"] = pd.to_datetime(df_trend["날짜"])

        # 평균 순위
        avg = df_trend.groupby("키워드")["트렌드지수"].mean().sort_values(ascending=False)

        st.success(f"✅ {len(keywords)}개 키워드 트렌드 수집 완료!")
        st.divider()

        # ── KPI 카드 ──
        st.subheader("🏆 평균 트렌드 순위")
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣"]
        cols = st.columns(len(avg))
        for i, (kw, score) in enumerate(avg.items()):
            with cols[i]:
                delta_color = "normal"
                st.metric(
                    f"{medals[i] if i < len(medals) else ''} {kw}",
                    f"{score:.1f}점",
                    help="기간 내 평균 트렌드 지수"
                )

        st.divider()

        # ── 차트 1: 트렌드 추이 라인차트 ──
        st.subheader("📈 주간 트렌드 추이")
        colors = ["#FF6B6B","#4ECDC4","#C8A96E","#96CEB4","#FFEAA7"]

        fig1 = px.line(
            df_trend, x="날짜", y="트렌드지수",
            color="키워드",
            color_discrete_sequence=colors,
            template="plotly_dark",
            markers=True,
            line_shape="spline"
        )
        fig1.update_traces(line_width=2.5, marker_size=5)
        fig1.update_layout(
            margin=dict(l=0,r=0,t=0,b=0),
            height=420,
            yaxis_title="트렌드 지수",
            xaxis_title="",
            legend=dict(
                orientation="h", y=-0.15,
                bgcolor="rgba(0,0,0,0)"
            ),
            hovermode="x unified"
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # ── 차트 2: 평균 순위 바차트 + 파이차트 ──
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 평균 트렌드 지수 비교")
            avg_df = avg.reset_index()
            avg_df.columns = ["키워드","평균지수"]
            avg_df_sorted = avg_df.sort_values("평균지수", ascending=True)

            fig2 = px.bar(
                avg_df_sorted, x="평균지수", y="키워드",
                orientation="h", text="평균지수",
                color="키워드",
                color_discrete_sequence=colors,
                template="plotly_dark"
            )
            fig2.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside"
            )
            fig2.update_layout(
                margin=dict(l=0,r=40,t=0,b=0),
                height=300, showlegend=False,
                xaxis_title="평균 트렌드 지수"
            )
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            st.subheader("🥧 트렌드 점유율")
            fig3 = px.pie(
                avg_df, values="평균지수", names="키워드",
                hole=0.45,
                color_discrete_sequence=colors,
                template="plotly_dark"
            )
            fig3.update_layout(
                margin=dict(l=0,r=0,t=0,b=0),
                height=300,
                legend=dict(orientation="h", y=-0.2)
            )
            st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # ── 차트 3: 기간별 최고점 분석 ──
        st.subheader("📅 기간별 최고 트렌드 키워드")
        df_trend["월"] = df_trend["날짜"].dt.strftime("%Y-%m")
        monthly_max = df_trend.loc[
            df_trend.groupby("월")["트렌드지수"].idxmax()
        ][["월","키워드","트렌드지수"]].reset_index(drop=True)

        fig4 = px.bar(
            monthly_max, x="월", y="트렌드지수",
            color="키워드",
            color_discrete_sequence=colors,
            template="plotly_dark",
            text="키워드"
        )
        fig4.update_traces(textposition="inside")
        fig4.update_layout(
            margin=dict(l=0,r=0,t=0,b=0),
            height=300,
            yaxis_title="트렌드 지수",
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # ── 상세 데이터 테이블 ──
        st.subheader("📋 주간 트렌드 상세")
        pivot = df_trend.pivot_table(
            values="트렌드지수",
            index="날짜",
            columns="키워드",
            aggfunc="mean"
        ).round(1)
        pivot.index = pivot.index.strftime("%Y-%m-%d")
        st.dataframe(pivot, use_container_width=True, height=300)

        csv = df_trend.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 트렌드 데이터 CSV", data=csv,
            file_name=f"트렌드분석_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    else:
        st.info("👆 프리셋 선택 또는 키워드 직접 입력 후 '트렌드 분석' 버튼을 눌러주세요!")
        st.markdown("""
        **사용 방법:**
        - 프리셋 선택 → 브랜드/아이템별 미리 설정된 키워드 자동 입력
        - 직접 입력 → 원하는 키워드 쉼표로 구분 (최대 5개)
        
        **볼 수 있는 것:**
        - 📈 주간 트렌드 추이 라인차트
        - 📊 평균 트렌드 지수 비교
        - 🥧 트렌드 점유율
        - 📅 기간별 최고 트렌드 키워드
        """)
        # ══════════════════════════════
# 페이지 5: 경쟁사 분석
# ══════════════════════════════
elif page == "🏪 경쟁사 분석":

    st.title("⚾ MLB vs 경쟁브랜드 분석")
    st.caption("네이버 쇼핑 실시간 데이터 기반")
    st.divider()

    BRANDS = {
        "MLB":     {"검색명": "MLB",     "구분": "자사",  "color": "#FF6B6B"},
        "나이키":  {"검색명": "나이키",  "구분": "경쟁사", "color": "#4ECDC4"},
        "아디다스":{"검색명": "아디다스","구분": "경쟁사", "color": "#45B7D1"},
        "데상트":  {"검색명": "데상트",  "구분": "경쟁사", "color": "#96CEB4"},
        "언더아머":{"검색명": "언더아머","구분": "경쟁사", "color": "#FFEAA7"},
    }

    # 대카테고리 검색 키워드
    CAT_SEARCH = {
        "의류": ["티셔츠", "의류", "옷"],
        "신발": ["신발", "슈즈"],
        "모자": ["모자", "캡"],
    }

    # 세부카테고리 분류 기준
    SUB_CATEGORIES = {
        "의류": {
            "티셔츠":       ["티셔츠", "반팔", "반소매"],
            "후드":         ["후드", "hoodie"],
            "패딩":         ["패딩", "다운", "점퍼"],
            "바람막이":     ["바람막이", "윈드브레이커", "방풍"],
            "트레이닝팬츠": ["트레이닝", "조거", "스웨트팬츠"],
        },
        "신발": {
            "스니커즈": ["스니커즈", "스니커"],
            "러닝화":   ["러닝화", "런닝화", "running"],
            "슬리퍼":   ["슬리퍼", "샌들"],
        },
        "모자": {
            "볼캡":   ["볼캡", "볼케", "캡"],
            "비니":   ["비니", "beanie"],
            "버킷햇": ["버킷", "bucket"],
        }
    }

    PRICE_ORDER = ["~3만원", "3~5만원", "5~10만원", "10~20만원", "20만원~"]

    def get_price_tier(price):
        if price < 30000:    return "~3만원"
        elif price < 50000:  return "3~5만원"
        elif price < 100000: return "5~10만원"
        elif price < 200000: return "10~20만원"
        else:                return "20만원~"

    def classify_sub(name, cat):
        name_lower = name.lower()
        sub_dict = SUB_CATEGORIES.get(cat, {})
        for sub, keywords in sub_dict.items():
            if any(k in name_lower for k in keywords):
                return sub
        return "기타"

    def search_naver_mlb(keyword, display=100):
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": "SDsJUtriFW46zhbycKwN",
            "X-Naver-Client-Secret": "hYRXPdJtq4"
        }
        params = {"query": keyword, "display": display, "sort": "sim"}
        res = requests.get(url, headers=headers, params=params)
        return res.json().get("items", [])

    # ── 설정 ──
    st.sidebar.header("⚙️ 분석 설정")
    selected_brands = st.sidebar.multiselect(
        "브랜드 선택", list(BRANDS.keys()), default=list(BRANDS.keys()))
    selected_cats = st.sidebar.multiselect(
        "카테고리 선택", ["의류", "신발", "모자"], default=["의류", "신발", "모자"])

    if st.button("🔍 분석 시작", type="primary"):
        all_data = []
        progress = st.progress(0)
        total_steps = len(selected_brands) * len(selected_cats)
        step = 0

        for brand in selected_brands:
            info = BRANDS[brand]
            for cat in selected_cats:
                # 대카테고리 키워드로 검색
                search_keywords = CAT_SEARCH[cat]
                cat_items = []
                for sk in search_keywords:
                    keyword = f"{info['검색명']} {sk}"
                    items = search_naver_mlb(keyword, display=100)
                    cat_items.extend(items)

                # 중복 제거
                seen = set()
                for item in cat_items:
                    pid = item.get("productId","") or item.get("title","")
                    if pid in seen:
                        continue
                    seen.add(pid)

                    price = int(item.get("lprice", 0))
                    if price == 0: continue
                    name = item.get("title","").replace("<b>","").replace("</b>","")

                    all_data.append({
                        "브랜드":      brand,
                        "구분":        info["구분"],
                        "대카테고리":  cat,
                        "세부카테고리": classify_sub(name, cat),
                        "가격대":      get_price_tier(price),
                        "상품명":      name,
                        "쇼핑몰":      item.get("mallName",""),
                        "최저가":      price,
                    })

                step += 1
                progress.progress(step / total_steps)

        if not all_data:
            st.error("데이터를 가져오지 못했어요.")
            st.stop()

        df_mlb = pd.DataFrame(all_data)
        # 기타 제외
        df_mlb = df_mlb[df_mlb["세부카테고리"] != "기타"]

        st.success(f"✅ 총 {len(df_mlb)}개 상품 수집 완료!")
        st.divider()

        brand_colors = {b: BRANDS[b]["color"] for b in selected_brands}

        # ── KPI ──
        cols = st.columns(len(selected_brands))
        for i, brand in enumerate(selected_brands):
            df_b = df_mlb[df_mlb["브랜드"] == brand]
            with cols[i]:
                tag = "🔴 자사" if BRANDS[brand]["구분"] == "자사" else "🔵"
                st.metric(f"{tag} {brand}", f"{len(df_b):,}개")

        st.divider()

        # ── 차트 1: 대카테고리 비중 ──
        st.subheader("📊 카테고리 비중 (의류 vs 신발 vs 모자)")
        cat_pivot = df_mlb.groupby(["브랜드","대카테고리"]).size().reset_index()
        cat_pivot.columns = ["브랜드","대카테고리","수"]
        total = cat_pivot.groupby("브랜드")["수"].transform("sum")
        cat_pivot["비율"] = (cat_pivot["수"] / total * 100).round(1)

        fig1 = px.bar(
            cat_pivot, x="브랜드", y="비율",
            color="대카테고리", barmode="stack", text="비율",
            color_discrete_map={"의류":"#4ECDC4","신발":"#FF6B6B","모자":"#C8A96E"},
            template="plotly_dark"
        )
        fig1.update_traces(texttemplate="%{text:.1f}%", textposition="inside", textfont_size=20)
        fig1.update_layout(
    margin=dict(l=0, r=0, t=0, b=0), 
    height=420,
    yaxis_title="비율 (%)",

    xaxis=dict(
        tickfont=dict(size=18)   # 브랜드명 글씨 크기
    ),

    yaxis=dict(
        title_font=dict(size=18),
        tickfont=dict(size=14)
    ),

    legend=dict(
        orientation="h",
        y=-0.15,
        font=dict(size=20)
    )
)
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # ── 차트 2: 세부카테고리 구성비 ──
        st.subheader("📋 세부카테고리 구성비")
        for cat in selected_cats:
            st.markdown(f"**{cat}**")
            df_cat = df_mlb[df_mlb["대카테고리"] == cat]
            if len(df_cat) == 0: continue

            sub_pivot = df_cat.groupby(["브랜드","세부카테고리"]).size().reset_index()
            sub_pivot.columns = ["브랜드","세부카테고리","수"]
            total2 = sub_pivot.groupby("브랜드")["수"].transform("sum")
            sub_pivot["비율"] = (sub_pivot["수"] / total2 * 100).round(1)

            fig_sub = px.bar(
                sub_pivot, x="브랜드", y="비율",
                color="세부카테고리", barmode="stack", text="비율",
                template="plotly_dark"
            )
            fig_sub.update_traces(texttemplate="%{text:.1f}%", textposition="inside", textfont_size=20)
            fig1.update_layout(
    margin=dict(l=0, r=0, t=0, b=0), 
    height=320,
    yaxis_title="비율 (%)",

    xaxis=dict(
        tickfont=dict(size=25)   # 브랜드명 글씨 크기
    ),

    yaxis=dict(
        title_font=dict(size=18),
        tickfont=dict(size=14)
    ),

    legend=dict(
        orientation="h",
        y=-0.15,
        font=dict(size=20)
    )
)
            st.plotly_chart(fig_sub, use_container_width=True)

        st.divider()

        # ── 차트 3: Price Architecture ──
        st.subheader("💰 Price Architecture")
        col1, col2 = st.columns([2,1])

        with col1:
            price_pivot = df_mlb.groupby(["브랜드","가격대"]).size().reset_index()
            price_pivot.columns = ["브랜드","가격대","수"]
            total3 = price_pivot.groupby("브랜드")["수"].transform("sum")
            price_pivot["비율"] = (price_pivot["수"] / total3 * 100).round(1)
            price_pivot["가격대"] = pd.Categorical(
                price_pivot["가격대"], categories=PRICE_ORDER, ordered=True)
            price_pivot = price_pivot.sort_values("가격대")

            fig3 = px.bar(
                price_pivot, x="브랜드", y="비율",
                color="가격대", barmode="stack", text="비율",
                color_discrete_sequence=["#4ECDC4","#96CEB4","#C8A96E","#FF6B6B","#DDA0DD"],
                template="plotly_dark"
            )
            fig3.update_traces(texttemplate="%{text:.1f}%", textposition="inside", textfont_size=20)
            fig1.update_layout(
    margin=dict(l=0, r=0, t=0, b=0), 
    height=380,
    yaxis_title="비율 (%)",

    xaxis=dict(
        tickfont=dict(size=25)   # 브랜드명 글씨 크기
    ),

    yaxis=dict(
        title_font=dict(size=18),
        tickfont=dict(size=14)
    ),

    legend=dict(
        orientation="h",
        y=-0.15,
        font=dict(size=20)
    )
)
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            st.markdown("**브랜드별 가격 요약**")
            price_summary = df_mlb.groupby("브랜드")["최저가"].agg(
                평균가="mean", 최저가="min", 최고가="max"
            ).round(0).astype(int)
            price_summary["평균가"] = price_summary["평균가"].apply(lambda x: f"{x:,}원")
            price_summary["최저가"] = price_summary["최저가"].apply(lambda x: f"{x:,}원")
            price_summary["최고가"] = price_summary["최고가"].apply(lambda x: f"{x:,}원")
            st.dataframe(price_summary, use_container_width=True)

        st.divider()

        # ── 차트 4: 박스플롯 ──
        st.subheader("📦 가격 분포 비교")
        cat_select = st.selectbox("카테고리", ["전체"] + selected_cats)
        df_box = df_mlb if cat_select == "전체" else df_mlb[df_mlb["대카테고리"] == cat_select]

        fig4 = px.box(
            df_box, x="브랜드", y="최저가", color="브랜드",
            color_discrete_map=brand_colors,
            template="plotly_dark", points="outliers"
        )
        fig4.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=380,
                           showlegend=False, yaxis_title="가격 (원)")
        st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # ── 다운로드 ──
        csv = df_mlb.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 전체 데이터 CSV", data=csv,
            file_name=f"MLB경쟁사분석_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")

    else:
        st.info("👆 왼쪽에서 브랜드/카테고리 선택 후 '분석 시작' 버튼을 눌러주세요!")