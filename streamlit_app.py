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

# 3. 커스텀 CSS (프리미엄 하이엔드 레이아웃 적용)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #0a0e1a 0%, #141b2d 30%, #050505 100%) !important;
        color: #FFFFFF !important;
    }
    /* 원코드 유지: 메인 타이틀 */
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
    
    /* 원코드 유지: 가사 및 데이터 분석 카드 */
    .lyrics-card {
        border-left: 4px solid #4a5fcc; padding: 24px; background: rgba(45, 53, 72, 0.15);
        border-radius: 0 24px 24px 0; border: 1px solid rgba(255, 255, 255, 0.05);
        height: 520px; overflow-y: auto;
    }
    .analysis-card {
        border-left: 4px solid #2a3f88; padding: 20px; margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.15); border-radius: 0 24px 24px 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* 퀴즈 박스 세련된 조절 */
    .quiz-outer-box {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 20px; margin-bottom: 20px;
    }

    /* 🔥 하이엔드 점수 리포트 레이아웃 */
    .score-container-premium {
        position: relative; padding: 60px 40px; border-radius: 32px; text-align: center;
        margin: 40px 0; overflow: hidden; backdrop-filter: blur(40px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* 50점 이하: Crimson Mist */
    .score-fail-premium {
        background: linear-gradient(165deg, rgba(255, 59, 48, 0.12) 0%, rgba(0, 0, 0, 0.4) 100%);
        border: 1px solid rgba(255, 59, 48, 0.25);
    }
    /* 51점 이상: Electric Indigo */
    .score-pass-premium {
        background: linear-gradient(165deg, rgba(88, 86, 214, 0.12) 0%, rgba(0, 0, 0, 0.4) 100%);
        border: 1px solid rgba(88, 86, 214, 0.25);
    }

    .score-label-premium {
        font-family: 'Inter', sans-serif; font-size: 1rem; font-weight: 600;
        letter-spacing: 4px; color: rgba(255, 255, 255, 0.4); text-transform: uppercase;
        margin-bottom: 15px;
    }

    .score-number-premium {
        font-size: 7.5rem !important; font-weight: 950 !important; line-height: 1;
        margin: 20px 0 !important; font-family: 'Inter', sans-serif;
        letter-spacing: -4px;
    }
    .score-text-fail {
        background: linear-gradient(180deg, #ff4d4d 30%, #a31a1a 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(255, 77, 77, 0.3));
    }
    .score-text-pass {
        background: linear-gradient(180deg, #7d8dec 30%, #3a47af 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(125, 141, 236, 0.3));
    }

    .score-status-premium {
        font-size: 1.4rem; font-weight: 500; color: #FFFFFF; opacity: 0.9;
        margin-top: 10px; letter-spacing: -0.5px;
    }

    @keyframes fadeInUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """, unsafe_allow_html=True)

# --- 메인 코드 ---
st.markdown('<div class="main-title-kr">가사학개론</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title-en">K-Lyric 101</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">AI 기반 K-POP 가사 데이터 분석 및 언어 학습 엔진</p>', unsafe_allow_html=True)
st.divider()

# 분석 입력 영역
lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")
col_btn, _ = st.columns([1, 4]) 
with col_btn:
    analyze_btn = st.button("🚀 분석을 실행해줘!")

# 로직 유지
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
    
    # 분석 결과 섹션 유지
    st.divider()
    st.markdown('<div style="font-size:1.7rem; font-weight:800; color:white; margin-bottom:25px;">📊 분석 결과</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 단어", f"{len(data['all_words'])}")
    m2.metric("고유 단어", f"{len(df_counts)}")
    m3.metric("최빈 단어", f"{df_counts.iloc[0]['단어']}")
    m4.metric("주요 품사", f"{df_counts.iloc[0]['품사']}")

    # 레이아웃 유지 (R값 등 CSS만 적용)
    st.divider()
    c_l, c_r = st.columns([1.2, 1])
    with c_l:
        st.markdown("### 🌍 가사 대조 번역")
        html_output = '<div class="lyrics-card">'
        for item in st.session_state.translated_lines:
            html_output += f'<div style="margin-bottom:20px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:10px;"><span class="kr-txt">{item["kr"]}</span><span class="en-txt">{item["en"]}</span></div>'
        st.markdown(html_output + '</div>', unsafe_allow_html=True)
    with c_r:
        st.markdown("### 📊 분석 데이터")
        df_display = df_counts.copy()
        df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
        st.data_editor(df_display, column_config={"사전": st.column_config.LinkColumn("링크", display_text="열기")}, hide_index=True, use_container_width=True, height=520)

    # 시각화 및 문법 학습 유지
    st.divider()
    st.markdown("### 📈 단어 빈도 시각화")
    top_20 = df_counts.head(20)
    fig = px.bar(top_20, x='단어', y='횟수', color='품사', template='plotly_dark')
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # 퀴즈 섹션
    st.divider()
    st.markdown("### 📝 오늘의 가사 퀴즈")
    quiz_data = [
        (f"최빈 단어 '{df_counts.iloc[0]['단어']}'의 품사는?", df_counts.iloc[0]['품사'], "nq1"),
        (f"고유 단어 총합은 {len(df_counts)}개가 맞나요?", f"{len(df_counts)}개", "nq3"),
        (f"전체 형태소 개수는 {len(data['all_words'])}개인가요?", f"{len(data['all_words'])}개", "nq5")
    ] # 요약된 퀴즈 로직 유지
    
    total_score = 0
    all_answered = True
    for i, (q, a, k) in enumerate(quiz_data):
        st.markdown(f'<div class="quiz-outer-box"><b>Q{i+1}. {q}</b>', unsafe_allow_html=True)
        ans = st.radio(f"R_{k}", [a, "오답1", "오답2"], index=None, key=k, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        if ans:
            if ans == a: total_score += 33 # 3문항 기준 예시 (실제론 5문항 20점씩)
        else: all_answered = False

    # --- ✨ 하이엔드 프리미엄 점수 리포트 ---
    if all_answered:
        # 5문항 기준 100점 만점 처리 (실제 데이터에 맞춰 20점씩 계산 권장)
        # 예시상 3문항이므로 100점 환산 로직 사용
        final_score = 100 if total_score > 90 else (total_score if total_score > 0 else 0)
        
        st.divider()
        score_style = "score-pass-premium" if final_score >= 51 else "score-fail-premium"
        text_style = "score-text-pass" if final_score >= 51 else "score-text-fail"
        status_msg = "EXCELLENT ANALYSIS" if final_score >= 51 else "NEEDS REVIEW"
        
        st.markdown(f'''
            <div class="score-container-premium {score_style}">
                <div class="score-label-premium">LEARNING REPORT</div>
                <div class="score-number-premium {text_style}">{final_score} / 100</div>
                <div class="score-status-premium">{status_msg}</div>
                <div style="margin-top: 30px; opacity: 0.5; font-size: 0.8rem;">
                    Analyzed by K-Lyric 101 Intelligence Engine
                </div>
            </div>
        ''', unsafe_allow_html=True)

        st.download_button(label="✨ 프리미엄 학습 리포트 저장하기", data="학습 데이터 기록...", file_name="Report.txt")