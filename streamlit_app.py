import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
try:
    import plotly.express as px
except Exception:
    px = None

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

lyrics_input = st.text_area("노래 가사를 입력하세요:", height=200, placeholder="여기에 한국어 가사를 붙여넣으세요...")

if st.button("🚀 분석 및 번역 시작"):
    if lyrics_input.strip():
        # 1. 데이터 분석 로직
        morphs = okt.pos(lyrics_input, stem=True)
        
        all_words = []
        # 분석할 타겟 품사 설정
        target_pos_map = {'Noun': '명사', 'Verb': '동사', 'Adjective': '형용사', 'Adverb': '부사'}
        
        for word, pos in morphs:
            # 2글자 이상인 주요 품사만 추출
            if pos in target_pos_map and len(word) > 1:
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
                except Exception:
                    st.error("번역 서버 연결에 실패했습니다.")

            with col2:
                st.subheader("📊 주요 단어 분석")
                df_display = df_counts.copy()
                df_display['사전'] = df_display['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")
                
                st.data_editor(
                    df_display,
                    column_config={"사전": st.column_config.LinkColumn("링크", display_text="보기")},
                    hide_index=True, use_container_width=True
                )

            # --- 2. 그래프 섹션 ---
            st.divider()
            st.subheader("📈 단어 빈도수 TOP 10")
            top_10 = df_counts.head(10)
            if px:
                fig = px.bar(top_10, x='단어', y='횟수', color='품사', text='횟수', barmode='group')
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("plotly가 설치되어 있지 않아 차트를 표시할 수 없습니다.")

            # --- 3. 상세 품사 가이드 (메시지가 뜨는 부분) ---
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
                        
                        # --- 여기서 빈도수 메시지 추출 ---
                        specific_pos_df = df_counts[df_counts['품사'] == name]
                        if not specific_pos_df.empty:
                            top_word = specific_pos_df.iloc[0]['단어']
                            count = specific_pos_df.iloc[0]['횟수']
                            # 메시지 박스 출력
                            st.success(f"✅ 이 가사의 대표 {name}: **'{top_word}'** (총 {count}회)")
                            st.caption(f"[👉 '{top_word}' 사전 뜻 풀이 보기](https://ko.dict.naver.com/#/search?query={top_word})")
                        else:
                            st.warning(f"ℹ️ 이 가사에는 2글자 이상의 '{name}'가 없습니다.")
        else:
            st.warning("분석할 수 있는 주요 단어가 없습니다. 더 긴 가사를 입력해 보세요!")
    else:
        st.error("가사를 입력해 주세요.")
import streamlit as st
from konlpy.tag import Okt
import pandas as pd
from googletrans import Translator
try:
    import plotly.express as px  # 그래프를 위해 추가
except Exception:
    px = None

# 페이지 설정
st.set_page_config(page_title="K-Pop 가사 분석기", layout="wide", page_icon="🎵")

# 형태소 분석기 및 번역기 초기화
@st.cache_resource
def get_resources():
    return Okt(), Translator()

okt, translator = get_resources()

# --- 메인 영역 ---
st.title("🎵 K-Pop 가사 분석 & 스마트 학습")
st.write("가사를 분석하고 단어의 의미와 한국어 문법을 함께 배워보세요.")

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
        # 빈도 DF 초기화 (단어가 없을 때 에러 방지)
        df_counts = pd.DataFrame(columns=['단어', '품사', '횟수'])

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
                df_counts = df_all.groupby(['단어', '품사']).size().reset_index(name='횟수')
                df_counts = df_counts.sort_values(by='횟수', ascending=False)
                df_counts['사전 확인'] = df_counts['단어'].apply(lambda x: f"https://ko.dict.naver.com/#/search?query={x}")

                st.data_editor(
                    df_counts,
                    column_config={
                        "사전 확인": st.column_config.LinkColumn(
                            "사전 링크",
                            help="클릭하면 네이버 사전으로 이동합니다",
                            validate="^https://.*",
                            display_text="사전 보기"
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
            top_10 = df_counts.head(10)
            if px:
                fig = px.bar(
                    top_10, x='단어', y='횟수', color='품사', text='횟수',
                    title="가사에서 가장 많이 사용된 단어",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("plotly가 설치되어 있지 않아 차트를 표시할 수 없습니다.")

        # --- 4. 상세 품사 개념 설명란 (추가된 부분) ---
        st.divider()
        st.subheader("📚 한국어 품사 백과사전")
        st.write("분석 결과에 나온 품사들의 정확한 개념을 확인해보세요.")

        m1, m2 = st.columns(2)

        with m1:
            with st.expander("📌 명사 (Noun) - 사물의 이름"):
                st.markdown("""
                **개념 설명:** 사람, 사물, 장소, 추상적인 개념 등에 붙여진 **이름**을 말합니다. 문장에서 주로 주체(누가)나 대상(무엇을)이 되는 핵심적인 역할을 합니다.  
                
                * **가사 속 역할:** 노래의 주제가 되는 대상(사랑, 이별, 너, 나, 밤하늘)을 구체적으로 지칭합니다.
                * **특징:** 뒤에 '은/는, 이/가, 을/를' 같은 조사가 붙어 문장에서의 자격이 결정됩니다.
                """)

            with st.expander("🏃 동사 (Verb) - 움직임과 동작"):
                st.markdown("""
                **개념 설명:** 사람이나 사물의 **주체적인 움직임이나 동작**을 나타내는 단어입니다.  
                
                * **가사 속 역할:** 주인공이 무엇을 하는지(가다, 울다, 기다리다, 잊다) 역동적인 상황을 설명합니다.
                * **특징:** 시간(과거/미래)에 따라 형태가 변합니다. (예: 가다 -> 갔다 / 울다 -> 울고 있다)
                """)

        with m2:
            with st.expander("✨ 형용사 (Adjective) - 성질과 상태"):
                st.markdown("""
                **개념 설명:** 사물의 **성질이나 상태, 느낌**을 나타내는 단어입니다. 동사와 비슷해 보이지만 '동작'이 아닌 '모습'을 묘사합니다.  
                
                * **가사 속 역할:** 분위기나 감정을 풍부하게 표현합니다. (예: 예쁘다, 슬프다, 그립다, 차갑다, 환하다)
                * **특징:** '지금 ~하는 중이다(-는 중)'라는 표현을 쓸 수 없습니다. (예: '슬픈 중이다' (X), '슬프다' (O))
                """)

            with st.expander("🎯 부사 (Adverb) - 상세한 수식"):
                st.markdown("""
                **개념 설명:** 주로 동사나 형용사 앞에서 그 뜻을 **더 세밀하고 풍부하게 꾸며주는** 역할을 합니다.  
                
                * **가사 속 역할:** 감정의 정도나 시간적 상황을 강조합니다. (예: **너무** 예쁘다, **문득** 생각나다, **영원히** 사랑해)
                * **특징:** 위치가 비교적 자유롭고, 문장의 느낌을 결정짓는 양념 같은 역할을 합니다.
                """)

    else:
        st.warning("가사를 입력해 주세요.")
