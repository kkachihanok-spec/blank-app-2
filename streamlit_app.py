# --- 커스텀 이중 폴딩 가이드 섹션 (모두 닫힘 버전) ---
        st.divider()
        
        if total_score >= 60:
            theme_color = "#516df4"  # 블루
            theme_bg = "rgba(81, 109, 244, 0.1)"
            advice_title = "[조언 1] 심화 학습 가이드"
            advice_text = "이미 훌륭한 실력을 갖추고 계시네요! 이제 가사의 <b>'은유적 표현'</b>이나 <b>'신조어'</b>에 주목해 보세요. 한국의 문학 작품이나 에세이를 병행하면 표현의 깊이가 달라질 거예요."
            ref_title = "[조언 2] 심화 학습 레퍼런스"
        else:
            theme_color = "#AF40FF"  # 퍼플
            theme_bg = "rgba(175, 64, 255, 0.1)"
            advice_title = "[조언 1] 기초 학습 가이드"
            advice_text = "조급해하지 마세요! 가사 속의 <b>'명사'</b>부터 하나씩 수집해 보는 건 어떨까요? 좋아하는 가수의 인터뷰 영상을 자막과 함께 보며 발음을 익히는 것부터 시작해 보세요."
            ref_title = "[조언 2] 기초 학습 레퍼런스"

        st.markdown(f"""
            <style>
                .custom-details {{
                    background: {theme_bg}; border: 1px solid {theme_color}44;
                    border-radius: 12px; overflow: hidden; margin-bottom: 15px; transition: all 0.3s ease;
                }}
                .custom-details[open] {{ border: 1px solid {theme_color}; box-shadow: 0 5px 15px {theme_color}22; }}
                .custom-summary {{
                    padding: 16px 20px; font-size: 1.1rem; font-weight: 800; color: #FFFFFF !important;
                    cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center;
                }}
                .custom-summary:hover {{ background: {theme_color}11; }}
                .custom-summary::after {{ content: '▼'; color: {theme_color}; font-size: 0.7rem; transition: transform 0.3s; }}
                .custom-details[open] .custom-summary::after {{ transform: rotate(180deg); }}
                
                .guide-content {{ padding: 0 25px 20px 25px; animation: fadeIn 0.4s ease; }}
                
                .guide-text {{ 
                    color: #FFFFFF; 
                    line-height: 1.7; 
                    font-size: 1.05rem !important; 
                    margin-top: 10px; 
                }}
                
                @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                
                .guide-link-card-custom {{
                    background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; 
                    text-align: center; color: #8b92b2 !important; border: 1px solid rgba(255,255,255,0.1);
                    text-decoration: none; display: block; transition: all 0.2s; font-size: 0.85rem !important;
                }}
                .guide-link-card-custom:hover {{ background: {theme_bg}; border-color: {theme_color}; color: white !important; }}
            </style>

            <details class="custom-details">
                <summary class="custom-summary"><span>{advice_title}</span></summary>
                <div class="guide-content">
                    <p class="guide-text">{advice_text}</p>
                </div>
            </details>

            <details class="custom-details">
                <summary class="custom-summary"><span>{ref_title}</span></summary>
                <div class="guide-content">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px;">
                        <a href="https://dict.naver.com" target="_blank" class="guide-link-card-custom">🟢 네이버 국어사전</a>
                        <a href="https://www.topik.go.kr" target="_blank" class="guide-link-card-custom">🎓 TOPIK 공식 홈페이지</a>
                        <a href="https://www.sejonghakdang.org" target="_blank" class="guide-link-card-custom">🏫 세종학당재단</a>
                        <a href="https://vlive.tv" target="_blank" class="guide-link-card-custom">📺 K-Contents 학습</a>
                    </div>
                </div>
            </details>
            <div style="margin-bottom: 50px;"></div>
        """, unsafe_allow_html=True)