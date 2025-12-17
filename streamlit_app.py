import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
import time

# 1. 페이지 설정
st.set_page_config(page_title="K-Pop Lyric Insight", layout="wide", page_icon="✨")

# 2. 커스텀 CSS 적용 (고급스러운 UI 디자인)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #1E1E1E;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    /* 카드 디자인 */
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-radius: 15px !important;
        background-color: white !important;
        margin-bottom: 1rem;
    }
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF3333;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 상단 헤더 ---
st.markdown('<h1 class="main-title">🎵 K-Pop Lyric Insight</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">가사를 분석하여 단어의 의미와 한국어 문법을 한눈에 파악하세요.</p>', unsafe_allow_html=True)

# --- 입력 섹션 ---
lyrics_input = st.text_area("✍️ 가사를 여기에 입력해 주세요", height=200, 
                           placeholder="분석하고 싶은 한국어 가사를 붙여넣으세요...", 
                           key="lyrics_main")
analyze_btn = st.button("🚀 분석 시작하기")

# --- 분석 결과 영역 ---
if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('가사를 꼼꼼하게 분석하고 있습니다...'):
            time.sleep(1) # 시각적 효과를 위한 짧은 대기
            
            # 분석 데이터 준비
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            
            # 한 글자 단어도 포함
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 요약 대시보드
            st.divider()
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("총 추출 단어", f"{len(all_words)}개")
            m_col2.metric("고유 단어 종류", f"{len(df_counts)}개")
            m_col3.metric("가장 많이 나온 품사", df_counts.iloc[0]['품사'])
            m_col4.metric("최다 빈도 단어", df_counts.iloc[0]['단어'])

            # 2. 번역 및 리스트
            st.divider()
            c1, c2 = st.columns([1, 1.2])

            with c1:
                st.markdown("### 🌍 English Translation")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except:
                    st.error("번역 서버 연결에 실패했습니다.")

            with c2:
                st.markdown("### 📊 Vocabulary List")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(
                    df_display,
                    column_config={"사전": st.column_config.LinkColumn("링크", display_text="사전 보기")},
                    hide_index=True, use_container_width=True, key="data_editor_v2"
                )

            # 3. 빈도수 그래프
            st.divider()
            st.markdown("### 📈 Keyword Frequency Top 10")
            fig = px.bar(df_counts.head(10), x='단어', y='횟수', color='품사', 
                         template="plotly_white", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

            # 4. 품사 학습 가이드 (가사 기반 예시 자동 추출)
            st.divider()
            st.markdown("### 📚 Grammer Guide (Customized)")
            
            p_col1, p_col2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "📌", "c": "#E3F2FD", "desc": "사물/사람의 이름입니다.", "role": "문장의 핵심 주제가 됩니다."},
                "동사": {"icon": "🏃", "c": "#E8F5E9", "desc": "동작이나 움직임을 말합니다.", "role": "상황의 행동을 설명합니다."},
                "형용사": {"icon": "✨", "c": "#FFF3E0", "desc": "상태나 느낌을 묘사합니다.", "role": "분위기와 감정을 풍부하게 합니다."},
                "부사": {"icon": "🎯", "c": "#F3E5F5", "desc": "다른 말을 꾸며주는 역할을 합니다.", "role": "감정의 정도를 강조합니다."}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = p_col1 if i < 2 else p_col2
                with target_col:
                    with st.expander(f"{info['icon']} {name} 설명 보기", expanded=True):
                        st.markdown(f"**개념:** {info['desc']}")
                        st.markdown(f"**가사 속 역할:** {info['role']}")
                        
                        # 해당 품사의 최빈 단어 찾기
                        spec_df = df_counts[df_counts['품사'] == name]
                        if not spec_df.empty:
                            top_w = spec_df.iloc[0]['단어']
                            cnt = spec_df.iloc[0]['횟수']
                            st.success(f"✅ 대표 단어: **'{top_w}'** (총 {cnt}회)")
                            st.caption(f"[👉 '{top_w}' 사전 뜻 풀이 보기](https://ko.dict.naver.com/#/search?query={top_w})")
                        else:
                            st.warning(f"ℹ️ 이 가사에는 '{name}' 품사가 없습니다.")
        else:
            st.warning("분석할 단어가 충분하지 않습니다. 가사를 더 길게 입력해 보세요.")
    else:
        st.error("가사를 먼저 입력해 주세요!")