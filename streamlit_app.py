import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="K-Lyric 101", layout="wide", page_icon="🎧")

# 2. 리소스 로드
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 세션 상태 초기화 ---
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None
if 'translated_lines' not in st.session_state:
    st.session_state.translated_lines = []

# 3. 커스텀 CSS (사용자 원코드 100% 복구 + 결과창만 프리미엄 레이아웃)
st.markdown("""
    <style>
    /* [원코드 복구] 메인 레이아웃 및 텍스트 */
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    .main-title-kr {
        font-family: 'Inter', sans-serif; font-size: 4.5rem !important; font-weight: 900 !important;
        letter-spacing: -2px; background: linear-gradient(135deg, #7d8dec 0%, #4a5fcc 50%, #2a3f88 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0rem !important; line-height: 1.1 !important; padding-top: 1rem;
    }
    .brand-title-en {
        font-family: 'Inter', sans-serif; font-size: 2.5rem !important; font-weight: 700 !important;
        color: #FFFFFF !important; margin-top: -10px !important; margin-bottom: 0.5rem !important; letter-spacing: 1px;
    }
    .sub-text { color: #8b92b2 !important; font-size: 1.1rem !important; font-weight: 500; margin-bottom: 1.5rem !important; }
    hr { border-bottom: 1px solid #2d3548 !important; }
    
    .stTextArea label p { font-size: 1.7rem !important; font-weight: 800 !important; color: #FFFFFF !important; margin-bottom: 25px !important; }
    .stTextArea textarea { background-color: rgba(20, 27, 45, 0.7) !important; color: #FFFFFF !important; border-radius: 12px !important; border: 1px solid #2d3548 !important; }
    
    .stButton>button {
        background-color: #4e5ec5 !important; border: none !important; border-radius: 2px !important; color: #FFFFFF !important;
        font-weight: 800 !important; font-size: 1.73rem !important; width: auto !important; min-width: 150px !important;
        height: 3.84rem !important; margin-top: 20px !important; display: flex !important; justify-content: center !important;
        padding-left: 30px !important; padding-right: 30px !important; align-items: center !important; transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }

    /* [원코드 복구] 가사 대조 및 분석 카드 */
    .lyrics-card {
        border-left: 4px solid #4a5fcc; padding: 24px; background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0; border: 1px solid rgba(45, 53, 72, 0.5); height: 520px; overflow-y: auto;
    }
    .analysis-card {
        border-left: 4px solid #2a3f88; padding: 16px 20px; margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25); border-radius: 0 12px 12px 0; border: 1px solid rgba(45, 53, 72, 0.5);
    }
    .quiz-outer-box {
        background: rgba(45, 53, 72, 0.15); border: 1px solid rgba(74, 95, 204, 0.3);
        border-radius: 12px; padding: 12px 20px; margin-top: 5px; margin-bottom: 25px; 
    }

    /* 🔥 [새로운 점수 결과창 스타일] */
    .score-container-premium {
        padding: 60px 40px; border-radius: 24px; text-align: center; margin: 40px 0;
        backdrop-filter: blur(20px); box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        animation: fadeInUp 0.7s ease-out;
    }
    .score-fail-premium { 
        background: linear-gradient(145deg, rgba(255, 59, 48, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%);
        border: 1px solid rgba(255, 59, 48, 0.3);
    }
    .score-pass-premium { 
        background: linear-gradient(145deg, rgba(74, 95, 204, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%);
        border: 1px solid rgba(74, 95, 204, 0.3);
    }
    .score-number-premium { 
        font-size: 7rem !important; font-weight: 900 !important; line-height: 1; margin: 20px 0 !important;
        letter-spacing: -3px;
    }
    .score-text-fail { background: linear-gradient(180deg, #ff4d4d, #9e1a1a); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .score-text-pass { background: linear-gradient(180deg, #7d8dec, #3a47af); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .score-status-text { font-size: 1.5rem; font-weight: 600; color: white; opacity: 0.9; margin-top: 15px; }

    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """, unsafe_allow_html=True)

# --- 메인 코드 ---
st.markdown('<div class="main-title-kr">가사학개론</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title-en">K-Lyric 101</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">AI 기반 K-POP 가사 데이터 분석 및 언어 학습 엔진</p>', unsafe_allow_html=True)
st.divider()

lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석을 실행해줘!")

if analyze_btn:
    if lyrics_input.strip():
        with st.spinner('데이터 분석 중...'):
            morphs = okt.pos(lyrics_input, stem=True)
            target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
            all_words = [{'단어': w, '품사': target_pos_map[p]} for w, p in morphs if p in target_pos_map and len(w) >= 1]
            df_all = pd.DataFrame(all_words)
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수').sort_values(by='횟수', ascending=False)
            
            lines = [line.strip() for line in lyrics_input.split('\n') if line.strip()]
            translated_list = []
            for line in lines:
                try: trans = translator.translate(line, dest='en').text
                except: trans = "Translation Error"
                translated_list.append({"kr": line, "en": trans})
            
            st.session_state.analyzed_data = {'all_words': all_words, 'df_counts': df_counts, 'lyrics_input': lyrics_input}
            st.session_state.translated_lines = translated_list
    else:
        st.error("가사를 입력해 주세요.")

if st.session_state.analyzed_data:
    data = st.session_state.analyzed_data
    df_counts = data['df_counts']
    
    st.divider()
    st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 단어", f"{len(data['all_words'])}")
    m2.metric("고유 단어", f"{len(df_counts)}")
    m3.metric("최빈 단어", f"{df_counts.iloc[0]['단어']}")
    m4.metric("주요 품사", f"{df_counts.iloc[0]['품사']}")

    st.divider()
    c_l, c_r = st.columns([1.2, 1])
    with c_l:
        st.markdown("### 🌍 가사 대조 번역")
        html_output = '<div class="lyrics-card">'
        for item in st.session_state.translated_lines:
            html_output += f'<div style="margin-bottom:20px; border-bottom:1px solid rgba(141,146,178,0.1); padding-bottom:10px;"><span class="kr-txt" style="font-size:1.1rem; color:white; font-weight:600; display:block;">{item["kr"]}</span><span class="en-txt" style="font-size:0.95rem; color:#8b92b2; display:block; font-style:italic;">{item["en"]}</span></div>'
        st.markdown(html_output + '</div>', unsafe_allow_html=True)
    with c_r:
        st.markdown("### 📊 분석 데이터")
        df_display = df_counts.copy()
        df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
        st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True, use_container_width=True, height=520)

    st.divider()
    st.markdown("### 📈 단어 빈도 시각화")
    top_20 = df_counts.head(20)
    fig = px.bar(top_20, x='단어', y='횟수', color='품사', color_discrete_map={'명사': '#7d8dec', '동사': '#4a5fcc', '형용사': '#2a3f88', '부사': '#8b92b2'}, template='plotly_dark')
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

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
                st.markdown(f'''<div class="analysis-card"><div class="pos-title" style="font-size:1.3rem; font-weight:800; color:#7d8dec; margin-bottom:10px;">{info['icon']} {name}</div><div class="pos-desc" style="color:#8b92b2; margin-bottom:12px;">{info['desc']}</div><div class="data-row" style="display:flex; align-items:baseline; border-top:1px solid rgba(141,146,178,0.2); padding-top:12px;"><span style="color:#8b92b2; margin-right:10px;">주요 단어:</span><span style="font-weight:700; color:white; font-size:1.1rem;">{top_w}</span><span style="color:#4a5fcc; font-weight:600; margin-left:10px;">{cnt}회</span></div></div>''', unsafe_allow_html=True)

    # --- 퀴즈 섹션 (원코드 로직 유지) ---
    st.divider()
    st.markdown("### 📝 오늘의 가사 퀴즈")
    
    top_word, top_pos = df_counts.iloc[0]['단어'], df_counts.iloc[0]['품사']
    other_pos_df = df_counts[df_counts['품사'] != top_pos]
    second_word = other_pos_df.iloc[0]['단어'] if len(other_pos_df) > 0 else "가사"
    second_pos = other_pos_df.iloc[0]['품사'] if len(other_pos_df) > 0 else "명사"

    quiz_data = [
        (f"가장 많이 사용된 '{top_word}'의 품사는 무엇인가요?", top_pos, "nq1"),
        (f"단어 '{second_word}'의 품사는 무엇일까요?", second_pos, "nq2"),
        (f"이 가사에는 총 몇 개의 '고유 단어'가 사용되었나요?", f"{len(df_counts)}개", "nq3"),
        (f"전체 가사 중 단어의 총 개수는 몇 개인가요?", f"{len(data['all_words'])}개", "nq5"),
        ("분석된 가사가 K-POP 학습에 도움이 되나요?", "네", "nq4")
    ]
    
    user_results = []
    total_score = 0
    all_answered = True
    
    for i, (q_text, q_ans, q_key) in enumerate(quiz_data):
        st.markdown(f'<div class="quiz-outer-box"><b>Q{i+1}. {q_text}</b>', unsafe_allow_html=True)
        opts = [q_ans, "오답A", "오답B", "오답C"] if i < 4 else ["네", "아니오"]
        ans = st.radio(f"Radio_{q_key}", opts, index=None, key=q_key, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        if ans:
            if ans == q_ans: total_score += 20
        else: all_answered = False

    # --- ✨ [업데이트된 점수 결과창] ---
    if all_answered:
        st.divider()
        score_class = "score-pass-premium" if total_score >= 51 else "score-fail-premium"
        text_color_class = "score-text-pass" if total_score >= 51 else "score-text-fail"
        status_msg = "PERFECT ANALYSIS" if total_score >= 51 else "NEED MORE STUDY"
        
        st.markdown(f'''
            <div class="score-container-premium {score_class}">
                <div style="letter-spacing: 5px; color: rgba(255,255,255,0.4); font-size: 0.9rem; font-weight: 700;">LEARNING REPORT</div>
                <div class="score-number-premium {text_color_class}">{total_score} / 100</div>
                <div class="score-status-text">{status_msg}</div>
            </div>
        ''', unsafe_allow_html=True)

        st.download_button(label="✨ 오늘 학습 리포트 저장하기", data="학습 데이터 기록...", file_name="K-Lyric_Report.txt")