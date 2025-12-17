import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 커스텀 CSS
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
        font-size: 3.5rem !important;
        font-weight: 900;
        text-align: left;
    }
    
    .sub-text {
        text-align: left;
        color: #1DB954 !important;
        font-size: 1.2rem !important;
        font-weight: 600;
        margin-bottom: 2rem;
    }

    /* 가사 입력창 레이블 */
    .stTextArea label p {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }

    /* 품사 카드 디자인 */
    .analysis-card {
        border-left: 4px solid #1DB954;
        padding: 15px 20px;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0 15px 15px 0;
    }

    .pos-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1DB954;
        margin-bottom: 5px;
    }

    .pos-desc {
        font-size: 0.9rem;
        color: #B3B3B3;
        margin-bottom: 12px;
        line-height: 1.4;
    }

    .result-line {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }

    .card-word {
        font-size: 1.8rem !important;
        font-weight: 800;
        color: #FFFFFF;
    }

    .card-count {
        font-size: 1.1rem;
        color: #1DB954;
        font-weight: 600;
    }

    .stButton>button {
        width: auto !important;
        min-width: 180px;
        border-radius: 50px !important;
        background-color: #1DB954 !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 800;
        height: 3.5rem;
        border: none;
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
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)

# --- 입력 ---
lyrics_input = st.text_area("📝 가사 입력", height=200, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")
col_btn, _ = st.columns([1, 3]) 
with col_btn:
    analyze_btn = st.button("🚀 분석 실행")

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('AI 분석 중...'):
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
                except: st.error("번역 서버 오류")

            with c_r:
                st.markdown("### 📊 분석 데이터")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True)

            # 문법 가이드 (설명 유지 + 요약 레이아웃)
            st.divider()
            st.markdown("### 📚 가사 속 문법 학습")
            p1, p2 = st.columns(2)
            
            pos_info = {
                "명사": {"icon": "💎", "desc": "사람, 사물, 장소 등의 이름을 나타내는 단어입니다. 가사의 핵심 주제가 됩니다."},
                "동사": {"icon": "⚡", "desc": "움직임이나 동작을 나타내는 단어입니다. 주인공의 행동을 설명합니다."},
                "형용사": {"icon": "🎨", "desc": "성질이나 상태를 묘사하는 단어입니다. 가사의 분위기를 풍부하게 만듭니다."},
                "부사": {"icon": "🎬", "desc": "다른 말을 꾸며주는 양념 역할입니다. 감정의 정도를 세밀하게 표현합니다."}
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
                                <div class="pos-title">{info['icon']} {name} (Part of Speech)</div>
                                <div class="pos-desc">{info['desc']}</div>
                                <div class="result-line">
                                    <span class="card-word">{top_w}</span>
                                    <span class="card-count">{cnt}회 등장</span>
                                    <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="font-size:0.8rem; margin-left:5px;">사전 보기 →</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption(f"{info['icon']} {name} 데이터가 없습니다.")
        else:
            st.warning("분석할 단어가 없습니다.")