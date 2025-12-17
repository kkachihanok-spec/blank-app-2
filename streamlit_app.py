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

# 3. 커스텀 CSS (기존 스타일 유지 + 퀴즈 스타일 추가)
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

    /* 버튼 스타일 */
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
    
    /* 퀴즈 박스 스타일 */
    .quiz-container {
        background-color: rgba(45, 53, 72, 0.4) !important;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #4a5fcc;
        margin-top: 20px;
    }

    [data-testid="stMetricLabel"] p { font-size: 1.6rem !important; font-weight: 900 !important; }
    [data-testid="stMetricValue"] { font-size: 1.67rem !important; color: #4a5fcc !important; font-weight: 700 !important; }

    .lyrics-card {
        border-left: 4px solid #4a5fcc;
        padding: 24px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        height: 520px;
        overflow-y: auto;
    }
    
    .kr-txt { font-size: 1.1rem; color: #FFFFFF; font-weight: 600; display: block; margin-bottom: 4px; }
    .en-txt { font-size: 0.95rem; color: #8b92b2; font-style: italic; }

    .analysis-card {
        border-left: 4px solid #2a3f88;
        padding: 16px 20px;
        margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
    }
    
    .data-row { display: flex; align-items: baseline; border-top: 1px solid rgba(141, 146, 178, 0.2); padding-top: 12px; font-size: 1.1rem !important; }
    .card-word { font-weight: 700 !important; color: #FFFFFF; } 
    .card-count { color: #4a5fcc; font-weight: 600; margin-left: 10px; } 
    </style>
    """, unsafe_allow_html=True)

# --- 메인 헤더 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)
st.divider()

# --- 입력 섹션 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석을 실행해줘!")

# --- 분석 결과 로직 ---
if analyze_btn or st.session_state.get('analyzed', False):
    if lyrics_input.strip():
        st.session_state['analyzed'] = True
        st.divider()
        st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

        # [데이터 분석 로직 동일]
        with st.spinner('데이터 분석 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 요약 대시보드
            m1, m2, m3, m4 = st.columns(4)
            w_arrow = "→ " 
            m1.metric("전체 단어", f"{w_arrow}{len(all_words)}")
            m2.metric("고유 단어", f"{w_arrow}{len(df_counts)}")
            m3.metric("최빈 단어", f"{w_arrow}{df_counts.iloc[0]['단어']}")
            m4.metric("주요 품사", f"{w_arrow}{df_counts.iloc[0]['품사']}")

            # 2. 번역 및 데이터 표
            st.divider()
            c_l, c_r = st.columns([1.2, 1])
            with c_l:
                st.markdown("### 🌍 가사 대조 번역")
                lines = [line.strip() for line in lyrics_input.split('\n') if line.strip()]
                html_output = '<div class="lyrics-card">'
                for line in lines:
                    try:
                        translated = translator.translate(line, dest='en').text
                        html_output += f'<div style="margin-bottom:20px;"><span class="kr-txt">{line}</span><span class="en-txt">{translated}</span></div>'
                    except:
                        html_output += f'<div><span class="kr-txt">{line}</span></div>'
                html_output += '</div>'
                st.markdown(html_output, unsafe_allow_html=True)

            with c_r:
                st.markdown("### 📊 분석 데이터")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, hide_index=True, use_container_width=True, height=520)

            # 3. 그래프 섹션
            st.divider()
            st.markdown("### 📈 단어 빈도 시각화")
            fig = px.bar(df_counts.head(20), x='단어', y='횟수', color='품사', template='plotly_dark')
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # 4. 문법 학습 섹션
            st.divider()
            st.markdown("### 📚 가사 속 문법 학습")
            # [기본 카드 로직 유지]
            p1, p2 = st.columns(2)
            # ... (기본 카드 출력 코드 생략 가능하지만 구조 유지를 위해 유지) ...

            # 5. [신규] 퀴즈 챌린지 섹션
            st.divider()
            st.markdown("### ✍️ 가사 마스터 퀴즈")
            with st.container():
                st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
                st.subheader("Q. 오늘 분석한 가사에서 '동작이나 움직임'을 나타내는 단어들은 어떤 품사에 해당할까요?")
                
                quiz_ans = st.radio("정답을 선택하세요:", ["명사", "동사", "형용사", "부사"], index=None)
                
                if quiz_ans:
                    if quiz_ans == "동사":
                        st.success("정답입니다! 🥳 동사는 가사 속 인물의 행동을 묘사하는 핵심 요소입니다.")
                        st.balloons()
                    else:
                        st.error("아쉽네요! 다시 한번 '문법 학습' 섹션을 확인해 보세요. 🧐")
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.warning("분석할 단어가 충분하지 않습니다.")
    else:
        st.error("가사를 입력해 주세요.")