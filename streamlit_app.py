import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="K-Lyric 101", layout="wide", page_icon="🎧")

# 2. 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

# 3. 커스텀 CSS (메트릭 폰트 크기 강제 적용 버전)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* 타이틀 디자인 유지 */
    .main-title-kr {
        font-family: 'Inter', sans-serif;
        font-size: 4.5rem !important; 
        font-weight: 900 !important;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #7d8dec 0%, #4a5fcc 50%, #2a3f88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem !important;
        line-height: 1.1 !important;
    }

    .brand-title-en {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        margin-top: -10px !important;
        margin-bottom: 0.5rem !important;
    }

    /* 분석 버튼 스타일 유지 */
    .stButton>button {
        background-color: #4e5ec5 !important; 
        border: none !important;
        border-radius: 2px !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.73rem !important;
        min-width: 150px !important;
        height: 3.84rem !important;
        margin-top: 20px !important;  
    }
    
    /* --- [핵심 수정] 메트릭 제목 및 값 크기 조정 (더 구체적인 선택자 사용) --- */
    /* 제목(Label): 1.6rem -> 0.96rem (40% 축소) */
    [data-testid="stMetricLabel"] div p {
        font-size: 0.96rem !important;
        color: #8b92b2 !important;
        font-weight: 700 !important;
    }
    
    /* 값(Value): 1.67rem -> 1.92rem (15% 확대) */
    [data-testid="stMetricValue"] div {
        font-size: 1.92rem !important;
        color: #4a5fcc !important;
        font-weight: 800 !important;
    }

    /* 퀴즈 결과창 스타일 유지 */
    .custom-result-box { padding: 12px 20px; border-radius: 8px; margin-bottom: 25px; }
    .correct-box { background: rgba(74, 95, 204, 0.1); border-color: #4a5fcc; border: 1px solid #4a5fcc; }
    .wrong-box { background: rgba(255, 75, 75, 0.05); border-color: rgba(255, 75, 75, 0.4); border: 1px solid rgba(255, 75, 75, 0.4); }
    .result-title { font-size: 1.25rem !important; font-weight: 800 !important; display: block; margin-bottom: 2px; }
    .result-sub { font-size: 1.0rem !important; color: #FFFFFF; display: block; }

    .lyrics-card { border-left: 4px solid #4a5fcc; padding: 24px; background: rgba(45, 53, 72, 0.25); height: 520px; overflow-y: auto; }
    .analysis-card { border-left: 4px solid #2a3f88; padding: 16px 20px; margin-bottom: 16px; background: rgba(45, 53, 72, 0.25); }
    </style>
    """, unsafe_allow_html=True)

# 헤더
st.markdown('<div class="main-title-kr">가사학개론</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title-en">K-Lyric 101</div>', unsafe_allow_html=True)
st.divider()

# 입력
lyrics_input = st.text_area("📝 가사 입력", height=180, key="lyrics_main")
if st.button("🚀 분석을 실행해줘!"):
    if lyrics_input.strip():
        morphs = okt.pos(lyrics_input, stem=True)
        target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
        all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
        df_all = pd.DataFrame(all_words)
        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)
            st.session_state.analyzed_data = { 'all_words': all_words, 'df_counts': df_counts, 'lyrics_input': lyrics_input }

# 출력
if st.session_state.analyzed_data:
    data = st.session_state.analyzed_data
    df_counts, all_words, saved_lyrics = data['df_counts'], data['all_words'], data['lyrics_input']

    st.divider()
    st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

    # 대시보드 (스타일 적용 대상)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 단어", f"→ {len(all_words)}")
    m2.metric("고유 단어", f"→ {len(df_counts)}")
    m3.metric("최빈 단어", f"→ {df_counts.iloc[0]['단어']}")
    m4.metric("주요 품사", f"→ {df_counts.iloc[0]['품사']}")

    st.divider()
    # 번역 및 데이터 시각화 로직 (이전과 동일)
    c_l, c_r = st.columns([1.2, 1])
    with c_l:
        st.markdown("### 🌍 가사 대조 번역")
        lines = [line.strip() for line in saved_lyrics.split('\n') if line.strip()]
        html_lyrics = '<div class="lyrics-card">'
        for line in lines:
            try:
                translated = translator.translate(line, dest='en').text
                html_lyrics += f'<div style="margin-bottom:20px;"><span style="color:white; font-weight:600;">{line}</span><br><span style="color:#8b92b2; font-style:italic; font-size:0.95rem;">{translated}</span></div>'
            except: html_lyrics += f'<div>{line}</div>'
        st.markdown(html_lyrics + '</div>', unsafe_allow_html=True)
    with c_r:
        st.markdown("### 📊 분석 데이터")
        st.data_editor(df_counts, use_container_width=True, height=520)

    # 퀴즈 (3문항 유지)
    st.divider()
    st.markdown("### 📝 오늘의 가사 퀴즈")
    top_word, top_pos = df_counts.iloc[0]['단어'], df_counts.iloc[0]['품사']
    
    # Q1
    st.markdown(f'<div style="background:rgba(45,53,72,0.15); border:1px solid rgba(74,95,204,0.3); border-radius:12px; padding:12px 20px; margin-bottom:10px;">Q1. \'{top_word}\'의 품사는?</div>', unsafe_allow_html=True)
    ans1 = st.radio("Q1", ["명사", "동사", "형용사", "부사"], index=None, key="uq1", label_visibility="collapsed")
    if ans1:
        res_class = "correct-box" if ans1 == top_pos else "wrong-box"
        res_txt = "🎉 정답입니다!" if ans1 == top_pos else "아쉬워요! 🧐"
        st.markdown(f'<div class="custom-result-box {res_class}"><span class="result-title">{res_txt}</span><span class="result-sub">분석 결과와 대조해 보세요.</span></div>', unsafe_allow_html=True)