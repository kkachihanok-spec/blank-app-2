import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 커스텀 CSS (글씨 크기 대폭 상향)
st.markdown("""
    <style>
    /* 배경 설정 */
    .stApp {
        background: radial-gradient(circle at top left, #121212, #191414) !important;
        color: #E0E0E0 !important;
    }
    
    /* 제목: 크기 키움 */
    .main-title {
        background: linear-gradient(to right, #1DB954, #1ED760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem !important; /* 3rem -> 4rem */
        font-weight: 900;
        text-align: left;
        margin-bottom: 0.1rem;
    }
    
    /* 서브 타이틀: 크기 키움 */
    .sub-text {
        text-align: left;
        color: #1DB954 !important; /* 색상을 좀 더 밝게 */
        font-size: 1.5rem !important; /* 1rem -> 1.5rem */
        font-weight: 600;
        margin-bottom: 3rem;
    }

    /* 가사 입력창 레이블 글씨 크기 */
    .stTextArea label p {
        font-size: 1.8rem !important; /* 레이블 크기 대폭 상향 */
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 10px;
    }

    /* 입력창 내부 글씨 크기 */
    .stTextArea textarea {
        background-color: #282828 !important;
        color: #FFFFFF !important;
        border-radius: 15px !important;
        font-size: 1.2rem !important; 
        line-height: 1.6 !important;
    }

    /* 버튼 크기 및 폰트 상향 */
    .stButton>button {
        width: auto !important;
        min-width: 200px;
        border-radius: 50px !important;
        background-color: #1DB954 !important;
        color: white !important;
        font-size: 1.3rem !important;
        font-weight: 800;
        height: 4rem;
        border: none;
        box-shadow: 0 4px 15px rgba(29, 185, 84, 0.2);
    }

    /* 섹션 헤더 크기 조정 */
    h3 {
        font-size: 2.2rem !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        margin-top: 20px !important;
    }

    /* 메트릭 글자 크기 */
    [data-testid="stMetricLabel"] p {
        font-size: 1.1rem !important;
        color: #B3B3B3 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 헤더 섹션 ---
st.markdown('<h1 class="main-title">K-POP INSIGHT</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)

# --- 입력 영역 ---
with st.container():
    # label 내용을 시각적으로 더 크게 강조
    lyrics_input = st.text_area("📝 분석할 가사를 입력해 주세요", height=250, 
                               placeholder="여기에 한국어 가사를 붙여넣으세요...", 
                               key="lyrics_main")
    
    col_btn, _ = st.columns([1, 3]) 
    with col_btn:
        analyze_btn = st.button("🚀 분석 시작하기")

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('데이터를 정밀 분석 중입니다...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 요약 대시보드
            st.write("")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("총 단어 수", f"{len(all_words)}")
            m2.metric("고유 단어", f"{len(df_counts)}")
            m3.metric("최다 빈도", df_counts.iloc[0]['단어'])
            m4.metric("핵심 품사", df_counts.iloc[0]['품사'])

            # 2. 메인 결과 섹션
            st.markdown("<br><hr>", unsafe_allow_html=True)
            c_l, c_r = st.columns([1, 1.2])
            with c_l:
                st.markdown("### 🌍 가사 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except:
                    st.error("번역 서버 응답 실패")

            with c_r:
                st.markdown("### 📊 단어 데이터")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("LINK", display_text="열기")}, hide_index=True)

            # 3. 빈도 분석 그래프
            st.markdown("<br><hr>", unsafe_allow_html=True)
            st.markdown("### 📈 키워드 등장 빈도")
            fig = px.bar(df_counts.head(10), x='단어', y='횟수', color='품사', 
                         template="plotly_dark", 
                         color_discrete_sequence=["#1DB954", "#9B59B6", "#3498DB"])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=15) # 그래프 글씨 크기도 조정
            )
            st.plotly_chart(fig, use_container_width=True)

            # 4. 문법 학습 가이드
            st.markdown("<br><hr>", unsafe_allow_html=True)
            st.markdown("### 📚 가사 활용 문법 가이드")
            p1, p2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "💎", "desc": "가사의 주제와 핵심 대상"},
                "동사": {"icon": "⚡", "desc": "움직임과 상황의 흐름"},
                "형용사": {"icon": "🎨", "desc": "감정과 상태의 묘사"},
                "부사": {"icon": "🎬", "desc": "수식과 디테일의 강조"}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = p1 if i < 2 else p2
                with target_col:
                    with st.expander(f"{info['icon']} {name} 심층 분석", expanded=True):
                        spec_df = df_counts[df_counts['품사'] == name]
                        if not spec_df.empty:
                            top_w = spec_df.iloc[0]['단어']
                            cnt = spec_df.iloc[0]['횟수']
                            st.markdown(f"""
                                <div style="border-left: 5px solid #1DB954; padding-left: 20px; margin: 15px 0;">
                                    <p style="color:#B3B3B3; font-size:1.1rem; margin-bottom:8px;">{info['desc']}</p>
                                    <h2 style="margin:0; color:white;">최빈 단어: <span style="color:#1DB954;">{top_w}</span></h2>
                                    <p style="font-size:1.3rem; margin-top:5px;">총 {cnt}회 등장</p>
                                    <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="color:#1DB954; text-decoration:none; font-size:1rem; font-weight:700;">사전에서 자세히 보기 →</a>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.caption("해당 품사 데이터 없음")
        else:
            st.warning("분석할 단어를 찾지 못했습니다.")