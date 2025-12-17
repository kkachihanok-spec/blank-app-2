import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="K-POP INSIGHT", layout="wide", page_icon="🎧")

# 2. 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# 3. 세션 상태 초기화 (페이지 증발 방지 핵심)
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

# 4. 커스텀 CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    .main-product-title {
        font-family: 'Inter', sans-serif;
        font-size: 4rem !important; 
        font-weight: 900 !important;
        background: linear-gradient(135deg, #2a3f88 0%, #4a5fcc 50%, #7d8dec 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2 !important;
    }
    .sub-text { color: #8b92b2 !important; font-size: 1.2rem !important; font-weight: 600; }
    .lyrics-card {
        border-left: 4px solid #4a5fcc;
        padding: 24px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        height: 520px;
        overflow-y: auto;
    }
    .kr-txt { font-size: 1.1rem; color: #FFFFFF; font-weight: 600; display: block; }
    .en-txt { font-size: 0.95rem; color: #8b92b2; font-style: italic; }
    .analysis-card {
        border-left: 4px solid #2a3f88;
        padding: 16px 20px;
        margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
    }
    /* 퀴즈 정답 섹션 여백 */
    .quiz-result-area { margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 헤더 ---
st.markdown('<h1 class="main-product-title">&lt;K-POP INSIGHT&gt;</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">가사 데이터 분석 및 맞춤형 문법 엔진</p>', unsafe_allow_html=True)
st.divider()

# --- 입력 섹션 ---
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    if st.button("🚀 분석을 실행해줘!"):
        if lyrics_input.strip():
            with st.spinner('데이터 분석 중...'):
                morphs = okt.pos(lyrics_input, stem=True)
                target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
                all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
                df_all = pd.DataFrame(all_words)
                
                if not df_all.empty:
                    df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)
                    # 분석 결과 세션에 저장 (증발 방지)
                    st.session_state.analyzed_data = {
                        'all_words': all_words,
                        'df_counts': df_counts,
                        'lyrics': lyrics_input
                    }
        else:
            st.error("가사를 입력해 주세요.")

# --- 분석 결과 로직 (세션에 데이터가 있을 때만 실행) ---
if st.session_state.analyzed_data:
    data = st.session_state.analyzed_data
    df_counts = data['df_counts']
    all_words = data['all_words']

    st.divider()
    st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

    # 1. 요약 대시보드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 단어", f"→ {len(all_words)}")
    m2.metric("고유 단어", f"→ {len(df_counts)}")
    m3.metric("최빈 단어", f"→ {df_counts.iloc[0]['단어']}")
    m4.metric("주요 품사", f"→ {df_counts.iloc[0]['품사']}")

    # 2. 번역 및 데이터 섹션
    st.divider()
    c_l, c_r = st.columns([1.2, 1])
    with c_l:
        st.markdown("### 🌍 가사 대조 번역")
        lines = [line.strip() for line in data['lyrics'].split('\n') if line.strip()]
        html_output = '<div class="lyrics-card">'
        for line in lines:
            try:
                translated = translator.translate(line, dest='en').text
                html_output += f'<div style="margin-bottom:20px;"><span class="kr-txt">{line}</span><span class="en-txt">{translated}</span></div>'
            except:
                html_output += f'<div style="margin-bottom:20px;"><span class="kr-txt">{line}</span></div>'
        html_output += '</div>'
        st.markdown(html_output, unsafe_allow_html=True)

    with c_r:
        st.markdown("### 📊 분석 데이터")
        df_display = df_counts.copy()
        df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
        st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크")}, hide_index=True, use_container_width=True, height=520)

    # 3. 그래프
    st.divider()
    st.markdown("### 📈 단어 빈도 시각화")
    fig = px.bar(df_counts.head(20), x='단어', y='횟수', color='품사', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    # 4. 문법 학습 섹션
    st.divider()
    st.markdown("### 📚 가사 속 문법 학습")
    pos_info = {"명사": "💎", "동사": "⚡", "형용사": "🎨", "부사": "🎬"}
    p1, p2 = st.columns(2)
    for i, (name, icon) in enumerate(pos_info.items()):
        target_col = p1 if i < 2 else p2
        spec_df = df_counts[df_counts['품사'] == name]
        if not spec_df.empty:
            with target_col:
                st.markdown(f'<div class="analysis-card"><b>{icon} {name}</b>: {spec_df.iloc[0]["단어"]} ({spec_df.iloc[0]["횟수"]}회)</div>', unsafe_allow_html=True)

    # 5. [해결] 퀴즈 섹션 (증발 X, 유령 박스 X)
    st.divider()
    st.markdown("### 📝 오늘의 가사 퀴즈")
    top_word, top_pos = df_counts.iloc[0]['단어'], df_counts.iloc[0]['품사']
    
    st.markdown(f"**Q. 가사에서 가장 많이 사용된 '{top_word}'의 품사는 무엇일까요?**")
    
    user_choice = st.radio(
        "정답을 선택하세요", 
        ["명사", "동사", "형용사", "부사"], 
        index=None, 
        key="quiz_session_final",
        label_visibility="collapsed"
    )
    
    if user_choice:
        if user_choice == top_pos:
            st.success(f"정답입니다! 🎉 '{top_word}'은(는) {top_pos}입니다.")
            st.balloons()
        else:
            st.error("아쉬워요! 분석 데이터를 다시 확인해 보세요.")