import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
import time

# 1. 페이지 설정
st.set_page_config(page_title="K-Pop 가사 인사이트", layout="wide", page_icon="✨")

# 2. 커스텀 CSS (다크/라이트 모드 대응 및 가시성 확보)
st.markdown("""
    <style>
    /* 전체 배경색과 기본 글자색 제어 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 제목 및 텍스트 스타일 */
    .main-title {
        color: #2D3436 !important;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* 카드(Expander) 내부 스타일 강제 고정 */
    .st-expanderContent, .st-expanderHeader {
        background-color: #ffffff !important;
        color: #2D3436 !important;
    }

    /* 강조 박스 디자인 */
    .custom-card {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #FF4B4B;
        color: #2D3436 !important; /* 글자색 검정 고정 */
    }
    
    .custom-card b, .custom-card p, .custom-card h4 {
        color: #2D3436 !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        border-radius: 20px;
        background: linear-gradient(90deg, #FF4B4B, #FF7878);
        color: white !important;
        font-weight: bold;
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
st.markdown('<h1 class="main-title">🎵 K-Pop 가사 분석기</h1>', unsafe_allow_html=True)
st.write("---")

# --- 입력 ---
lyrics_input = st.text_area("📝 분석할 가사를 입력하세요", height=200, placeholder="가사를 여기에 붙여넣으세요...", key="lyrics_main")
analyze_btn = st.button("🚀 분석 시작")

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('AI가 단어를 분석 중입니다...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 메트릭 요약
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("총 단어", f"{len(all_words)}개")
            m2.metric("고유 단어", f"{len(df_counts)}종")
            m3.metric("인기 단어", df_counts.iloc[0]['단어'])
            m4.metric("핵심 품사", df_counts.iloc[0]['품사'])

            # 2. 번역 및 리스트
            st.write("---")
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("### 🌍 영문 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except:
                    st.error("번역 서버 오류")

            with col_r:
                st.markdown("### 📒 단어 목록")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="보기")}, hide_index=True)

            # 3. 그래프 (에러 수정됨)
            st.write("---")
            st.markdown("### 📈 빈도 분석")
            top_10 = df_counts.head(10)
            fig = px.bar(top_10, x='단어', y='횟수', color='품사', template="plotly_white")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)') # 문제되었던 bordercolor 삭제
            st.plotly_chart(fig, use_container_width=True)

            # 4. 품사 학습 가이드 (가시성 고정)
            st.write("---")
            st.markdown("### 📚 가사로 배우는 문법")
            
            p_col1, p_col2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "📌", "bg": "#E1F5FE", "desc": "이름을 나타내는 말"},
                "동사": {"icon": "🏃", "bg": "#E8F5E9", "desc": "동작을 나타내는 말"},
                "형용사": {"icon": "✨", "bg": "#FFF9C4", "desc": "상태를 나타내는 말"},
                "부사": {"icon": "🎯", "bg": "#F3E5F5", "desc": "자세히 꾸며주는 말"}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = p_col1 if i < 2 else p_col2
                with target_col:
                    with st.expander(f"{info['icon']} {name} 가이드", expanded=True):
                        spec_df = df_counts[df_counts['품사'] == name]
                        top_w = spec_df.iloc[0]['단어'] if not spec_df.empty else "없음"
                        cnt = spec_df.iloc[0]['횟수'] if not spec_df.empty else 0
                        
                        st.markdown(f"""
                            <div class="custom-card" style="background-color: {info['bg']};">
                                <h4 style="margin:0;">{info['desc']}</h4>
                                <p style="margin:10px 0;">이 노래의 대표 단어: <b>{top_w}</b> ({cnt}회)</p>
                                <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="color: #555; text-decoration: none; font-size: 0.8rem;">사전 보기 →</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("분석할 단어가 없습니다.")
    else:
        st.error("가사를 입력해 주세요.")