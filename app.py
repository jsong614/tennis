import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt
from PIL import Image
import io
import matplotlib.font_manager as fm

# 📌 한글 폰트 설정 (환경 맞춰 조정)
try:
    font_path = "/Users/songjasong/Library/Fonts/NanumSquareR.ttf"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
except:
    pass

st.set_page_config(layout="wide")
st.title("🎾 혼복 본선 대진표 브래킷 생성기 (CSV 기반)")

uploaded_file = st.file_uploader("📥 팀명('팀' 열 포함) CSV 파일 업로드", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if '팀' not in df.columns:
        st.error("❗ CSV에 '팀'이라는 열이 있어야 합니다.")
    else:
        teams = df['팀'].dropna().tolist()
        draw_size = len(teams)

        # 드로수가 2의 거듭제곱인지 확인
        if (draw_size & (draw_size - 1)) != 0:
            st.warning(f"⚠️ 현재 {draw_size}개 팀 → 2ⁿ 형태가 아니에요. 브래킷이 비정형일 수 있습니다.")

        rounds = int(math.log2(draw_size))

        # 브래킷 시각화
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

        # 이미지 저장 & 출력
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=150
