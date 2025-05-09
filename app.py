# app.py
import streamlit as st
import pandas as pd
import random
import math

st.title("🎾 테니스 대회 랜덤 조 편성기")

uploaded_file = st.file_uploader("📥 CSV 참가자 명단 업로드", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📋 원본 데이터")
    st.dataframe(df)

    if st.button("랜덤으로 3명씩 조 편성"):
        df = df.dropna()
        players = df.sample(frac=1, random_state=42).reset_index(drop=True)
        num_groups = math.ceil(len(players) / 3)
        group_labels = [chr(65 + i) + "조" for i in range(num_groups)]
        players["조"] = [group_labels[i // 3] for i in range(len(players))]

        st.subheader("✅ 조 편성 결과")
        st.dataframe(players)

        csv = players.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📤 결과 CSV 다운로드", data=csv, file_name="조편성결과.csv", mime='text/csv')
