import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
import time

# 1. 페이지 설정
st.set_page_config(page_title="K-Pop 가사 인사이트", layout="wide", page_icon="🎧")

# 2. 고급 다크 UI CSS (글로시한 카드 디자인)
st.markdown("""
    <style>
    /* 배경 및 기본 글꼴 */
    .stApp {
        background: radial-gradient(circle at top left, #121212, #191414) !important;
        color: #E0E0E0 !important;
    }
    
    /* 제목: 네온 효과 */
    .main-title {
        background: linear-gradient(to right, #1DB954, #1ED760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }
    
    /* 서브 텍스트 */
    .sub-text {
        text-align: center;
        color: #B3B3B3 !important;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
    }

    /* 카드형 섹션 (Glassmorphism 효과) */
    div[data-testid="stExpander"], .custom-card {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 20px;
        backdrop-filter: blur(10px);
    }

    /* 메트릭 박스 */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stMetricValue"] {
        color: #1DB954 !important;
        font-size: 2rem !important;
    }

    /* 입력창 디자인 */
    .stTextArea textarea {
        background-color: #282828 !important;
        color: #FFFFFF !important;
        border-radius: 15px !important;
        border: 1px solid #404040 !important;
        font-size: 1.1rem !important;
    }

    /* 버튼 스타일 (Spotify 그린) */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        background-color: #1DB954 !important;
        color: white !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        height: 3.5rem;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        background-color: #1ED760 !important;
        box-shadow: 0 0 20px rgba(29, 185, 84, 0.4);
    }

    /* 링크 스타일 */
    a { color: #1DB954 !important; text-decoration: none !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 헤더 섹션 ---
st.markdown('<h1 class="main-title">K-POP INSIGHT</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 시각화 및 맞춤형 문법 분석 엔진</p>', unsafe_allow_html=True)

# --- 입력 영역 ---
with st.container():
    lyrics_input = st.text_area("", height=200, placeholder="가사를 이곳에 입력하면 분석이 시작됩니다...", key="lyrics_main")
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b2:
        analyze_btn = st.button("분석 실행하기")

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('데이터 엔진 가동 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 메트릭 요약 (상단 대시보드)
            st.write("")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("TOTAL WORDS", f"{len(all_words)}")
            m2.metric("UNIQUE", f"{len(df_counts)}")
            m3.metric("TOP WORD", df_counts.iloc[0]['단어'])
            m4.metric("PRIMARY POS", df_counts.iloc[0]['품사'])

            # 2. 메인 분석 (번역 & 리스트)
            st.write("---")
            c_l, c_r = st.columns([1, 1.2])
            with c_l:
                st.markdown("### 🌍 가사 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except:
                    st.error("번역 서버 응답 실패")

            with c_r:
                st.markdown("### 📊 단어 라이브러리")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("LINK", display_text="OPEN")}, hide_index=True)

            # 3. 그래프 (그린 & 퍼플 테마)
            st.write("---")
            st.markdown("### 📈 키워드 빈도 분석")
            fig = px.bar(df_counts.head(10), x='단어', y='횟수', color='품사', 
                         template="plotly_dark", 
                         color_discrete_sequence=["#1DB954", "#9B59B6", "#3498DB", "#E74C3C"])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#B3B3B3"))
            st.plotly_chart(fig, use_container_width=True)

            # 4. 문법 카드 (Glassmorphism 카드형 디자인)
            st.write("---")
            st.markdown("### 📚 문법 학습 가이드")
            p1, p2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "💎", "desc": "주제와 대상을 나타내는 핵심 단어"},
                "동사": {"icon": "⚡", "desc": "역동적인 행동과 흐름을 설명"},
                "형용사": {"icon": "🎨", "desc": "가사의 색채와 감정을 묘사"},
                "부사": {"icon": "🎬", "desc": "상황의 디테일을 더해주는 수식"}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = p1 if i < 2 else p2
                with target_col:
                    with st.expander(f"{info['icon']} {name} 분석", expanded=True):
                        spec_df = df_counts[df_counts['품사'] == name]
                        if not spec_df.empty:
                            top_w = spec_df.iloc[0]['단어']
                            cnt = spec_df.iloc[0]['횟수']
                            st.markdown(f"""
                                <div style="border-left: 4px solid #1DB954; padding-left: 15px; margin: 10px 0;">
                                    <p style="color:#B3B3B3; font-size:0.9rem; margin-bottom:5px;">{info['desc']}</p>
                                    <h4 style="margin:0; color:white;">최다 등장: <span style="color:#1DB954;">{top_w}</span> ({cnt}회)</h4>
                                    <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank">단어 상세보기 →</a>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.caption("해당 품사 데이터 없음")
        else:
            st.warning("분석할 단어가 없습니다.")