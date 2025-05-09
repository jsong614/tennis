import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
import random

st.set_page_config(page_title="🎾 혼복 대회 조 편성 및 본선 대진표", layout="wide")
st.title("🎾 테니스 대회 복식 조 편성기 + 본선 대진표 시각화")

uploaded_file = st.file_uploader("📥 CSV 파일 업로드 (이름1, 이름2, 연락처1)", type="csv")

# 상태 저장
if 'teams' not in st.session_state:
    st.session_state.teams = None
if 'draw_teams' not in st.session_state:
    st.session_state.draw_teams = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 팀 만들기
    teams = []
    for _, row in df.iterrows():
        if pd.notna(row['이름 1 (대표자)']) and pd.notna(row['이름 2']):
            팀이름 = f"{row['이름 1 (대표자)']} / {row['이름 2']}"
            연락처 = row['연락처 1']
            teams.append({'팀': 팀이름, '연락처': 연락처})
    team_df = pd.DataFrame(teams)

    st.subheader("📋 참가 팀 목록")
    st.dataframe(team_df)

    if st.button("🎲 랜덤 조 편성"):
        team_df = team_df.sample(frac=1, random_state=42).reset_index(drop=True)
        total = len(team_df)
        num_full = total // 3
        remainder = total % 3

        group_sizes = [3] * num_full
        if remainder == 1 and num_full >= 1:
            group_sizes[-1] = 2
        elif remainder == 2:
            group_sizes.append(2)

        group_labels = [chr(65+i) + "조" for i in range(len(group_sizes))]
        group_assignments = []
        for i, size in enumerate(group_sizes):
            group_assignments.extend([group_labels[i]] * size)

        if len(group_assignments) < len(team_df):
            group_assignments += ['미정'] * (len(team_df) - len(group_assignments))

        team_df['조'] = group_assignments
        st.session_state.teams = team_df

if st.session_state.teams is not None:
    st.subheader("✅ 조 편성 결과")
    st.dataframe(st.session_state.teams)

    st.markdown("---")
    st.header("🏆 본선 대진표 생성 + 시각화")

    draw_size = st.selectbox("드로 수를 선택하세요", [4, 8, 16], index=1)

    if st.button("🔀 본선 대진표 만들기"):
        df = st.session_state.teams
        qualified = []
        for group in df['조'].unique():
            if group == '미정': continue
            top2 = df[df['조'] == group].head(2)
            qualified.extend(top2.to_dict(orient='records'))

        qualified_df = pd.DataFrame(qualified).sample(frac=1, random_state=123).reset_index(drop=True)

        # 부전승 채우기
        needed = draw_size - len(qualified_df)
        if needed > 0:
            byes = [{'팀': 'BYE', '연락처': '', '조': ''}] * needed
            qualified_df = pd.concat([qualified_df, pd.DataFrame(byes)], ignore_index=True)

        qualified_df = qualified_df.sample(frac=1, random_state=99).reset_index(drop=True)
        st.session_state.draw_teams = qualified_df

if st.session_state.draw_teams is not None:
    st.subheader("📄 본선 참가 팀 (랜덤 정렬 + 부전승 포함)")
    st.dataframe(st.session_state.draw_teams)

    # 토너먼트 대진표 시각화 (Plotly)
    st.subheader("📊 본선 대진표 시각화")

    labels = st.session_state.draw_teams['팀'].tolist()

    def make_bracket(labels):
        fig = go.Figure()

        # 레벨별 Y좌표 계산
        levels = int(math.log2(len(labels)))
        positions = {}
        for i in range(len(labels)):
            positions[i] = (0, i * 2)

        line_color = "black"
        textprops = dict(font=dict(size=12), textposition="middle right")

        match_id = 0
        next_level = len(labels)
        current_level = len(labels)

        # 첫 라운드 (x=0)
        for i in range(0, len(labels), 2):
            fig.add_trace(go.Scatter(
                x=[0, 0], y=[positions[i][1], positions[i+1][1]],
                mode="lines", line=dict(color=line_color),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[0], y=[positions[i][1]], text=[labels[i]],
                mode="text", showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[0], y=[positions[i+1][1]], text=[labels[i+1]],
                mode="text", showlegend=False
            ))

        # 다음 라운드들
        x = 1
        while current_level > 1:
            next_positions = {}
            for i in range(0, current_level, 2):
                y1 = positions[i][1]
                y2 = positions[i+1][1]
                y_mid = (y1 + y2) / 2
                fig.add_trace(go.Scatter(
                    x=[x-1, x], y=[y_mid, y_mid],
                    mode="lines", line=dict(color=line_color),
                    showlegend=False
                ))
                next_positions[i//2] = (x, y_mid)
            positions = next_positions
            current_level = len(positions)
            x += 1

        fig.update_layout(
            height=600,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        return fig

    st.plotly_chart(make_bracket(labels), use_container_width=True)
