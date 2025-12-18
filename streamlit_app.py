import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
from datetime import datetime
import random
import base64

# --- PDF 라이브러리 체크 ---
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

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

# 3. 커스텀 CSS (합격 컬러 #516df4 유지)
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
    
    .stTextArea textarea { background-color: rgba(20, 27, 45, 0.7) !important; color: #FFFFFF !important; border-radius: 12px !important; border: 1px solid #2d3548 !important; }
    
    /* 버튼 스타일 통합 */
    .stButton>button {
        background-color: #4e5ec5 !important; border: none !important; border-radius: 2px !important; color: #FFFFFF !important;
        font-weight: 800 !important; font-size: 1.5rem !important; width: auto !important;
        height: 3.5rem !important; margin-top: 20px !important; padding: 0 30px !important;
    }
    
    /* 다운로드 버튼 레이아웃 */
    .dl-container { display: flex; gap: 15px; margin-top: 20px; justify-content: center; flex-wrap: wrap; }
    div.stDownloadButton > button {
        background: rgba(81, 109, 244, 0.1) !important;
        border: 1px solid rgba(81, 109, 244, 0.4) !important;
        color: #516df4 !important; font-weight: 700 !important;
        padding: 10px 20px !important; border-radius: 8px !important;
    }

    /* 점수판 스타일 */
    .score-container-premium {
        padding: 40px; border-radius: 24px; text-align: center; margin: 40px 0;
        backdrop-filter: blur(20px); box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    .score-pass-premium { background: linear-gradient(145deg, rgba(74, 95, 204, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%); border: 1px solid rgba(74, 95, 204, 0.3); }
    .score-fail-premium { background: linear-gradient(145deg, rgba(110, 72, 170, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%); border: 1px solid rgba(110, 72, 170, 0.3); }
    .score-number-premium { font-size: 5.5rem !important; font-weight: 900 !important; }
    .score-text-pass { color: #516df4 !important; }
    .score-text-fail { color: #AF40FF !important; }

    /* PNG 안내 카드 */
    .png-tip {
        background: rgba(255, 255, 255, 0.05); border: 1px dashed rgba(255, 255, 255, 0.2);
        padding: 20px; border-radius: 15px; margin-top: 20px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 파일 생성 유틸리티
def create_txt(data, score, lines):
    report = f"--- K-Lyric 101 Analysis Report ---\n"
    report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"Final Score: {score}/100\n\n"
    report += "--- Original & Translation ---\n"
    for l in lines: report += f"KR: {l['kr']}\nEN: {l['en']}\n\n"
    report += "--- Vocabulary Analysis ---\n"
    for _, row in data['df_counts'].iterrows():
        report += f"{row['단어']} ({row['품사']}): {row['횟수']}회\n"
    return report

def create_pdf(data, score):
    if not FPDF_AVAILABLE: return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="K-Lyric 101 Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Score: {score}/100", ln=True)
    pdf.cell(200, 10, txt=f"Unique Words: {len(data['df_counts'])}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 메인 실행 로직 ---
st.markdown('<div class="main-title-kr">가사학개론</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title-en">K-Lyric 101</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">AI 기반 K-POP 가사 데이터 분석 및 언어 학습 엔진</p>', unsafe_allow_html=True)
st.divider()

lyrics_input = st.text_area("📝 가사 입력", height=180, placeholder="분석할 가사를 입력하세요...", key="lyrics_main")

if st.button("🚀 분석을 실행해줘!"):
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
            
            st.session_state.analyzed_data = {'all_words': all_words, 'df_counts': df_counts}
            st.session_state.translated_lines = translated_list
    else:
        st.error("가사를 입력해 주세요.")

if st.session_state.analyzed_data:
    data = st.session_state.analyzed_data
    df_counts = data['df_counts']
    
    # 결과 시각화 부분 (기존과 동일하므로 핵심 다운로드 로직으로 점프)
    st.markdown("### 📈 분석 결과 대시보드")
    top_20 = df_counts.head(20)
    fig = px.bar(top_20, x='단어', y='횟수', color='품사', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    # ... (퀴즈 로직 생략 - 이전 코드와 동일) ...
    # 편의상 여기서는 점수를 100점으로 가정하여 다운로드 영역을 보여줍니다.
    total_score = 100 

    st.divider()
    st.markdown("<h3 style='text-align:center;'>📥 결과 저장하기</h3>", unsafe_allow_html=True)
    
    # 버튼들을 한 줄에 배치
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if FPDF_AVAILABLE:
            pdf_bytes = create_pdf(data, total_score)
            st.download_button("📥 PDF 리포트", data=pdf_bytes, file_name="K-Lyric_Report.pdf", mime="application/pdf")
        else:
            st.info("PDF 라이브러리 미설치")

    with col2:
        txt_bytes = create_txt(data, total_score, st.session_state.translated_lines)
        st.download_button("📄 TXT 리포트", data=txt_bytes, file_name="K-Lyric_Report.txt", mime="text/plain")

    with col3:
        # PNG는 기술적 한계로 브라우저 캡처 가이드 제공
        st.markdown("""
            <div style="text-align:center;">
                <p style="font-size:0.8rem; color:#8b92b2;">📸 PNG 저장은 <b>Win+Shift+S</b> 또는 <b>Cmd+Shift+4</b>를 이용해 보세요!</p>
            </div>
        """, unsafe_allow_html=True)

    # 전체 페이지 스크린샷 팁
    st.markdown(f"""
        <div class="png-tip">
            <span style="color:#516df4; font-weight:800;">💡 PNG로 이 페이지를 통째로 간직하고 싶나요?</span><br>
            브라우저에서 <b>Ctrl + P</b> (인쇄)를 누른 뒤 'PDF로 저장'하거나, 캡처 도구로 대시보드 영역을 지정해 보세요!
        </div>
    """, unsafe_allow_html=True)