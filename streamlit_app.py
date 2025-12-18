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

# --- 세션 상태 초기화 ---
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

# 3. 커스텀 CSS (이미지 스타일 반영: 이중 타이틀 구조)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* 메인 한국어 타이틀 스타일 */
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
        padding-top: 1rem;
    }

    /* 서브 영어 타이틀 스타일 */
    .brand-title-en {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        margin-top: -10px !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: 1px;
    }
    
    .sub-text {
        color: #8b92b2 !important;
        font-size: 1.1rem !important; 
        font-weight: 500;
        margin-bottom: 1.5rem !important; 
    }

    hr { border-bottom: 1px solid #2d3548 !important; }

    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 25px !important; 
    }

    .stTextArea textarea {
        background-color: rgba(20, 27, 45, 0.7) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #2d3548 !important;
    }

    /* 버튼 스타일: 단색 #4e5ec5 + 스퀘어 유지 */
    .stButton>button {
        background-color: #4e5ec5 !important; 
        border: none !important;
        border-radius: 2px !important;
        color: #FFFFFF !important;
        font-weight: 700;
        width: auto !important;
        min-width: 150px !important;
        height: 3.84rem !important;   
        font-size: 1.44rem !important; 
        margin-top: 20px !important;  
        display: flex !important;
        justify-content: flex-start !important; 
        padding-left: 30px !important;
        padding-right: 30px !important;
        align-items: center !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button:hover {
        background-color: #5d6edb !important; 
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }

    [data-testid="stMetricLabel"] p { 
        font-size: 1.6rem !important; 
        color: #FFFFFF !important; 
        font-weight: 900 !important; 
        margin-bottom: 8px !important; 
    }
    [data-testid="stMetricValue"] { 
        font-size: 1.67rem !important; 
        color: #4a5fcc !important; 
        font-weight: 700 !important; 
    }

    .lyrics-card {
        border-left: 4px solid #4a5fcc;
        padding: 24px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        border: 1px solid rgba(45, 53, 72, 0.5);
        height: 520px;
        overflow-y: auto;
    }
    
    .kr-txt { font-size: 1.1rem; color: #FFFFFF; font-weight: 600; display: block; margin-bottom: 4px; }
    .en-txt { font-size: 0.95rem; color: #8b92b2; font-weight: 400; display: block; font-style: italic; }

    .analysis-card {
        border-left: 4px solid #2a3f88;
        padding: 16px 20px;
        margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        border: 1px solid rgba(45, 53, 72, 0.5);
    }
    
    .pos-title { font-size: 1.3rem !important; font-weight: 800 !important; color: #7d8dec; margin-bottom: 10px; }
    .pos-desc { font-size: 1.05rem !important; color: #8b92b2; margin-bottom: 14px; line-height: 1.6; }
    
    .quiz-outer-box {
        background: rgba(45, 53, 72, 0.15);
        border: 1px solid rgba(74, 95, 204, 0.3);
        border-radius: 12px;
        padding: 12px 20px;
        margin-top: 5px;
        margin-bottom: 25px; 
    }
    
    div[data-testid="stRadio"] > div { gap: 0px !important; margin-top: -12px !important; }
    [data-testid="stWidgetLabel"] { display: none; }

    .custom-result-box {
        padding: 12px 20px; 
        border-radius: 8px;
        border: 1px solid transparent;
        animation: fadeInUp 0.25s ease-out forwards;
    }
    .correct-box { background: rgba(74, 95, 204, 0.1); border-color: #4a5fcc; }
    .wrong-box { background: rgba(255, 75, 75, 0.05); border-color: rgba(255, 75, 75, 0.4); }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .lyrics-card::-webkit-scrollbar { width: 6px; }
    .lyrics-card::-webkit-scrollbar-thumb { background: #2a3f88; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 헤더 섹션 (이미지 디자인 반영) ---
st.markdown('<div class="main-title-kr">가사학개론</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title-en">K-Lyric 101</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">AI 기반 K-POP 가사 데이터 분석 및 언어 학습 엔진</p>', unsafe_allow_html=True)
st.divider()

# --- 입력 섹션 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석을 실행해줘!")

# --- 분석 로직 ---
if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('데이터 분석 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

            if not df_all.empty:
                df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)
                st.session_state.analyzed_data = {
                    'all_words': all_words,
                    'df_counts': df_counts,
                    'lyrics_input': lyrics_input
                }
    else:
        st.error("가사를 입력해 주세요.")

# --- 출력 섹션 ---
if st.session_state.analyzed_data:
    data = st.session_state.analyzed_data
    df_counts = data['df_counts']
    all_words = data['all_words']
    saved_lyrics = data['lyrics_input']

    st.divider()
    st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

    # 1. 요약 대시보드
    m1, m2, m3, m4 = st.columns(4)
    w_arrow = "→ " 
    m1.metric("전체 단어", f"{w_arrow}{len(all_words)}")
    m2.metric("고유 단어", f"{w_arrow}{len(df_counts)}")
    m3.metric("최빈 단어", f"{w_arrow}{df_counts.iloc[0]['단어']}")
    m4.metric("주요 품사", f"{w_arrow}{df_counts.iloc[0]['품사']}")

    # 2. 번역 및 데이터 섹션
    st.divider()
    c_l, c_r = st.columns([1.2, 1])
    with c_l:
        st.markdown("### 🌍 가사 대조 번역")
        lines = [line.strip() for line in saved_lyrics.split('\n') if line.strip()]
        html_output = '<div class="lyrics-card">'
        for line in lines:
            try:
                translated = translator.translate(line, dest='en').text
                line_html = f'<div style="margin-bottom:20px;"><span class="kr-txt">{line}</span><span class="en-txt">{translated}</span></div>'
                html_output += line_html
            except:
                html_output += f'<div style="margin-bottom:20px;"><span class="kr-txt">{line}</span></div>'
        html_output += '</div>'
        st.markdown(html_output, unsafe_allow_html=True)

    with c_r:
        st.markdown("### 📊 분석 데이터")
        df_display = df_counts.copy()
        df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
        st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True, use_container_width=True, height=520)

    # 3. 그래프
    st.divider()
    st.markdown("### 📈 단어 빈도 시각화")
    top_20 = df_counts.head(20)
    fig = px.bar(top_20, x='단어', y='횟수', color='품사', color_discrete_map={'명사': '#7d8dec', '동사': '#4a5fcc', '형용사': '#2a3f88', '부사': '#8b92b2'}, template='plotly_dark')
    fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # 4. 문법 학습 및 퀴즈 섹션 (동일 로직 유지)
    st.divider()
    st.markdown("### 📚 가사 속 문법 학습")
    # ... (중략: 기존 문법 카드 및 퀴즈 로직 코드 동일하게 삽입)