import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go

st.set_page_config(page_title="🎾 테니스 대회 대진표", layout="wide")
st.title("🎾 혼합복식 조 편성 및 본선 대진표 시각화")

uploaded_file = st.file_uploader("📥 CSV 업로드 (이름1, 이름2, 연락처1)", type="csv")

if 'teams' not in st.session_state:
    st.session_state.teams = None
if 'draw_teams' not in st.session_state:
    st.session_state.draw_teams = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 팀 구성
    teams = []
    for _, row in df.iterrows():
        if pd.notna(row['이름 1 (대표자)']) and pd.notna(row['이름 2']):
            팀이름 = f"{row['이름 1 (대표자)']} / {row['이름 2']}"
            연락처 = row['연락처 1']
            teams.append({'팀': 팀이름, '연락처': 연락처})
    team_df = pd.DataFrame(teams)

    st.subheader("📋 참가 팀 목록")
    st.dataframe(team_df)

    if st.button("🎲 조 편성"):
        team_df = team_df.sample(frac=1, random_state=42).reset_index(drop=True)
        total = len(team_df)
        num_full = total // 3
        remainder = total % 3

        group_sizes = [3] * num_full
        if remainder == 1 and num_full >= 1:
            group_sizes[-1] = 2
        elif remainder == 2:
            group_sizes.append(2)

        group_labels = [chr(65 + i) + "조" for i in range(len(group_sizes))]
        group_assignments = []
        for i, size in enumerate(group_sizes):
            group_assignments.extend([group_labels[i]] * size)

        # 길이 맞추기
        while len(group_assignments) < len(team_df):
            group_assignments.append('미정')

        team_df['조'] = group_assignments
        st.session_state.teams = team_df

if st.session_state.teams is not None:
    st.subheader("✅ 조 편성 결과")
    st.dataframe(st.session_state.teams)

    st.markdown("---")
    st.header("🏆 본선 대진표 생성")

    draw_size = st.selectbox("드로 수 선택", [4, 8, 16], index=1)

    if st.button("🔀 본선 진출팀 랜덤 배정"):
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
    st.subheader("📄 본선 대진 참가 팀")
    st.dataframe(st.session_state.draw_teams)

    st.subheader("📊 본선 토너먼트 시각화")

    labels = st.session_state.draw_teams['팀'].tolist()

    def plot_bracket(labels):
        fig = go.Figure()
        y_gap = 20
        x_gap = 1
        current_positions = {i: (0, -i * y_gap) for i in range(len(labels))}

        for i, label in current_positions.items():
            fig.add_trace(go.Scatter(
                x=[label[0]], y=[label[1]],
                text=[labels[i]], mode='text', textposition='middle right'
            ))

        round_num = 0
        while len(current_positions) > 1:
            next_positions = {}
            keys = list(current_positions.keys())
            for i in range(0, len(keys), 2):
                left = current_positions[keys[i]]
                right = current_positions[keys[i+1]]
                mid_y = (left[1] + right[1]) / 2
                mid_x = left[0] + x_gap

                # 연결선
                fig.add_trace(go.Scatter(
                    x=[left[0], mid_x], y=[left[1], mid_y],
                    mode="lines", line=dict(color="black")
                ))
                fig.add_trace(go.Scatter(
                    x=[right[0], mid_x], y=[right[1], mid_y],
                    mode="lines", line=dict(color="black")
                ))

                next_positions[i//2] = (mid_x, mid_y)
            current_positions = next_positions
            round_num += 1

        fig.update_layout(height=600, xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
        return fig

    st.plotly_chart(plot_bracket(labels), use_container_width=True)
