import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 리소스 로드 (캐싱 적용)
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# 3. 커스텀 CSS (제목 크기 20% 축소 반영)
st.markdown("""
    <style>
    /* 기본 배경 및 텍스트 설정 */
    .stApp {
        background: radial-gradient(circle at top left, #121212, #191414) !important;
        color: #E0E0E0 !important;
    }
    
    /* [수정] 메인 제목: 기존 5rem에서 4rem으로 20% 축소 */
    .main-product-title {
        font-family: 'Inter', sans-serif;
        font-size: 4rem !important; 
        font-weight: 900 !important;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #1DB954 0%, #1ED760 50%, #81EEA3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem !important;
        line-height: 1.1;
    }
    
    /* [수정] 서브 타이틀: 기존 1.5rem에서 1.2rem으로 20% 축소 */
    .sub-text {
        color: #1DB954 !important;
        font-size: 1.2rem !important; 
        font-weight: 600;
        margin-bottom: 2.5rem;
        opacity: 0.95;
    }

    /* [기존 유지] 가사 입력 레이블 및 여백 */
    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 35px !important;
    }

    .stTextArea textarea {
        background-color: #282828 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #404040 !important;
    }

    /* [기존 유지] 스퀘어 버튼 스타일 */
    .stButton {
        margin-top: -10px !important;
    }
    
    .stButton>button {
        width: auto !important;
        min-width: 160px;
        border-radius: 4px !important;
        background-color: #1DB954 !important;
        color: white !important;
        font-weight: 700;
        height: 3.2rem;
        border: none;
    }

    /* 메트릭 및 카드 스타일 유지 */
    [data-testid="stMetricLabel"] p {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.0rem !important;
        font-weight: 400 !important;
        color: #1DB954 !important;
    }

    .analysis-card {
        border-left: 3px solid #1DB954;
        padding: 12px 18px;
        margin-bottom: 12px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 0 12px 12px 0;
    }

    .card-word {
        font-size: 1.2rem !important;
        font-weight: 400 !important;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 헤더 섹션 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)

# --- 입력 섹션 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

st.write("") 

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석 실행")

st.write("") 

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

            # 요약 대시보드
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("전체 단어", f"{len(all_words)}")
            m2.metric("고유 단어", f"{len(df_counts)}")
            m3.metric("최빈 단어", df_counts.iloc[0]['단어'])
            m4.metric("주요 품사", df_counts.iloc[0]['품사'])

            st.divider()
            
            # 번역 및 데이터 표시
            c_l, c_r = st.columns([1, 1.2])
            with c_l:
                st.markdown("### 🌍 가사 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except:
                    st.error("번역 실패")

            with c_r:
                st.markdown("### 📊 분석 데이터")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True)

            # 문법 학습 섹션
            st.divider()
            st.markdown("### 📚 가사 속 문법 학습")
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
                                <div class="pos-title">{icon} {name}</div>
                                <div style="display: flex; align-items: baseline;">
                                    <span class="card-word">{top_w}</span>
                                    <span style="font-size: 0.9rem; color: #1DB954; margin-left:8px;">{cnt}회 등장</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("분석할 단어가 없습니다.")