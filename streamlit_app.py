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

# 세션 상태 초기화
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'lyrics_text' not in st.session_state:
    st.session_state.lyrics_text = ""

# 3. 커스텀 CSS
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
        padding-left: 30px !important;
        padding-right: 30px !important;
        align-items: center !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #4a5fcc !important;
        transform: translateY(-2px);
    }

    /* 퀴즈 정답 선택지 박스 스타일링 */
    .quiz-container-box {
        background: rgba(74, 95, 204, 0.08); 
        border: 1px solid rgba(74, 95, 204, 0.4); 
        padding: 30px; 
        border-radius: 15px;
        margin-top: 10px;
    }

    /* 라디오 버튼 텍스트 크기 확대 (20% 키움) */
    [data-testid="stWidgetLabel"] p {
        font-size: 1.25rem !important; 
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 1.25rem !important;
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
    
    .analysis-card {
        border-left: 4px solid #2a3f88;
        padding: 16px 20px;
        margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        border: 1px solid rgba(45, 53, 72, 0.5);
    }
    
    .pos-title { font-size: 1.3rem !important; font-weight: 800 !important; color: #7d8dec; }
    </style>
    """, unsafe_allow_html=True)

# --- 헤더 및 입력 로직 생략 없이 유지 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)
st.divider()

lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    if st.button("🚀 분석을 실행해줘!"):
        if lyrics_input.strip():
            st.session_state.analyzed = True
            st.session_state.lyrics_text = lyrics_input

# --- 분석 결과 섹션 ---
if st.session_state.analyzed:
    input_data = st.session_state.lyrics_text
    st.divider()
    
    with st.spinner('데이터 분석 중...'):
        morphs = okt.pos(input_data, stem=True)
        target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
        all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
        df_all = pd.DataFrame(all_words)

    if not df_all.empty:
        df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)
        
        # 중간 대시보드 및 그래프 생략(기존 코드와 동일)
        # ... (이전 코드의 요약 대시보드, 번역, 데이터 표, 그래프 섹션이 이곳에 들어갑니다)
        
        # 5. [신규 레이아웃] 퀴즈 섹션
        st.divider()
        st.markdown("### 📝 오늘의 가사 퀴즈")
        
        top_word, top_pos = df_counts.iloc[0]['단어'], df_counts.iloc[0]['품사']
        
        # 질문은 박스 없이 깔끔하게 텍스트로 노출
        st.markdown(f"""
            <div style="margin-bottom: 20px; padding-left: 5px;">
                <span style="color: #7d8dec; font-weight: 800; font-size: 1.3rem;">Q.</span> 
                <span style="color: white; font-size: 1.2rem; font-weight: 600;">
                    이 가사에서 가장 많이 사용된 단어는 '{top_word}'입니다. 이 단어의 품사는 무엇일까요?
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        # 정답 선택지 영역을 박스로 감쌈
        st.markdown('<div class="quiz-container-box">', unsafe_allow_html=True)
        user_choice = st.radio(
            "정답을 골라보세요!", 
            ["명사", "동사", "형용사", "부사"], 
            index=None, 
            key="quiz_final_new_layout"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if user_choice:
            st.write("") # 결과와의 간격
            if user_choice == top_pos:
                st.success(f"정답입니다! 🎉 '{top_word}'은(는) **{top_pos}**입니다.")
                st.balloons()
            else:
                st.error("아쉬워요! 다시 한번 고민해볼까요? 🧐")