import streamlit as st
import pandas as pd
import random

st.title("🎾 테니스 복식 대회 운영 플랫폼")

uploaded_file = st.file_uploader("📥 CSV 업로드 ('이름 1 (대표자)', '이름 2', '연락처 1' 포함)", type="csv")

if 'teams' not in st.session_state:
    st.session_state.teams = None

# 1️⃣ 팀 구성 및 조 편성
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    teams = []
    for _, row in df.iterrows():
        if pd.notna(row['이름 1 (대표자)']) and pd.notna(row['이름 2']):
            팀이름 = f"{row['이름 1 (대표자)']} / {row['이름 2']}"
            연락처 = row['연락처 1']
            teams.append({'팀': 팀이름, '대표자 연락처': 연락처})

    team_df = pd.DataFrame(teams)

    st.subheader("📋 참가 팀 목록")
    st.dataframe(team_df)

    if st.button("🎲 랜덤으로 조 편성"):
        team_df = team_df.sample(frac=1, random_state=42).reset_index(drop=True)
        total = len(team_df)

        group_sizes = [3] * (total // 3)
        remainder = total % 3

        if remainder == 1 and len(group_sizes) >= 2:
            group_sizes[-1] = 2
            group_sizes[-2] = 2
        elif remainder == 1:
            group_sizes.append(2)
        elif remainder == 2:
            group_sizes.append(2)

        group_labels = [f"{i+1}조" for i in range(len(group_sizes))]

        group_assignments = []
        for i, size in enumerate(group_sizes):
            group_assignments.extend([group_labels[i]] * size)

        # 길이 보정
        diff = len(team_df) - len(group_assignments)
        if diff > 0:
            group_assignments += [group_labels[-1]] * diff
        elif diff < 0:
            group_assignments = group_assignments[:len(team_df)]

        team_df['조'] = group_assignments
        st.session_state.teams = team_df

# 2️⃣ 조 편성 결과 + 순위 입력
if st.session_state.teams is not None:
    df = st.session_state.teams.copy()
    df['순위'] = None

    st.subheader("🏅 조별 순위 입력 (1~3등만 허용)")
    for group in sorted(df['조'].unique(), key=lambda x: int(x.replace("조", ""))):
        st.markdown(f"### ⛳ {group}")
        group_df = df[df['조'] == group]
        for i, row in group_df.iterrows():
            rank = st.number_input(
                f"{row['팀']} (순위 입력)",
                min_value=1, max_value=3, step=1,
                key=f"{group}_{row['팀']}"
            )
            df.at[i, '순위'] = rank

    st.subheader("📋 전체 결과 (조 + 팀 + 순위)")
    st.dataframe(df)

    csv_all = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 전체 결과 CSV 다운로드", data=csv_all, file_name="전체결과_순위포함.csv", mime="text/csv")

    # 3️⃣ 본선 진출팀 추출
    st.subheader("✅ 본선 진출팀 (조별 1~2위)")
    qualified = df[df['순위'] <= 2].copy()
    qualified = qualified.sort_values(by=['조', '순위'])
    st.dataframe(qualified[['조', '팀', '순위']])

    csv_qualified = qualified.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 본선 진출팀 CSV 다운로드", data=csv_qualified, file_name="본선진출팀.csv", mime="text/csv")
