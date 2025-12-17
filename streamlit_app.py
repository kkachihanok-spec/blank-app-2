import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="K-Pop 가사 분석기", layout="wide", page_icon="🎵")

# 형태소 분석기 및 번역기 초기화
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 메인 영역 ---
st.title("🎵 K-Pop 가사 분석 & 맞춤형 학습")
st.write("가사를 분석하고, 가장 많이 나온 단어로 한국어 품사를 배워보세요.")

# 가사 입력 창 (파일 전체에서 단 하나만 존재해야 합니다)
lyrics_input = st.text_area("노래 가사를 입력하세요:", height=200, placeholder="여기에 한국어 가사를 붙여넣으세요...", key="lyrics_main")

if st.button("🚀 분석 및 번역 시작", key="analyze_btn"):
    if lyrics_input.strip():
        # 1. 데이터 분석 로직
        morphs = okt.pos(lyrics_input, stem=True)
        
        all_words = []
        # 분석할 타겟 품사 설정
        target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
        
        for word, pos in morphs:
            # 한 글자 단어도 포함하도록 len(word) >= 1로 수정
            if pos in target_pos_map and len(word) >= 1:
                all_words.append({'단어': word, '품사': target_pos_map[pos]})
        
        df_all = pd.DataFrame(all_words)

        # 분석 결과가 있는 경우에만 실행
        if not df_all.empty:
            # 중복 제거 및 빈도수 계산
            df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수')
            df_counts = df_counts.sort_values(by='횟수', ascending=False)

            # 레이아웃 나누기 (상단: 번역과 표)
            col1, col2 = st.columns([1, 1.2])

            with col1:
                st.subheader("🌍 가사 번역 (English)")
                try:
                    translation = translator.translate(lyrics_input, dest='en')
                    st.info(translation.text)
                except:
                    st.error("번역 서버 연결에 실패했습니다.")

            with col2:
                st.subheader("📊 주요 단어 분석")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                
                st.data_editor(
                    df_display,
                    column_config={"사전": st.column_config.LinkColumn("링크", display_text="보기")},
                    hide_index=True, use_container_width=True, key="editor_main"
                )

            # --- 2. 그래프 섹션 ---
            st.divider()
            st.subheader("📈 단어 빈도수 TOP 10")
            top_10 = df_counts.head(10)
            fig = px.bar(top_10, x='단어', y='횟수', color='품사', text='횟수')
            st.plotly_chart(fig, use_container_width=True)

            # --- 3. 상세 품사 가이드 ---
            st.divider()
            st.subheader("📚 가사 속 단어로 배우는 품사")
            
            m1, m2 = st.columns(2)
            pos_info = {
                "명사": {"icon": "📌", "desc": "사람, 사물, 장소의 이름입니다.", "role": "가사의 주제(대상)를 나타냅니다."},
                "동사": {"icon": "🏃", "desc": "주체의 움직임이나 동작입니다.", "role": "주인공이 무엇을 하는지 행동을 설명합니다."},
                "형용사": {"icon": "✨", "desc": "성질이나 상태, 느낌을 나타냅니다.", "role": "가사의 감정이나 분위기를 풍부하게 합니다."},
                "부사": {"icon": "🎯", "desc": "뜻을 세밀하게 꾸며주는 양념 역할입니다.", "role": "감정의 정도나 상황을 강조합니다."}
            }

            for i, (name, info) in enumerate(pos_info.items()):
                target_col = m1 if i < 2 else m2
                with target_col:
                    with st.expander(f"{info['icon']} {name} 설명 보기", expanded=True):
                        st.markdown(f"**개념:** {info['desc']}")
                        st.markdown(f"**역할:** {info['role']}")
                        
                        # 특정 품사 데이터만 필터링
                        spec_df = df_counts[df_counts['품사'] == name]
                        if not spec_df.empty:
                            top_word = spec_df.iloc[0]['단어']
                            count = spec_df.iloc[0]['횟수']
                            st.success(f"✅ 이 가사의 대표 {name}: **'{top_word}'** (총 {count}회)")
                            st.caption(f"[👉 '{top_word}' 사전 뜻 풀이 보기](https://ko.dict.naver.com/#/search?query={top_word})")
                        else:
                            st.warning(f"ℹ️ 이 가사에는 '{name}' 품사가 없습니다.")
        else:
            st.warning("분석할 수 있는 단어가 없습니다.")
    else:
        st.error("가사를 입력해 주세요.")
git add streamlit_app.py
git commit -m "feat: K-Pop Lyric Insight: UI 개선, CSS 추가, 대시보드 및 번역 기능 강화"