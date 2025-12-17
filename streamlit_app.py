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

# 3. 커스텀 CSS
st.markdown("""
    <style>
    /* [배경 설정] 상단 다크네이비에서 하단 블랙으로 흐르는 세로 그라데이션 */
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* [메인 제목] */
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
        opacity: 0.95;
    }

    hr {
        margin: 1.5rem 0 !important;
        border-bottom: 1px solid #2d3548 !important;
    }

    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 15px !important;
    }

    .stTextArea textarea {
        background-color: rgba(20, 27, 45, 0.7) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #2d3548 !important;
    }

    .stButton>button {
        width: auto !important;
        min-width: 160px;
        border-radius: 4px !important;
        background-color: #2a3f88 !important;
        color: #FFFFFF !important;
        font-weight: 700;
        height: 3.2rem;
        border: none;
    }

    .result-header {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-top: 0.5rem !important;
        margin-bottom: 20px !important;
    }

    /* 문법 카드 디자인 */
    .analysis-card {
        border-left: 4px solid #2a3f88;
        padding: 16px 20px;
        margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        border: 1px solid rgba(45, 53, 72, 0.5);
    }
    
    /* [수정] 품사 제목 폰트 2포인트 상향 (기존 1.1rem -> 1.3rem) */
    .pos-title { 
        font-size: 1.3rem !important; 
        font-weight: 800 !important; 
        color: #7d8dec; 
        margin-bottom: 10px; 
    }
    
    /* 핵심 설명 폰트 (상향 유지) */
    .pos-desc { 
        font-size: 1.05rem !important; 
        color: #8b92b2; 
        margin-bottom: 14px; 
        line-height: 1.6; 
    }

    /* 데이터 영역 폰트 통일 */
    .data-row {
        display: flex; 
        align-items: baseline; 
        border-top: 1px solid rgba(141, 146, 178, 0.2); 
        padding-top: 12px;
        font-size: 1.1rem !important; 
    }
    .data-label { color: #8b92b2; margin-right: 10px; }
    .card-word { font-weight: 700 !important; color: #FFFFFF; }
    .card-count { color: #4a5fcc; font-weight: 600; margin-left: 10px; }
    
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
            
            pos_info = {
                "명사": {"icon": "💎", "desc": "사람, 사물, 장소나 추상적인 개념의 이름을 나타냅니다. 가사에서 주로 '누가', '무엇'에 해당하는 핵심 소재가 됩니다."},
                "동사": {"icon": "⚡", "desc": "주어의 동작이나 움직임을 나타냅니다. 가사 속 주인공이 현재 어떤 행동을 하고 있는지 생동감 있게 표현합니다."},
                "형용사": {"icon": "🎨", "desc": "사람이나 사물의 성질이나 상태를 나타냅니다. 가사의 감정선이나 분위기를 풍부하게 꾸며주는 역할을 합니다."},
                "부사": {"icon": "🎬", "desc": "용언이나 다른 부사를 꾸며주어 의미를 더 세밀하게 만듭니다. '어떻게' 수행되는지를 설명하는 양념 역할을 합니다."}
            }

            p1, p2 = st.columns(2)
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
                                <div class="data-row">
                                    <span class="data-label">가장 많이 사용된 단어:</span>
                                    <span class="card-word">{top_w}</span>
                                    <span class="card-count">{cnt}회</span>
                                    <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="font-size:0.8rem; margin-left:auto; color:#7d8dec; text-decoration:none;">사전 보기 →</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption(f"{info['icon']} {name} 데이터가 없습니다.")
        else:
            st.warning("분석 데이터 부족")
    else:
        st.error("가사를 입력하세요")