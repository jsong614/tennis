import streamlit as st
import pandas as pd
import random
import math

st.title("🎾 테니스 대회 랜덤 조 편성기 (3인 조 중심, 최소 2인 조 1개 허용)")

uploaded_file = st.file_uploader("📥 CSV 파일 업로드", type="csv")

if 'players' not in st.session_state:
    st.session_state.players = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    players = []
    for _, row in df.iterrows():
        if pd.notna(row['이름 1 (대표자)']) and pd.notna(row['연락처 1']):
            players.append({'이름': row['이름 1 (대표자)'], '연락처': row['연락처 1']})
        if pd.notna(row['이름 2']) and pd.notna(row['연락처 2']):
            players.append({'이름': row['이름 2'], '연락처': row['연락처 2']})

    players_df = pd.DataFrame(players)

    st.subheader("📋 참가자 명단")
    st.dataframe(players_df)

    if st.button("🎲 랜덤으로 조 편성"):
        players_df = players_df.sample(frac=1, random_state=42).reset_index(drop=True)
        total = len(players_df)
        num_full_groups = total // 3
        remainder = total % 3

        group_sizes = [3] * num_full_groups

        if remainder == 1:
            # 3+3+3+3+4 → 하나를 줄여서 2인 조 1개로 바꿈
            group_sizes[-1] = 2
        elif remainder == 2:
            group_sizes.append(2)

        # 조 이름 만들기
        group_labels = [chr(65 + i) + "조" for i in range(len(group_sizes))]

        # 조 배정
        group_assignments = []
        idx = 0
        for i, size in enumerate(group_sizes):
            for _ in range(size):
                group_assignments.append(group_labels[i])
                idx += 1

        players_df['조'] = group_assignments
        st.session_state.players = players_df

if st.session_state.players is not None:
    st.subheader("✅ 조 편성 결과")
    st.dataframe(st.session_state.players)

    csv = st.session_state.players.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📤 결과 CSV 다운로드", data=csv, file_name="조편성결과.csv", mime='text/csv')
