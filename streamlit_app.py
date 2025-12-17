import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# 3. 커스텀 CSS (배경 그라데이션 및 컬러 팔레트 적용)
st.markdown("""
    <style>
    /* [배경 설정] 상단 다크네이비에서 하단 블랙으로 흐르는 세로 그라데이션 */
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* [메인 제목] 블루 퍼플 그라데이션 */
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
    
    /* [서브 타이틀] 그레이 텍스트 (#8b92b2) */
    .sub-text {
        color: #8b92b2 !important;
        font-size: 1.2rem !important; 
        font-weight: 600;
        margin-bottom: 1.5rem !important; 
        opacity: 0.95;
    }

    /* 구분선 스타일 (#2d3548) */
    hr {
        margin: 1.5rem 0 !important;
        border-bottom: 1px solid #2d3548 !important;
    }

    /* [가사 입력 레이블] */
    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 15px !important;
        line-height: 1.4 !important;
    }

    /* 입력창 배경 (배경과 조화를 위해 투명도 살짝 부여) */
    .stTextArea textarea {
        background-color: rgba(20, 27, 45, 0.7) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #2d3548 !important;
    }

    /* [분석 실행 버튼] 블루 퍼플 강조색 */
    .stButton>button {
        width: auto !important;
        min-width: 160px;
        border-radius: 4px !important;
        background-color: #2a3f88 !important;
        color: #FFFFFF !important;
        font-weight: 700;
        height: 3.2rem;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #3b52a8 !important;
        box-shadow: 0 0 15px rgba(42, 63, 136, 0.4);
    }

    /* 분석 결과 제목 (1.7rem) */
    .result-header {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-top: 0.5rem !important;
        margin-bottom: 20px !important;
        line-height: 1.4 !important;
    }

    /* 메트릭 스타일 */
    [data-testid="stMetricLabel"] p { color: #8b92b2 !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] { color: #4a5fcc !important; font-weight: 700 !important; }

    /* 문법 카드 스타일 */
    .analysis-card {
        border-left: 3px solid #2a3f88;
        padding: 12px 18px;
        margin-bottom: 12px;
        background: rgba(45, 53, 72, 0.3);
        border-radius: 0 12px 12px 0;
        border-top: 1px solid #2d3548;
        border-right: 1px solid #2d3548;
        border-bottom: 1px solid #2d3548;
    }
    .pos-title { font-size: 1rem; font-weight: 700; color: #7d8dec; margin-bottom: 4px; }
    .pos-desc { font-size: 0.85rem; color: #8b92b2; margin-bottom: 10px; }
    .card-word { font-size: 1.2rem !important; font-weight: 500 !important; color: #FFFFFF; }
    .card-count { font-size: 0.9rem; color: #4a5fcc; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- 헤더 섹션 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)

st.divider()

# --- 입력 섹션 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석 실행")

# --- 분석 로직 ---
if analyze_btn:
    if lyrics_input.strip():
        st.divider()
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

            # 2. 번역 및 데이터
            st.divider()
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

            # 3. 문법 학습 섹션
            st.divider()
            st.markdown("### 📚 가사 속 문법 학습")
            p1, p2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "💎", "desc": "핵심 주제어"},
                "동사": {"icon": "⚡", "desc": "동작 및 움직임"},
                "형용사": {"icon": "🎨", "desc": "감정 및 상태 묘사"},
                "부사": {"icon": "🎬", "desc": "의미 보정 및 수식"}
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
                                    <span class="card-count" style="margin-left:10px;">{cnt}회</span>
                                    <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="font-size:0.75rem; margin-left:12px; color:#7d8dec; text-decoration:none;">Search →</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("분석 데이터 부족")
    else:
        st.error("가사를 입력하세요")