import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 커스텀 CSS (라벨은 강조, 데이터값은 보통 굵기로)
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #121212, #191414) !important;
        color: #E0E0E0 !important;
    }
    
    .main-title {
        background: linear-gradient(to right, #1DB954, #1ED760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 900;
        text-align: left;
    }
    
    h3 {
        font-size: 1.8rem !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
    }

    /* [요청사항] 메트릭 라벨은 굵게 */
    [data-testid="stMetricLabel"] p {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }
    
    /* [요청사항] 메트릭 실제 값(숫자, 단어)은 보통 굵기로 */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 400 !important; /* 900 -> 400 (보통 굵기) */
        color: #1DB954 !important;
    }

    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }

    /* 품사 카드 내 분석 단어 굵기 조정 */
    .card-word {
        font-size: 1.4rem !important;
        font-weight: 400 !important; /* 700 -> 400 (보통 굵기) */
        color: #FFFFFF;
        margin-right: 8px;
    }

    .analysis-card {
        border-left: 3px solid #1DB954;
        padding: 12px 18px;
        margin-bottom: 12px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 0 12px 12px 0;
    }

    .pos-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1DB954;
        margin-bottom: 4px;
    }

    .pos-desc {
        font-size: 0.85rem;
        color: #B3B3B3;
        margin-bottom: 10px;
    }

    .stButton>button {
        width: auto !important;
        min-width: 160px;
        border-radius: 50px !important;
        background-color: #1DB954 !important;
        color: white !important;
        font-weight: 700;
        height: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 헤더 ---
st.markdown('<h1 class="main-title">K-POP INSIGHT</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#1DB954; font-weight:600; margin-bottom:2rem;">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)

# --- 입력 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")
col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석 실행")

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
            st.write("")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("전체 단어", f"{len(all_words)}")
            m2.metric("고유 단어", f"{len(df_counts)}")
            m3.metric("최빈 단어", df_counts.iloc[0]['단어'])
            m4.metric("주요 품사", df_counts.iloc[0]['품사'])

            # 결과 섹션
            st.divider()
            c_l, c_r = st.columns([1, 1.2])
            with c_l:
                st.markdown("### 🌍 가사 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except: st.error("번역 실패")

            with c_r:
                st.markdown("### 📊 분석 데이터")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True)

            # 문법 가이드
            st.divider()
            st.markdown("### 📚 가사 속 문법 학습")
            p1, p2 = st.columns(2)
            
            pos_info = {
                "명사": {"icon": "💎", "desc": "사람, 사물, 장소 등의 이름을 나타내는 핵심 주제어입니다."},
                "동사": {"icon": "⚡", "desc": "주인공의 움직임이나 역동적인 동작을 설명합니다."},
                "형용사": {"icon": "🎨", "desc": "가사의 분위기와 감정 상태를 풍부하게 묘사합니다."},
                "부사": {"icon": "🎬", "desc": "의미를 세밀하게 꾸며주는 양념 같은 역할입니다."}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = p1 if i < 2 else p2
                with target_col:
                    spec_df = df_counts[df_counts['품사'] == name]
                    if not spec_df.empty:
                        top_w = spec_df.iloc[0]['단어']
                        cnt = spec_df.iloc[0]['횟수']
                        st.markdown(f"""
                            <div class="analysis-card">
                                <div class="pos-title">{info['icon']} {name}</div>
                                <div class="pos-desc">{info['desc']}</div>
                                <div style="display: flex; align-items: baseline;">
                                    <span class="card-word">{top_w}</span>
                                    <span style="font-size: 1rem; color: #1DB954;">{cnt}회 등장</span>
                                    <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="font-size:0.75rem; margin-left:8px; color:#1DB954; text-decoration:none;">사전 보기 →</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)