import streamlit as st
import pandas as pd
import math
import random

st.set_page_config(page_title="🎾 혼복 조 편성기", layout="wide")
st.title("🎾 테니스 대회 복식 조 편성 및 본선 대진표 생성기")

uploaded_file = st.file_uploader("📥 CSV 파일 업로드 (혼복)", type="csv")

# 상태 초기화
if 'teams' not in st.session_state:
    st.session_state.teams = None
if 'draw' not in st.session_state:
    st.session_state.draw = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 팀 데이터 추출
    teams = []
    for _, row in df.iterrows():
        if pd.notna(row['이름 1 (대표자)']) and pd.notna(row['이름 2']):
            팀이름 = f"{row['이름 1 (대표자)']} / {row['이름 2']}"
            연락처 = row['연락처 1']
            teams.append({'팀': 팀이름, '대표자 연락처': 연락처})

    team_df = pd.DataFrame(teams)
    st.subheader("📋 참가 팀 목록")
    st.dataframe(team_df)

    if st.button("🎲 조 편성 (3팀씩 랜덤)"):
        team_df = team_df.sample(frac=1, random_state=42).reset_index(drop=True)
        total = len(team_df)
        num_full_groups = total // 3
        remainder = total % 3

        group_sizes = [3] * num_full_groups
        if remainder == 1 and num_full_groups >= 1:
            group_sizes[-1] = 2
        elif remainder == 2:
            group_sizes.append(2)

        group_labels = [chr(65 + i) + "조" for i in range(len(group_sizes))]

        group_assignments = []
        for i, size in enumerate(group_sizes):
            group_assignments.extend([group_labels[i]] * size)

        # 조 리스트 길이 조정
        diff = len(team_df) - len(group_assignments)
        if diff > 0:
            group_assignments += ["미정"] * diff
        elif diff < 0:
            group_assignments = group_assignments[:len(team_df)]

        team_df['조'] = group_assignments
        st.session_state.teams = team_df

if st.session_state.teams is not None:
    st.subheader("✅ 조 편성 결과")
    st.dataframe(st.session_state.teams)

    csv = st.session_state.teams.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📤 조편성 결과 다운로드", data=csv, file_name="혼복_조편성결과.csv", mime='text/csv')

    st.markdown("---")
    st.header("🏆 본선 대진표 생성")

    draw_size = st.selectbox("드로 수를 선택하세요", [4, 8, 16, 32], index=2)

    if st.button("🔀 본선 대진표 생성"):
        df = st.session_state.teams

        # 각 조에서 1위, 2위 진출 가정
        group_list = df['조'].unique()
        qualified = []
        for group in group_list:
            group_teams = df[df['조'] == group]
            group_teams = group_teams.head(2)  # 상위 2팀만 본선 진출
            qualified.extend(group_teams.to_dict(orient='records'))

        qualified_df = pd.DataFrame(qualified).sample(frac=1, random_state=123).reset_index(drop=True)

        # BYE 처리
        needed_byes = draw_size - len(qualified_df)
        byes = [{'팀': 'BYE', '대표자 연락처': '', '조': ''}] * needed_byes
        draw_df = pd.concat([qualified_df, pd.DataFrame(byes)], ignore_index=True)
        draw_df = draw_df.sample(frac=1, random_state=99).reset_index(drop=True)

        # 대진표 만들기
        matches = []
        for i in range(0, draw_size, 2):
            t1 = draw_df.iloc[i]['팀']
            t2 = draw_df.iloc[i+1]['팀']
            matches.append({'경기': f'{i//2 + 1}경기', '팀1': t1, '팀2': t2})

        draw_result = pd.DataFrame(matches)
        st.session_state.draw = draw_result

if st.session_state.draw is not None:
    st.subheader("🎾 본선 대진표")
    st.dataframe(st.session_state.draw)

    csv = st.session_state.draw.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📤 본선 대진표 다운로드", data=csv, file_name="혼복_본선대진표.csv", mime='text/csv')
