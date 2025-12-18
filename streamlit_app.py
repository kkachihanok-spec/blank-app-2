import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
from datetime import datetime
import random

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

# 3. 커스텀 CSS
st.markdown("""
    <style>
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
    
    [data-testid="stMetricLabel"] p { font-size: 1.1rem !important; color: #4a5fcc !important; font-weight: 900 !important; margin-bottom: 6px !important; }
    [data-testid="stMetricValue"] div:first-child::before { content: "→ "; color: #8b92b2 !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] div { font-size: 1.54rem !important; color: #FFFFFF !important; font-weight: 700 !important; }
    
    .lyrics-card {
        border-left: 4px solid #4a5fcc; padding: 24px; background: rgba(45, 53, 72, 0.25);
        border-radius: 0 12px 12px 0; border: 1px solid rgba(45, 53, 72, 0.5); height: 520px; overflow-y: auto;
    }
    .kr-txt { font-size: 1.1rem; color: #FFFFFF; font-weight: 600; display: block; margin-bottom: 4px; }
    .en-txt { font-size: 0.95rem; color: #8b92b2; font-weight: 400; display: block; font-style: italic; }
    
    .analysis-card {
        border-left: 4px solid #2a3f88; padding: 16px 20px; margin-bottom: 16px;
        background: rgba(45, 53, 72, 0.25); border-radius: 0 12px 12px 0; border: 1px solid rgba(45, 53, 72, 0.5);
    }
    .pos-title { font-size: 1.3rem !important; font-weight: 800 !important; color: #7d8dec; margin-bottom: 10px; }
    .data-row { display: flex; align-items: baseline; border-top: 1px solid rgba(141, 146, 178, 0.2); padding-top: 12px; }
    .card-word { font-weight: 700 !important; color: #FFFFFF; font-size: 1.1rem; } 
    .card-count { color: #4a5fcc; font-weight: 600; margin-left: 10px; } 

    .quiz-outer-box {
        background: rgba(45, 53, 72, 0.15); border: 1px solid rgba(74, 95, 204, 0.3);
        border-radius: 12px; padding: 12px 20px; margin-top: 5px; margin-bottom: 25px; 
    }
    div[data-testid="stRadio"] > div { gap: 0px !important; margin-top: -12px !important; }
    [data-testid="stWidgetLabel"] { display: none; }
    div[data-testid="stRadio"] label { color: white !important; font-size: 0.95rem !important; }

    .custom-result-box {
        padding: 12px 20px; border-radius: 8px; border: 1px solid transparent;
        animation: fadeInUp 0.25s ease-out forwards; margin-bottom: 25px;
    }
    .correct-box { background: rgba(74, 95, 204, 0.1); border-color: #4a5fcc; }
    .wrong-box { background: rgba(157, 80, 187, 0.05); border-color: rgba(157, 80, 187, 0.5); }
    .result-title { font-size: 1.25rem !important; font-weight: 800 !important; margin-bottom: 2px !important; display: block; }

    .score-container-premium {
        padding: 40px 40px; border-radius: 24px; text-align: center; margin: 40px 0;
        backdrop-filter: blur(20px); box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        animation: fadeInUp 0.7s ease-out;
    }
    .score-fail-premium { background: linear-gradient(145deg, rgba(110, 72, 170, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%); border: 1px solid rgba(110, 72, 170, 0.3); }
    .score-pass-premium { background: linear-gradient(145deg, rgba(74, 95, 204, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%); border: 1px solid rgba(74, 95, 204, 0.3); }
    
    .score-label-premium { letter-spacing: 2px !important; color: rgba(255,255,255,0.7); font-size: 0.9rem !important; font-weight: 400 !important; margin-bottom: 0px !important; }
    .score-number-premium { font-size: 5.91rem !important; font-weight: 900 !important; line-height: 0.9 !important; margin: 10px 0 20px 0 !important; letter-spacing: -2px; }
    
    .score-text-fail { color: #AF40FF !important; -webkit-text-fill-color: #AF40FF !important; background: none !important; }
    .score-text-pass { color: #516df4 !important; -webkit-text-fill-color: #516df4 !important; background: none !important; }
    
    .score-status-text { font-size: 1.28rem !important; font-weight: 700; color: white; opacity: 1.0; margin-top: 5px !important; }

    @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """, unsafe_allow_html=True)

# --- 메인 실행 로직 ---
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
            html_output += f'<div style="margin-bottom:20px; border-bottom:1px solid rgba(141,146,178,0.1); padding-bottom:10px;"><span class="kr-txt">{item["kr"]}</span><span class="en-txt">{item["en"]}</span></div>'
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
                st.markdown(f'''<div class="analysis-card"><div class="pos-title">{info['icon']} {name}</div><div class="pos-desc">{info['desc']}</div><div class="data-row"><span style="color:#8b92b2; margin-right:10px;">주요 단어:</span><span class="card-word">{top_w}</span><span class="card-count">{cnt}회</span></div></div>''', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📝 오늘의 가사 퀴즈")
    
    top_word, top_pos = df_counts.iloc[0]['단어'], df_counts.iloc[0]['품사']
    other_pos_df = df_counts[df_counts['품사'] != top_pos]
    second_word = other_pos_df.iloc[0]['단어'] if len(other_pos_df) > 0 else "가사"
    second_pos = other_pos_df.iloc[0]['품사'] if len(other_pos_df) > 0 else "명사"
    third_word = other_pos_df.iloc[1]['단어'] if len(other_pos_df) > 1 else "노래"
    third_pos = other_pos_df.iloc[1]['품사'] if len(other_pos_df) > 1 else "명사"

    quiz_configs = [
        {"q": f"가장 많이 사용된 '{top_word}'의 품사는 무엇인가요?", "a": top_pos, "type": "pos"},
        {"q": f"단어 '{second_word}'의 품사는 무엇일까요?", "a": second_pos, "type": "pos"},
        {"q": f"이 가사에는 총 몇 개의 '고유 단어'가 사용되었나요?", "a": f"{len(df_counts)}개", "type": "count_unique"},
        {"q": f"가사 속에 등장한 '{third_word}'의 품사로 알맞은 것은?", "a": third_pos, "type": "pos"},
        {"q": f"전체 가사 중 단어의 총 개수는 몇 개인가요?", "a": f"{len(data['all_words'])}개", "type": "count_total"}
    ]
    
    total_score = 0
    all_answered = True
    
    for i, config in enumerate(quiz_configs):
        q_key = f"final_quiz_v12_q_{i}"
        st.markdown(f'<div class="quiz-outer-box"><div style="line-height: 1.2; margin-bottom: 4px;"><span style="color: #7d8dec; font-weight: 900; font-size: 1.2rem;">Q{i+1}.</span> <span style="color: white; font-size: 1.1rem; font-weight: 700;">{config["q"]}</span></div>', unsafe_allow_html=True)
        if config["type"] == "pos": opts = ["명사", "동사", "형용사", "부사"]
        elif config["type"] == "count_unique":
            b = len(df_counts); opts = [f"{b}개", f"{b+3}개", f"{max(0, b-2)}개", f"{b+7}개"]
        else:
            b = len(data['all_words']); opts = [f"{b}개", f"{b+12}개", f"{max(0, b-8)}개", f"{b+4}개"]
        
        if q_key not in st.session_state:
            random.shuffle(opts); st.session_state[q_key] = opts
        ans = st.radio(f"R_{q_key}", st.session_state[q_key], index=None, key=f"ans_f_v12_{q_key}", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        if ans:
            if ans == config["a"]:
                st.markdown(f'<div class="custom-result-box correct-box"><span class="result-title" style="color:#7d8dec;">🎉 정답입니다!</span></div>', unsafe_allow_html=True)
                total_score += 20
            else:
                st.markdown(f'<div class="custom-result-box wrong-box"><span class="result-title" style="color:#9D50BB;">아쉬워요!</span><span style="color:white; opacity:0.8;">정답: {config["a"]}</span></div>', unsafe_allow_html=True)
        else: all_answered = False

    if all_answered:
        st.divider()
        score_class = "score-pass-premium" if total_score >= 60 else "score-fail-premium"
        text_color_class = "score-text-pass" if total_score >= 60 else "score-text-fail"
        
        if total_score <= 20: status_msg = "기초부터 차근차근 시작해봐요!"
        elif 40 <= total_score <= 60: status_msg = "거의 다 왔어요! 조금만 더 집중해볼까요?"
        else: status_msg = "완벽한 분석입니다! K-POP 가사 마스터네요!"
        
        st.markdown(f'''
            <div class="score-container-premium {score_class}">
                <div class="score-label-premium">LEARNING REPORT</div>
                <div class="score-number-premium {text_color_class}">{total_score} / 100</div>
                <div class="score-status-text">{status_msg}</div>
            </div>
        ''', unsafe_allow_html=True)

        # --- 커스텀 폴딩 가이드 섹션 (폰트 20% 축소 반영) ---
        st.divider()
        
        if total_score >= 60:
            theme_color = "#516df4"  # 블루
            theme_bg = "rgba(81, 109, 244, 0.1)"
            guide_title = "🏆 K-POP 마스터를 위한 심화 조언"
            advice = "이미 훌륭한 실력을 갖추고 계시네요! 이제 가사의 <b>'은유적 표현'</b>이나 <b>'신조어'</b>에 주목해 보세요. 한국의 문학 작품이나 에세이를 병행하면 표현의 깊이가 달라질 거예요."
        else:
            theme_color = "#AF40FF"  # 퍼플
            theme_bg = "rgba(175, 64, 255, 0.1)"
            guide_title = "🌱 기초를 탄탄하게 만드는 조언"
            advice = "조급해하지 마세요! 가사 속의 <b>'명사'</b>부터 하나씩 수집해 보는 건 어떨까요? 좋아하는 가수의 인터뷰 영상을 자막과 함께 보며 발음을 익히는 것부터 시작해 보세요."

        st.markdown(f"""
            <style>
                .custom-details {{
                    background: {theme_bg}; border: 1px solid {theme_color}44;
                    border-radius: 15px; overflow: hidden; margin-bottom: 50px; transition: all 0.3s ease;
                }}
                .custom-details[open] {{ border: 1px solid {theme_color}; box-shadow: 0 5px 20px {theme_color}22; }}
                .custom-summary {{
                    padding: 20px; font-size: 1.25rem; font-weight: 800; color: #FFFFFF !important;
                    cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center;
                }}
                .custom-summary:hover {{ background: {theme_color}11; }}
                .custom-summary::after {{ content: '▼'; color: {theme_color}; font-size: 0.8rem; transition: transform 0.3s; }}
                .custom-details[open] .custom-summary::after {{ transform: rotate(180deg); }}
                
                /* 가이드 내부 콘텐츠 폰트 크기 20% 축소 (1.1rem -> 0.88rem, 10px -> 8px 등) */
                .guide-content {{ padding: 0 25px 25px 25px; animation: fadeIn 0.5s ease; }}
                .guide-header {{ color: {theme_color}; margin-top: 10px; font-weight: 800; font-size: 0.8rem !important; }}
                .guide-text {{ color: #FFFFFF; line-height: 1.7; font-size: 0.88rem !important; margin-bottom: 25px; }}
                .ref-header {{ color: {theme_color}; font-weight: 800; margin-bottom: 15px; font-size: 0.8rem !important; }}
                
                @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                
                .guide-link-card-custom {{
                    background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; 
                    text-align: center; color: #8b92b2 !important; border: 1px solid rgba(255,255,255,0.1);
                    text-decoration: none; display: block; transition: all 0.2s;
                    font-size: 0.8rem !important; /* 링크 폰트도 축소 */
                }}
                .guide-link-card-custom:hover {{ background: {theme_bg}; border-color: {theme_color}; color: white !important; }}
            </style>

            <details class="custom-details" open>
                <summary class="custom-summary"><span>{guide_title}</span></summary>
                <div class="guide-content">
                    <div class="guide-header">📝 학습 가이드</div>
                    <p class="guide-text">{advice}</p>
                    <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 25px;">
                    <div class="ref-header">🔗 추천 학습 레퍼런스</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <a href="https://dict.naver.com" target="_blank" class="guide-link-card-custom">🟢 네이버 국어사전</a>
                        <a href="https://www.topik.go.kr" target="_blank" class="guide-link-card-custom">🎓 TOPIK 공식 홈페이지</a>
                        <a href="https://www.sejonghakdang.org" target="_blank" class="guide-link-card-custom">🏫 세종학당재단</a>
                        <a href="https://vlive.tv" target="_blank" class="guide-link-card-custom">📺 K-Contents 학습</a>
                    </div>
                </div>
            </details>
        """, unsafe_allow_html=True)