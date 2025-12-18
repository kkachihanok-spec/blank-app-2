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

# 3. 커스텀 CSS (퀴즈 결과 텍스트 크기 통일 반영)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* 타이틀 디자인 */
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

    /* 분석 버튼 스타일 */
    .stButton>button {
        background-color: #4e5ec5 !important; 
        border: none !important;
        border-radius: 2px !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.73rem !important;
        width: auto !important;
        min-width: 150px !important;
        height: 3.84rem !important;
        margin-top: 20px !important;  
        display: flex !important;
        justify-content: center !important; 
        padding-left: 30px !important;
        padding-right: 30px !important;
        align-items: center !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }

    /* 퀴즈 박스 및 결과창 */
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
    div[data-testid="stRadio"] label { color: white !important; font-size: 0.95rem !important; }

    /* --- [수정] 텍스트 크기 일정하게 고정 --- */
    .custom-result-box {
        padding: 16px 20px; 
        border-radius: 8px;
        border: 1px solid transparent;
        animation: fadeInUp 0.25s ease-out forwards;
        margin-bottom: 25px;
    }
    .correct-box { background: rgba(74, 95, 204, 0.1); border-color: #4a5fcc; }
    .wrong-box { background: rgba(255, 75, 75, 0.05); border-color: rgba(255, 75, 75, 0.4); }
    
    /* 타이틀 크기 통일 */
    .result-title { 
        font-size: 1.3rem !important; 
        font-weight: 800 !important; 
        margin-bottom: 6px !important; 
        display: block;
    }
    /* 설명글 크기 통일 */
    .result-sub { 
        color: #FFFFFF; 
        font-size: 1.1rem !important; 
        opacity: 0.9; 
        line-height: 1.4;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 기타 레이아웃 유지 */
    .stTextArea textarea { background-color: rgba(20, 27, 45, 0.7) !important; color: #FFFFFF !important; border-radius: 12px !important; }
    .lyrics-card { border-left: 4px solid #4a5fcc; padding: 24px; background: rgba(45, 53, 72, 0.25); height: 520px; overflow-y: auto; }
    .analysis-card { border-left: 4px solid #2a3f88; padding: 16px 20px; margin-bottom: 16px; background: rgba(45, 53, 72, 0.25); }
    </style>
    """, unsafe_allow_html=True)

# --- [4] 헤더 섹션 ---
st.markdown('<div class="main-title-kr">가사학개론</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title-en">K-Lyric 101</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">AI 기반 K-POP 가사 데이터 분석 및 언어 학습 엔진</p>', unsafe_allow_html=True)
st.divider()

# --- [5] 입력 섹션 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석을 실행해줘!")

# --- [6] 분석 로직 ---
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

# --- [7] 출력 섹션 ---
if st.session_state.analyzed_data:
    data = st.session_state.analyzed_data
    df_counts = data['df_counts']
    all_words = data['all_words']
    saved_lyrics = data['lyrics_input']

    st.divider()
    st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

    # 대시보드
    m1, m2, m3, m4 = st.columns(4)
    w_arrow = "→ " 
    m1.metric("전체 단어", f"{w_arrow}{len(all_words)}")
    m2.metric("고유 단어", f"{w_arrow}{len(df_counts)}")
    m3.metric("최빈 단어", f"{w_arrow}{df_counts.iloc[0]['단어']}")
    m4.metric("주요 품사", f"{w_arrow}{df_counts.iloc[0]['품사']}")

    # 번역/데이터
    st.divider()
    c_l, c_r = st.columns([1.2, 1])
    with c_l:
        st.markdown("### 🌍 가사 대조 번역")
        lines = [line.strip() for line in saved_lyrics.split('\n') if line.strip()]
        html_output = '<div class="lyrics-card">'
        for line in lines:
            try:
                translated = translator.translate(line, dest='en').text
                html_output += f'<div style="margin-bottom:20px; border-bottom:1px solid rgba(141,146,178,0.1); padding-bottom:10px;"><span class="kr-txt">{line}</span><span class="en-txt">{translated}</span></div>'
            except:
                html_output += f'<div style="margin-bottom:20px;"><span class="kr-txt">{line}</span></div>'
        html_output += '</div>'
        st.markdown(html_output, unsafe_allow_html=True)

    with c_r:
        st.markdown("### 📊 분석 데이터")
        df_display = df_counts.copy()
        df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
        st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True, use_container_width=True, height=520)

    # 퀴즈 섹션 (텍스트 크기 통일 적용)
    st.divider()
    st.markdown("### 📝 오늘의 가사 퀴즈")
    
    top_word = df_counts.iloc[0]['단어']
    top_pos = df_counts.iloc[0]['품사']
    other_pos_df = df_counts[df_counts['품사'] != top_pos]
    second_word = other_pos_df.iloc[0]['단어'] if not other_pos_df.empty else "가사"
    second_pos = other_pos_df.iloc[0]['품사'] if not other_pos_df.empty else "명사"
    unique_count = len(df_counts)

    # Q1
    st.markdown(f'<div class="quiz-outer-box"><div style="line-height: 1.2; margin-bottom: 4px;"><span style="color: #7d8dec; font-weight: 900; font-size: 1.2rem;">Q1.</span> <span style="color: white; font-size: 1.1rem; font-weight: 700;">가장 많이 사용된 \'{top_word}\'의 품사는?</span></div>', unsafe_allow_html=True)
    ans1 = st.radio("Q1선택", ["명사", "동사", "형용사", "부사"], index=None, key="uq1", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    if ans1:
        if ans1 == top_pos:
            st.markdown(f'<div class="custom-result-box correct-box"><span class="result-title" style="color:#7d8dec;">🎉 정답입니다!</span><span class="result-sub">\'{top_word}\'은(는) 완벽한 <b>{top_pos}</b>입니다.</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="custom-result-box wrong-box"><span class="result-title" style="color:#ff4b4b;">아쉬워요! 🧐</span><span class="result-sub">위쪽 분석 데이터를 다시 확인해 보세요.</span></div>', unsafe_allow_html=True)

    # Q2
    st.markdown(f'<div class="quiz-outer-box"><div style="line-height: 1.2; margin-bottom: 4px;"><span style="color: #7d8dec; font-weight: 900; font-size: 1.2rem;">Q2.</span> <span style="color: white; font-size: 1.1rem; font-weight: 700;">단어 \'{second_word}\'의 품사는 무엇일까요?</span></div>', unsafe_allow_html=True)
    ans2 = st.radio("Q2선택", ["명사", "동사", "형용사", "부사"], index=None, key="uq2", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    if ans2:
        if ans2 == second_pos:
            st.markdown(f'<div class="custom-result-box correct-box"><span class="result-title" style="color:#7d8dec;">🎉 정답입니다!</span><span class="result-sub">\'{second_word}\'은(는) <b>{second_pos}</b>가 맞습니다.</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="custom-result-box wrong-box"><span class="result-title" style="color:#ff4b4b;">아쉬워요! 🧐</span><span class="result-sub">단어의 의미를 다시 한번 생각해 보세요.</span></div>', unsafe_allow_html=True)

    # Q3
    st.markdown(f'<div class="quiz-outer-box"><div style="line-height: 1.2; margin-bottom: 4px;"><span style="color: #7d8dec; font-weight: 900; font-size: 1.2rem;">Q3.</span> <span style="color: white; font-size: 1.1rem; font-weight: 700;">이 가사에는 총 몇 개의 고유 단어가 사용되었나요?</span></div>', unsafe_allow_html=True)
    ans3 = st.radio("Q3선택", [f"{unique_count}개", f"{unique_count+3}개", f"{max(0, unique_count-5)}개", "10개"], index=None, key="uq3", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    if ans3:
        if ans3 == f"{unique_count}개":
            st.markdown(f'<div class="custom-result-box correct-box"><span class="result-title" style="color:#7d8dec;">🎉 정답입니다!</span><span class="result-sub">총 <b>{unique_count}개</b>의 고유 단어를 모두 찾아내셨군요!</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="custom-result-box wrong-box"><span class="result-title" style="color:#ff4b4b;">아쉬워요! 🧐</span><span class="result-sub">대시보드의 \'고유 단어\' 수치를 확인해 보세요.</span></div>', unsafe_allow_html=True)