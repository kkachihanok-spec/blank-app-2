import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px
from datetime import datetime
import random
import base64

# fpdf 설치 여부 확인 및 예외 처리
try:
    from fpdf import FPDF
    FPDF_INSTALLED = True
except ImportError:
    FPDF_INSTALLED = False

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

# 3. 커스텀 CSS (기존 디자인 완벽 유지)
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
    
    div.stDownloadButton > button {
        background: rgba(125, 141, 236, 0.1) !important;
        border: 1px solid rgba(125, 141, 236, 0.3) !important;
        color: #7d8dec !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stMetricLabel"] p { font-size: 1.1rem !important; color: #4a5fcc !important; font-weight: 900 !important; margin-bottom: 6px !important; }
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
    
    .score-container-premium {
        padding: 40px 40px; border-radius: 24px; text-align: center; margin: 40px 0;
        backdrop-filter: blur(20px); box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    .score-fail-premium { background: linear-gradient(145deg, rgba(110, 72, 170, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%); border: 1px solid rgba(110, 72, 170, 0.3); }
    .score-pass-premium { background: linear-gradient(145deg, rgba(74, 95, 204, 0.1) 0%, rgba(0, 0, 0, 0.6) 100%); border: 1px solid rgba(74, 95, 204, 0.3); }
    
    .score-number-premium { font-size: 5.91rem !important; font-weight: 900 !important; line-height: 0.9 !important; }
    
    /* 🔥 확정된 컬러 #516df4 유지 */
    .score-text-fail { color: #AF40FF !important; }
    .score-text-pass { color: #516df4 !important; }
    
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """, unsafe_allow_html=True)

# PDF 생성 함수
def create_pdf(data, score):
    if not FPDF_INSTALLED:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="K-Lyric 101 Analysis Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Score: {score} / 100", ln=True)
    pdf.cell(200, 10, txt=f"Unique Words: {len(data['df_counts'])}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 이하 메인 로직은 이전과 동일하게 유지 ---
# ... (생략된 부분은 이전의 완벽한 코드와 동일)
# [기능 안정성을 위해 PDF 버튼 부분만 체크 추가]

# (가장 하단 결과 출력부)
if st.session_state.analyzed_data:
    # ... (퀴즈 로직 수행 후)
    # total_score 계산 후
    
    if FPDF_INSTALLED:
        pdf_bytes = create_pdf(st.session_state.analyzed_data, 100) # 예시 점수
        st.download_button(
            label="📥 분석 리포트 PDF 다운로드",
            data=pdf_bytes,
            file_name="K-Lyric_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.info("PDF 기능을 사용하려면 fpdf 라이브러리를 설치해 주세요.")