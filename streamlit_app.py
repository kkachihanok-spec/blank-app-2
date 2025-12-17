import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
import time

# 1. 페이지 설정
st.set_page_config(page_title="K-Pop 가사 인사이트", layout="wide", page_icon="🌙")

# 2. 커스텀 CSS (배경 블랙 및 글자 화이트 고정)
st.markdown("""
    <style>
    /* 전체 배경을 블랙으로 고정 */
    .stApp {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }
    
    /* 제목 스타일 */
    .main-title {
        color: #FF4B4B !important;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* 서브 타이틀 */
    .sub-text {
        color: #B2BEC3 !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 입력창 및 에디터 스타일 조정 */
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: white !important;
        border: 1px solid #333 !important;
    }

    /* 카드(Expander) 디자인 - 배경 어둡게, 테두리 강조 */
    div[data-testid="stExpander"] {
        background-color: #1E1E1E !important;
        border: 1px solid #333 !important;
        border-radius: 15px !important;
        color: white !important;
    }

    /* 박스 내부의 텍스트 색상 강제 고정 */
    .custom-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 5px solid #FF4B4B;
        background-color: #262730 !important;
    }
    
    .custom-card h4, .custom-card p, .custom-card b {
        color: #FFFFFF !important;
    }

    .custom-card a {
        color: #00D1FF !important;
        text-decoration: none;
    }

    /* 메트릭 박스 글자색 */
    [data-testid="stMetricValue"] {
        color: #FF4B4B !important;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #FF4B4B, #FF7878);
        color: white !important;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 헤더 ---
st.markdown('<h1 class="main-title">🌙 K-Pop 가사 분석기</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">어두운 밤에도 선명하게 가사를 분석해보세요.</p>', unsafe_allow_html=True)

# --- 입력 섹션 ---
lyrics_input = st.text_area("📝 분석할 가사를 입력하세요", height=200, placeholder="가사를 여기에 붙여넣으세요...", key="lyrics_main")
analyze_btn = st.button("🚀 분석 시작")

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('가사 데이터를 읽어오는 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)

        if not df_all.empty:
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

            # 1. 요약 메트릭
            st.write("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("총 추출 단어", f"{len(all_words)}개")
            m2.metric("단어 종류", f"{len(df_counts)}종")
            m3.metric("최다 빈도 단어", df_counts.iloc[0]['단어'])
            m4.metric("주요 품사", df_counts.iloc[0]['품사'])

            # 2. 번역 및 리스트
            st.write("---")
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("### 🌍 영문 번역")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.success(translation.text)
                except:
                    st.error("번역 서비스 응답 지연")

            with col_r:
                st.markdown("### 📊 단어 목록")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                # 데이터 에디터 배경 조정을 위해 key 추가
                st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("사전", display_text="보기")}, hide_index=True, key="dark_editor")

            # 3. 그래프 (다크 테마 적용)
            st.write("---")
            st.markdown("### 📈 빈도 분석 차트")
            top_10 = df_counts.head(10)
            fig = px.bar(top_10, x='단어', y='횟수', color='품사', 
                         template="plotly_dark", # 다크 모드 전용 템플릿
                         color_discrete_sequence=px.colors.qualitative.Vivid)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # 4. 품사 학습 가이드 (블랙 모드 최적화)
            st.write("---")
            st.markdown("### 📚 맞춤형 문법 학습")
            
            p_col1, p_col2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "📌", "desc": "이름을 나타내는 말 (Name)"},
                "동사": {"icon": "🏃", "desc": "움직임을 나타내는 말 (Action)"},
                "형용사": {"icon": "✨", "desc": "상태를 묘사하는 말 (Status)"},
                "부사": {"icon": "🎯", "desc": "자세히 꾸며주는 말 (Adverb)"}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = p_col1 if i < 2 else p_col2
                with target_col:
                    with st.expander(f"{info['icon']} {name} 마스터하기", expanded=True):
                        spec_df = df_counts[df_counts['품사'] == name]
                        top_w = spec_df.iloc[0]['단어'] if not spec_df.empty else "분석 결과 없음"
                        cnt = spec_df.iloc[0]['횟수'] if not spec_df.empty else 0
                        
                        st.markdown(f"""
                            <div class="custom-card">
                                <h4 style="margin:0; color:#FF4B4B;">{info['desc']}</h4>
                                <p style="margin:15px 0; font-size:1.1rem;">이 곡의 대표 단어: <b>{top_w}</b> (총 {cnt}회)</p>
                                <a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank">네이버 사전으로 더 알아보기 →</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("분석할 단어가 충분하지 않습니다.")
    else:
        st.error("분석할 가사를 입력해 주세요.")