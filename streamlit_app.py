import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
import time

# 1. 페이지 설정 및 테마 최적화
st.set_page_config(page_title="K-Pop 가사 인사이트", layout="wide", page_icon="✨")

# 2. 커스텀 CSS (세련된 폰트와 카드 디자인)
st.markdown("""
    <style>
    /* 배경 및 기본 폰트 설정 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* 제목 스타일 */
    .main-title {
        font-family: 'Apple SD Gothic Neo', 'Nanum Gothic', sans-serif;
        color: #2D3436;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 섹션 박스 디자인 */
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* 분석 결과 박스 커스텀 */
    div[data-testid="stExpander"] {
        background-color: white !important;
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
    }
    
    /* 버튼 스타일 가다듬기 */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3.5rem;
        background: linear-gradient(90deg, #FF4B4B, #FF8E8E);
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 헤더 섹션 ---
st.markdown('<h1 class="main-title">🎵 K-Pop Lyric Insight</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#636E72; font-size:1.2rem;">가사 속에 담긴 감정과 문법을 인공지능으로 분석해보세요.</p>', unsafe_allow_html=True)
st.write("---")

# --- 입력 섹션 ---
with st.container():
    lyrics_input = st.text_area("📝 분석할 가사를 입력하세요", height=200, 
                               placeholder="예: 보고 싶다 이렇게 말하니까 더 보고 싶다...", 
                               key="lyrics_main")
    
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        analyze_btn = st.button("🚀 분석 시스템 가동")

# --- 분석 결과 영역 ---
if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('AI가 단어의 맥락을 분석 중입니다...'):
            # 실제 분석 로직
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 요약 대시보드 (Metric 카드)
            st.markdown("### 📊 가사 데이터 요약")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("총 단어", f"{len(all_words)}개")
            m_col2.metric("고유 단어", f"{len(df_counts)}종")
            m_col3.metric("최다 빈도 단어", df_counts.iloc[0]['단어'])
            m_col4.metric("주요 품사", df_counts.iloc[0]['품사'])

            # 2. 메인 분석 영역 (좌: 번역, 우: 리스트)
            st.write("")
            col_left, col_right = st.columns([1, 1.2])

            with col_left:
                st.markdown("#### 🌍 영문 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.success(translation.text)
                except:
                    st.error("번역 서버 연결에 실패했습니다.")

            with col_right:
                st.markdown("#### 📒 단어 라이브러리")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(
                    df_display,
                    column_config={"사전": st.column_config.LinkColumn("🔎 사전", display_text="보기")},
                    hide_index=True, use_container_width=True
                )

            # 3. 빈도수 시각화
            st.write("---")
            st.markdown("### 📈 단어 등장 빈도 분석")
            top_10 = df_counts.head(10)
            fig = px.bar(top_10, x='단어', y='횟수', color='품사', 
                         text='횟수', template="plotly_white",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(bordercolor="white", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # 4. 맞춤형 품사 학습 (고급 카드 디자인)
            st.write("---")
            st.markdown("### 📚 가사로 배우는 한국어 문법")
            
            p_col1, p_col2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "📌", "color": "#0984E3", "bg": "#E1F5FE", "desc": "사람, 사물 등의 이름"},
                "동사": {"icon": "🏃", "color": "#00B894", "bg": "#E8F5E9", "desc": "움직임과 행동"},
                "형용사": {"icon": "✨", "color": "#FDCB6E", "bg": "#FFF9C4", "desc": "상태와 느낌 묘사"},
                "부사": {"icon": "🎯", "color": "#6C5CE7", "bg": "#F3E5F5", "desc": "의미를 더해주는 양념"}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = p_col1 if i < 2 else p_col2
                with target_col:
                    with st.expander(f"{info['icon']} {name} 마스터 가이드", expanded=True):
                        st.markdown(f"""
                        <div style="background-color:{info['bg']}; padding:20px; border-radius:15px;">
                            <h4 style="color:{info['color']}; margin-top:0;">{info['desc']}</h4>
                            <p style="color:#2D3436; font-size:1rem;">이 노래에서 가장 많이 쓰인 <b>{name}</b>를 확인해 보세요.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        spec_df = df_counts[df_counts['품사'] == name]
                        if not spec_df.empty:
                            top_w = spec_df.iloc[0]['단어']
                            cnt = spec_df.iloc[0]['횟수']
                            st.info(f"✨ 대표 단어: **{top_word if 'top_word' in locals() else top_w}** ({cnt}회 사용됨)")
                            st.caption(f"[사전에서 '{top_w}' 검색하기](https://ko.dict.naver.com/#/search?query={top_w})")
                        else:
                            st.write("이 곡에는 분석된 해당 품사가 없습니다.")

        else:
            st.warning("분석할 수 있는 단어가 부족합니다. 가사를 더 길게 입력해 보세요.")
    else:
        st.error("가사를 입력해 주세요!")