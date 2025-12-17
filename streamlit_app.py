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

# 3. 커스텀 CSS (폰트 사이즈 통일 및 디자인 최적화)
st.markdown("""
    <style>
    /* 기본 배경 및 텍스트 설정 */
    .stApp {
        background: radial-gradient(circle at top left, #121212, #191414) !important;
        color: #E0E0E0 !important;
    }
    
    /* [메인 제목] 4rem */
    .main-product-title {
        font-family: 'Inter', sans-serif;
        font-size: 4rem !important; 
        font-weight: 900 !important;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #1DB954 0%, #1ED760 50%, #81EEA3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
        padding-top: 1rem;
    }
    
    /* [서브 타이틀] 1.2rem */
    .sub-text {
        color: #1DB954 !important;
        font-size: 1.2rem !important; 
        font-weight: 600;
        margin-bottom: 1.5rem !important; 
        opacity: 0.95;
    }

    /* 구분선 스타일 */
    hr {
        margin: 1.5rem 0 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* [가사 입력 레이블] - 1.7rem */
    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 15px !important;
        line-height: 1.4 !important;
    }

    .stTextArea textarea {
        background-color: #282828 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #404040 !important;
    }

    /* [분석 실행 버튼] 스퀘어 디자인 */
    .stButton {
        padding-top: 0.5rem !important;
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

    /* [수정] 분석 결과 제목: 가사 입력 레이블과 동일하게 1.7rem으로 설정 */
    .result-header {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-top: 0.5rem !important;
        margin-bottom: 20px !important;
        line-height: 1.4 !important;
    }

    /* 결과 메트릭 및 카드 스타일 */
    [data-testid="stMetricLabel"] p { font-size: 1.3rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
    [data-testid="stMetricValue"] { font-size: 2.0rem !important; font-weight: 400 !important; color: #1DB954 !important; }

    .analysis-card {
        border-left: 3px solid #1DB954;
        padding: 12px 18px;
        margin-bottom: 12px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 0 12px 12px 0;
    }
    .pos-title { font-size: 1rem; font-weight: 700; color: #1DB954; margin-bottom: 4px; }
    .pos-desc { font-size: 0.85rem; color: #B3B3B3; margin-bottom: 10px; line-height: 1.4; }
    .card-word { font-size: 1.2rem !important; font-weight: 400 !important; color: #FFFFFF; margin-right: 8px; }
    .card-count { font-size: 0.9rem; color: #1DB954; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- 헤더 섹션 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)

st.divider() # 서브 타이틀과 입력창 사이 줄

# --- 입력 섹션 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석 실행")

# --- 분석 로직 ---
if analyze_btn:
    if lyrics_input.strip():
        # 분석 버튼 아래 줄 긋기
        st.divider()
        
        # [수정] 분석 결과 메인 제목 (1.7rem 반영)
        st.markdown('<div class="result-header">📊 분석 결과</div>', unsafe_allow_html=True)

        with st.spinner('데이터 분석 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 요약 대시보드
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("전체 단어", f"{len(all_words)}")
            m2.metric("고유 단어", f"{len(df_counts)}")
            m3.metric("최빈 단어", df_counts.iloc[0]['단어'])
            m4.metric("주요 품사", df_counts.iloc[0]['품사'])

            # 2. 번역 및 상세 데이터
            st.divider()
            c_l, c_r = st.columns([1, 1.2])
            with c_l:
                st.markdown("### 🌍 가사 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except:
                    st.error("번역 서버 연결에 실패했습니다.")

            with c_r:
                st.markdown("### 📊 분석 데이터")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True)

            # 3. 문법 학습 섹션
            st.divider()
            st.markdown("### 📚 가사 속 문법 학습")
            p1, p2 = st.columns(2)
            
            pos_info = {
                "명사": {"icon": "💎", "desc": "사람, 사물, 장소 등의 이름을 나타내는 핵심 주제어입니다."},
                "동사": {"icon": "⚡", "desc": "주인공의 움직임이나 동작을 설명합니다."},
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
                                    <span class="card-count">{cnt}회 등장</span>
                                    <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="font-size:0.75rem; margin-left:8px; color:#1DB954; text-decoration:none;">사전 보기 →</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption(f"{info['icon']} {name} 데이터가 없습니다.")
        else:
            st.warning("분석할 수 있는 단어가 충분하지 않습니다.")
    else:
        st.error("가사를 입력해 주세요!")