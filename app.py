import streamlit as st
import pandas as pd
import random
import math

st.title("🎾 테니스 대회 복식 조 편성기 (팀 기준, 3팀 조)")

uploaded_file = st.file_uploader("📥 혼복 CSV 파일 업로드", type="csv")

if 'teams' not in st.session_state:
    st.session_state.teams = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 팀 단위로 이름/연락처 구성
    teams = []
    for _, row in df.iterrows():
        if pd.notna(row['이름 1 (대표자)']) and pd.notna(row['이름 2']):
            팀이름 = f"{row['이름 1 (대표자)']} / {row['이름 2']}"
            연락처 = row['연락처 1']
            teams.append({'팀': 팀이름, '대표자 연락처': 연락처})

    team_df = pd.DataFrame(teams)

    st.subheader("📋 복식 팀 목록")
    st.dataframe(team_df)

    if st.button("🎲 랜덤으로 조 편성"):
        team_df = team_df.sample(frac=1, random_state=42).reset_index(drop=True)
        total = len(team_df)
        num_full_groups = total // 3
        remainder = total % 3

        group_sizes = [3] * num_full_groups
        if remainder == 1:
            group_sizes[-1] = 2
        elif remainder == 2:
            group_sizes.append(2)

        group_labels = [chr(65 + i) + "조" for i in range(len(group_sizes))]

        group_assignments = []
        idx = 0
        for i, size in enumerate(group_sizes):
            for _ in range(size):
                group_assignments.append(group_labels[i])
                idx += 1

        team_df['조'] = group_assignments
        st.session_state.teams = team_df

if st.session_state.teams is not None:
    st.subheader("✅ 조 편성 결과 (팀 기준)")
    st.dataframe(st.session_state.teams)

    csv = st.session_state.teams.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📤 결과 CSV 다운로드", data=csv, file_name="혼복_조편성결과.csv", mime='text/csv')
