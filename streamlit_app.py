import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 커스텀 CSS (텍스트 크기는 유지하되 레이아웃은 간결하게)
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

    /* 분석 결과 카드 스타일 (간결화) */
    .analysis-card {
        border-left: 4px solid #1DB954;
        padding: 12px 18px;
        margin: 8px 0;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0 10px 10px 0;
    }

    .card-word {
        font-size: 1.6rem !important;
        font-weight: 800;
        color: #1DB954;
        margin-right: 10px;
    }

    .card-count {
        font-size: 1.1rem;
        color: #B3B3B3;
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
lyrics_input = st.text_area("📝 가사 입력", height=200, placeholder="가사를 붙여넣으세요...", key="lyrics_main")
col_btn, _ = st.columns([1, 3]) 
with col_btn:
    analyze_btn = st.button("🚀 분석 실행")

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('분석 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 요약 메트릭
            st.write("")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("총 단어", f"{len(all_words)}")
            m2.metric("고유 단어", f"{len(df_counts)}")
            m3.metric("최빈 단어", df_counts.iloc[0]['단어'])
            m4.metric("주요 품사", df_counts.iloc[0]['품사'])

            # 결과 섹션
            st.divider()
            c_l, c_r = st.columns([1, 1.2])
            with c_l:
                st.markdown("### 🌍 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except: st.error("번역 실패")

            with c_r:
                st.markdown("### 📊 단어 데이터")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True)

            # 문법 가이드 (이 부분이 요청하신 대로 요약된 부분입니다)
            st.divider()
            st.markdown("### 📚 핵심 문법 요약")
            p1, p2 = st.columns(2)
            pos_info = {"명사": "💎", "동사": "⚡", "형용사": "🎨", "부사": "🎬"}

            for i, (name, icon) in enumerate(pos_info.items()):
                target_col = p1 if i < 2 else p2
                with target_col:
                    spec_df = df_counts[df_counts['품사'] == name]
                    if not spec_df.empty:
                        top_w = spec_df.iloc[0]['단어']
                        cnt = spec_df.iloc[0]['횟수']
                        st.markdown(f"""
                            <div class="analysis-card">
                                <span style="color:#B3B3B3; font-size:0.9rem;">{icon} {name}</span><br>
                                <span class="card-word">{top_w}</span>
                                <span class="card-count">({cnt}회)</span>
                                <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="margin-left:10px; font-size:0.8rem;">[사전]</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption(f"{icon} {name} 데이터 없음")
        else:
            st.warning("분석할 단어가 없습니다.")