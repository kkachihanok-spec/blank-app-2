import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 세션 상태 초기화 ---
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

# 3. 커스텀 CSS (기존 스타일 유지 + 새로운 정답/오답 박스 디자인 추가)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    
    .main-product-title {
        font-family: 'Inter', sans-serif;
        font-size: 4rem !important; 
        font-weight: 900 !important;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #2a3f88 0%, #4a5fcc 50%, #7d8dec 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
        padding-top: 1rem;
    }
    
    .sub-text {
        color: #8b92b2 !important;
        font-size: 1.2rem !important; 
        font-weight: 600;
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

    .stButton>button {
        background-color: #2a3f88 !important;
        color: #FFFFFF !important;
        font-weight: 700;
        width: auto !important;
        min-width: 150px !important;
        height: 3.84rem !important;   
        font-size: 1.44rem !important; 
        border: none;
        margin-top: 20px !important;  
        display: flex !important;
        justify-content: flex-start !important; 
        padding-left: 30px !important;
        padding-right: 30px !important;
        align-items: center !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #4a5fcc !important;
        transform: translateY(-2px);
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
    
    .lyrics-line-pair {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(141, 146, 178, 0.1);
    }
    .lyrics-line-pair:last-child { border-bottom: none; }
    
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
    
    .data-row { 
        display: flex; 
        align-items: baseline; 
        border-top: 1px solid rgba(141, 146, 178, 0.2); 
        padding-top: 12px; 
        font-size: 1.1rem !important; 
    }
    .card-word { font-weight: 700 !important; color: #FFFFFF; } 
    .card-count { color: #4a5fcc; font-weight: 600; margin-left: 10px; } 

    /* 퀴즈 박스 세로폭 최소화 */
    .quiz-outer-box {
        background: rgba(45, 53, 72, 0.15);
        border: 1px solid rgba(74, 95, 204, 0.3);
        border-radius: 12px;
        padding: 12px 20px;
        margin-top: 5px;
        margin-bottom: 25px; 
    }
    
    div[data-testid="stRadio"] > div {
        gap: 0px !important;
        margin-top: -12px !important;
    }
    
    [data-testid="stWidgetLabel"] { display: none; }
    div[data-testid="stRadio"] label {
        color: white !important;
        font-size: 0.95rem !important;
        padding: 1px 0px !important;
    }

    /* --- 나만의 축하 메시지 스퀘어 박스 --- */
    .custom-result-box {
        padding: 20px;
        border-radius: 8px;
        border: 1px solid transparent;
        text-align: center;
        animation: fadeInUp 0.5s ease-out;
    }
    .correct-box {
        background: rgba(74, 95, 204, 0.1);
        border-color: #4a5fcc;
        box-shadow: 0 0 15px rgba(74, 95, 204, 0.3);
    }
    .wrong-box {
        background: rgba(255, 75, 75, 0.05);
        border-color: rgba(255, 75, 75, 0.4);
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .lyrics-card::-webkit-scrollbar { width: 6px; }
    .lyrics-card::-webkit-scrollbar-thumb { background: #2a3f88; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 헤더 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)
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
    st.markdown('<div class="result-header" style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

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
                line_html = f'<div class="lyrics-line-pair"><span class="kr-txt">{line}</span><span class="en-txt">{translated}</span></div>'
                html_output += line_html
            except:
                html_output += f'<div class="lyrics-line-pair"><span class="kr-txt">{line}</span></div>'
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
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="빈도수"))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 4. 문법 학습 섹션
    st.divider()
    st.markdown("### 📚 가사 속 문법 학습")
    pos_info = {"명사": {"icon": "💎", "desc": "사물이나 개념의 이름입니다."}, "동사": {"icon": "⚡", "desc": "동작이나 움직임을 나타냅니다."}, "형용사": {"icon": "🎨", "desc": "상태나 성질을 묘사합니다."}, "부사": {"icon": "🎬", "desc": "행동을 더 세밀하게 꾸며줍니다."}}
    p1, p2 = st.columns(2)
    for i, (name, info) in enumerate(pos_info.items()):
        target_col = p1 if i < 2 else p2
        with target_col:
            spec_df = df_counts[df_counts['품사'] == name]
            if not spec_df.empty:
                top_w, cnt = spec_df.iloc[0]['단어'], spec_df.iloc[0]['횟수']
                st.markdown(f'''<div class="analysis-card"><div class="pos-title">{info['icon']} {name}</div><div class="pos-desc">{info['desc']}</div><div class="data-row"><span style="color:#8b92b2; margin-right:10px;">주요 단어:</span><span class="card-word">{top_w}</span><span class="card-count">{cnt}회</span><a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="font-size:0.8rem; margin-left:auto; color:#7d8dec; text-decoration:none;">사전 보기 →</a></div></div>''', unsafe_allow_html=True)

    # 5. 퀴즈 박스 및 축하 메시지
    st.divider()
    st.markdown("### 📝 오늘의 가사 퀴즈")
    
    top_word, top_pos = df_counts.iloc[0]['단어'], df_counts.iloc[0]['품사']
    
    st.markdown(f"""
        <div class="quiz-outer-box">
            <div style="line-height: 1.2; margin-bottom: 4px;">
                <span style="color: #7d8dec; font-weight: 900; font-size: 1.2rem;">Q.</span> 
                <span style="color: white; font-size: 1.1rem; font-weight: 700;">
                    이 가사에서 가장 많이 사용된 단어는 '{top_word}'입니다. 이 단어의 품사는 무엇일까요?
                </span>
            </div>
    """, unsafe_allow_html=True)
    
    user_choice = st.radio(
        "정답 선택", ["명사", "동사", "형용사", "부사"], 
        index=None, key="quiz_snow_version", label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if user_choice:
        if user_choice == top_pos:
            st.snow() # 눈 내리는 효과
            st.markdown(f"""
                <div class="custom-result-box correct-box">
                    <span style="font-size: 1.5rem; font-weight: 800; color: #7d8dec;">🎉 정답입니다!</span><br>
                    <span style="color: white; font-size: 1.1rem;">'{top_word}'은(는) 완벽한 <b>{top_pos}</b>입니다.</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="custom-result-box wrong-box">
                    <span style="font-size: 1.3rem; font-weight: 700; color: #ff4b4b;">아쉬워요! 🧐</span><br>
                    <span style="color: #8b92b2; font-size: 1rem;">위쪽 분석 데이터를 다시 한 번 확인해 볼까요?</span>
                </div>
            """, unsafe_allow_html=True)