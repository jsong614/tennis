import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt
from PIL import Image
import io
import matplotlib.font_manager as fm

# 한글 폰트 설정
try:
    font_path = "/Users/songjasong/Library/Fonts/NanumSquareR.ttf"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
except:
    pass

st.set_page_config(layout="wide")
st.title("🎾 예선 순위 입력 + 본선 대진표 생성기 (기존 CSV 포맷 사용)")

uploaded_file = st.file_uploader("📥 CSV 업로드 ('이름 1 (대표자)', '이름 2', '조' 포함)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if not {'이름 1 (대표자)', '이름 2', '조'}.issubset(df.columns):
        st.error("❗ '이름 1 (대표자)', '이름 2', '조' 열이 CSV에 포함되어야 합니다.")
    else:
        # 팀 이름 생성
        df['팀'] = df['이름 1 (대표자)'].astype(str) + " / " + df['이름 2'].astype(str)
        df['순위'] = None

        st.subheader("📌 각 조별 순위 입력")
        for group in sorted(df['조'].dropna().unique()):
            st.markdown(f"### ⛳ {group}")
            teams_in_group = df[df['조'] == group]
            for i, row in teams_in_group.iterrows():
                rank = st.number_input(
                    f"{row['팀']}의 순위",
                    min_value=1, max_value=10, step=1,
                    key=f"{group}_{row['팀']}"
                )
                df.at[i, '순위'] = rank

        if st.button("✅ 본선 진출팀으로 대진표 생성"):
            qualified = df[df['순위'] <= 2].copy()
            teams = qualified['팀'].dropna().tolist()

            draw_size = len(teams)
            if draw_size < 2 or (draw_size & (draw_size - 1)) != 0:
                st.error(f"❗ 본선 진출팀 수는 2의 제곱이어야 합니다. 현재: {draw_size}팀")
            else:
                st.success(f"🎉 본선 진출팀 {draw_size}팀 → 브래킷 생성 중")

                rounds = int(math.log2(draw_size))
                fig, ax = plt.subplots(figsize=(12, draw_size * 0.45))
                ax.set_xlim(0, rounds + 1)
                ax.set_ylim(0, draw_size)
                ax.axis('off')

                positions = {}
                for i, name in enumerate(teams):
                    y = draw_size - i - 1
                    ax.text(0, y, name, va='center', fontsize=10)
                    positions[(0, i)] = y

                for r in range(1, rounds + 1):
                    step = 2 ** r
                    for m in range(0, draw_size, step):
                        left = positions.get((r - 1, m))
                        right = positions.get((r - 1, m + step // 2))
                        if left is not None and right is not None:
                            mid = (left + right) / 2
                            ax.plot([r - 1, r - 1], [left, right], color='black')
                            ax.plot([r - 1, r], [mid, mid], color='black')
                            positions[(r, m)] = mid

                buf = io.BytesIO()
                plt.tight_layout()
                plt.savefig(buf, format="png", dpi=150)
                buf.seek(0)
                image = Image.open(buf)

                st.image(image, caption="📊 본선 대진표 (브래킷)", use_column_width=True)
                st.download_button("📥 브래킷 PNG 다운로드", data=buf.getvalue(), file_name="bracket.png", mime="image/png")

