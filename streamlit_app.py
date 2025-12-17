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

# 세션 상태 초기화 (페이지 새로고침 시 데이터 유지용)
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'lyrics_text' not in st.session_state:
    st.session_state.lyrics_text = ""

# 3. 커스텀 CSS
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
    }

    hr { border-bottom: 1px solid #2d3548 !important; }

    .stTextArea label p {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 25px !important; 
    }

    .stTextArea textarea {
        background-color: rgba(20, 27, 45, 0.7) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #2d3548 !important;
    }

    .stButton>button {
        background-color: #2a3f88 !important;
        color: #FFFFFF !important;
        font-weight: 700;
        width: auto !important;
        min-width: 150px !important;
        height: 3.84rem !important;   
        font-size: 1.44rem !important; 
        border: none;
        margin-top: 20px !important;  
        display: flex !important;
        padding-left: 30px !important;
        padding-right: 30px !important;
        align-items: center !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #4a5fcc !important;
        transform: translateY(-2px);
    }

    [data-testid="stMetricLabel"] p { 
        font-size: 1.6rem !important; 
        color: #FFFFFF !important; 
        font-weight: 900 !important; 
    }
    [data-testid="stMetricValue"] { 
        font-size: 1.67rem !important; 
        color: #4a5fcc !important; 
        font-weight: 700 !important; 
    }

    .lyrics-card {
        border-left: 4px solid #4a5fcc;
        padding: 24px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        border: 1px solid rgba(45, 53, 72, 0.5);
        height: 520px;
        overflow-y: auto;
    }
    
    .lyrics-line-pair {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(141, 146, 178, 0.1);
    }
    
    .kr-txt { font-size: 1.1rem; color: #FFFFFF; font-weight: 600; display: block; }
    .en-txt { font-size: 0.95rem; color: #8b92b2; font-style: italic; display: block; }

    .analysis-card {
        border-left: 4px solid #2a3f88;
        padding: 16px 20px;
        margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0;
        border: 1px solid rgba(45, 53, 72, 0.5);
    }
    
    .pos-title { font-size: 1.3rem !important; font-weight: 800 !important; color: #7d8dec; }
    .data-row { display: flex; align-items: baseline; border-top: 1px solid rgba(141, 146, 178, 0.2); padding-top: 12px; }
    .card-word { font-weight: 700 !important; color: #FFFFFF; } 
    .card-count { color: #4a5fcc; font-weight: 600; margin-left: 10px; } 
    
    .lyrics-card::-webkit-scrollbar { width: 6px; }
    .lyrics-card::-webkit-scrollbar-thumb { background: #2a3f88; border-radius: 10px; }
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
            st.session_state.analyzed = True
            st.session_state.lyrics_text = lyrics_input
        else:
            st.error("가사를 입력해 주세요.")

# --- 분석 결과 섹션 ---
if st.session_state.analyzed:
    input_data = st.session_state.lyrics_text
    st.divider()
    st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

    with st.spinner('데이터 분석 중...'):
        morphs = okt.pos(input_data, stem=True)
        target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
        all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
        df_all = pd.DataFrame(all_words)

    if not df_all.empty:
        df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)

        # 1. 요약 대시보드
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("전체 단어", f"→ {len(all_words)}")
        m2.metric("고유 단어", f"→ {len(df_counts)}")
        m3.metric("최빈 단어", f"→ {df_counts.iloc[0]['단어']}")
        m4.metric("주요 품사", f"→ {df_counts.iloc[0]['품사']}")

        # 2. 번역 및 데이터 표
        st.divider()
        c_l, c_r = st.columns([1.2, 1])
        with c_l:
            st.markdown("### 🌍 가사 대조 번역")
            lines = [line.strip() for line in input_data.split('\n') if line.strip()]
            html_output = '<div class="lyrics-card">'
            for line in lines:
                try:
                    translated = translator.translate(line, dest='en').text
                    html_output += f'<div class="lyrics-line-pair"><span class="kr-txt">{line}</span><span class="en-txt">{translated}</span></div>'
                except:
                    html_output += f'<div class="lyrics-line-pair"><span class="kr-txt">{line}</span></div>'
            html_output += '</div>'
            st.markdown(html_output, unsafe_allow_html=True)

        with c_r:
            st.markdown("### 📊 분석 데이터")
            df_display = df_counts.copy()
            df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
            st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True, use_container_width=True, height=520)

        # 3. 그래프 섹션
        st.divider()
        st.markdown("### 📈 단어 빈도 시각화")
        fig = px.bar(df_counts.head(20), x='단어', y='횟수', color='품사', color_discrete_map={'명사': '#7d8dec', '동사': '#4a5fcc', '형용사': '#2a3f88', '부사': '#8b92b2'}, template='plotly_dark')
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="빈도수"))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 4. 문법 학습 섹션
        st.divider()
        st.markdown("### 📚 가사 속 문법 학습")
        pos_info = {"명사": {"icon": "💎", "desc": "사물이나 개념의 이름입니다."}, "동사": {"icon": "⚡", "desc": "동작이나 움직임을 나타냅니다."}, "형용사": {"icon": "🎨", "desc": "상태나 성질을 묘사합니다."}, "부사": {"icon": "🎬", "desc": "행동을 더 세밀하게 꾸며줍니다."}}
        p1, p2 = st.columns(2)
        for i, (name, info) in enumerate(pos_info.items()):
            target_col = p1 if i < 2 else p2
            with target_col:
                spec_df = df_counts[df_counts['품사'] == name]
                if not spec_df.empty:
                    top_w, cnt = spec_df.iloc[0]['단어'], spec_df.iloc[0]['횟수']
                    st.markdown(f'''<div class="analysis-card"><div class="pos-title">{info['icon']} {name}</div><div style="color:#8b92b2; margin-bottom:14px;">{info['desc']}</div><div class="data-row"><span style="color:#8b92b2; margin-right:10px;">주요 단어:</span><span class="card-word">{top_w}</span><span class="card-count">{cnt}회</span><a href="https://ko.dict.naver.com/#/search?query={top_w}" target="_blank" style="font-size:0.8rem; margin-left:auto; color:#7d8dec; text-decoration:none;">사전 보기 →</a></div></div>''', unsafe_allow_html=True)

        # 5. [최종 수정] 퀴즈 섹션 (텍스트 크기 -20% 및 가변형 박스)
        st.divider()
        st.markdown("### 📝 오늘의 가사 퀴즈")
        with st.container():
            top_word, top_pos = df_counts.iloc[0]['단어'], df_counts.iloc[0]['품사']
            
            # display: inline-block을 통해 텍스트 길이에 맞춰 박스가 생성되도록 함
            # font-size: 1.2rem으로 조절하여 시각적으로 20% 정도 작아지도록 세팅
            st.markdown(f"""
                <div style="
                    background: rgba(74, 95, 204, 0.1); 
                    border: 1px solid #4a5fcc; 
                    padding: 15px 25px; 
                    border-radius: 12px; 
                    display: inline-block; 
                    margin-bottom: 20px;
                ">
                    <span style="
                        margin: 0; 
                        color: white; 
                        font-size: 1.2rem; 
                        font-weight: 600; 
                        line-height: 1.5;
                    ">
                        Q. 이 가사에서 가장 많이 사용된 단어는 '{top_word}'입니다. 이 단어의 품사는 무엇일까요?
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            user_choice = st.radio("정답을 골라보세요!", ["명사", "동사", "형용사", "부사"], index=None, key="quiz_final_v2")
            if user_choice:
                if user_choice == top_pos:
                    st.success(f"정답입니다! 🎉 '{top_word}'은(는) **{top_pos}**입니다.")
                    st.balloons()
                else:
                    st.error("아쉬워요! 위쪽 분석 데이터를 다시 확인해 보세요. 🧐")
    else:
        st.warning("분석할 단어가 부족합니다.")