import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 커스텀 CSS (레이블 하단 여백 추가)
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #121212, #191414) !important;
        color: #E0E0E0 !important;
    }
    
    .main-product-title {
        font-family: 'Inter', sans-serif;
        font-size: 5rem !important;
        font-weight: 900 !important;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #1DB954 0%, #1ED760 50%, #81EEA3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        line-height: 1.2;
    }
    
    .sub-text {
        color: #1DB954 !important;
        font-size: 1.3rem !important;
        font-weight: 600;
        margin-bottom: 3rem;
        opacity: 0.9;
    }

    /* [수정] 가사 입력 레이블 아래에 스페이스 추가 */
    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 25px !important; /* 여백을 25px로 늘려 간격을 확보 */
    }

    .stTextArea textarea {
        background-color: #282828 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #404040 !important;
    }

    .stButton>button {
        width: auto !important;
        min-width: 160px;
        border-radius: 4px !important;
        background-color: #1DB954 !important;
        color: white !important;
        font-weight: 700;
        height: 3.2rem;
        border: none;
    }

    [data-testid="stMetricLabel"] p {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.0rem !important;
        font-weight: 400 !important;
        color: #1DB954 !important;
    }
    
    .analysis-card {
        border-left: 3px solid #1DB954;
        padding: 12px 18px;
        margin-bottom: 12px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 0 12px 12px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 헤더 섹션 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Advanced Lyrics Analytics & Grammar Engine</p>', unsafe_allow_html=True)

# --- 입력 섹션 ---
# CSS에서 label p의 margin-bottom을 조정했으므로 위젯만 호출하면 됩니다.
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

st.write("") 

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석 실행")

st.write("") 
st.write("") 

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('데이터 분석 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 요약 대시보드
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("전체 단어", f"{len(all_words)}")
            m2.metric("고유 단어", f"{len(df_counts)}")
            m3.metric("최빈 단어", df_counts.iloc[0]['단어'])
            m4.metric("주요 품사", df_counts.iloc[0]['품사'])
            
            st.divider()
            # ... (이하 로직 생략)