import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px  # 그래프를 위해 추가

# 페이지 설정
st.set_page_config(page_title="K-Pop 가사 분석기", layout="wide", page_icon="🎵")

# 형태소 분석기 및 번역기 초기화
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 메인 영역 ---
st.title("🎵 K-Pop 가사 분석 & 스마트 사전")
st.write("가사를 분석하고 단어의 빈도와 뜻을 바로 확인하세요.")

lyrics_input = st.text_area("노래 가사를 입력하세요:", height=200, placeholder="여기에 한국어 가사를 붙여넣으세요...")

if st.button("🚀 분석 및 번역 시작"):
    if lyrics_input.strip():
        # 1. 데이터 분석 로직
        morphs = okt.pos(lyrics_input, stem=True)
        
        all_words = []
        target_pos = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
        
        for word, pos in morphs:
            if pos in target_pos and len(word) > 1:
                all_words.append({'단어': word, '품사': target_pos[pos]})
        
        df_all = pd.DataFrame(all_words)

        # 레이아웃 나누기
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.subheader("🌍 가사 번역")
            try:
                translation = translator.translate(lyrics_input, dest='en')
                st.info(translation.text)
            except:
                st.error("번역 오류가 발생했습니다.")

        with col2:
            st.subheader("📊 주요 단어 분석 (클릭 시 사전 이동)")
            if not df_all.empty:
                # 중복 제거 및 빈도수 계산
                df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수')
                df_counts = df_counts.sort_values(by='횟수', ascending=False)

                # 하이퍼링크 URL 컬럼 추가
                df_counts['사전 확인'] = df_counts['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")

                # 하이퍼링크 적용하여 데이터프레임 표시
                st.data_editor(
                    df_counts,
                    column_config={
                        "사전 확인": st.column_config.LinkColumn(
                            "사전 링크",
                            help="클릭하면 네이버 사전으로 이동합니다",
                            validate="^https://.*",
                            display_text="사전 보기" # 링크 대신 '사전 보기'라는 글자로 표시
                        ),
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.write("분석할 단어가 없습니다.")

        # --- 3. 그래프 섹션 ---
        if not df_all.empty:
            st.divider()
            st.subheader("📈 단어 빈도수 TOP 10")
            
            # 상위 10개 단어 추출
            top_10 = df_counts.head(10)
            
            fig = px.bar(
                top_10, 
                x='단어', 
                y='횟수', 
                color='품사',
                text='횟수',
                title="가사에서 가장 많이 사용된 단어",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # --- 품사 가이드 (접이식) ---
        with st.expander("📚 한국어 품사 가이드 확인하기"):
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("명사", "이름", "사랑, 밤, 하늘")
            g2.metric("동사", "동작", "가다, 울다, 웃다")
            g3.metric("형용사", "상태", "예쁘다, 슬프다")
            g4.metric("부사", "꾸밈", "아주, 너무, 다시")

    else:
        st.warning("가사를 입력해 주세요.")

# 하단 안내
st.caption("Powered by Konlpy (Okt) & Google Translate")
