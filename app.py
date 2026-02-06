import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------
# 1. アプリの設定
# ---------------------------------------------------------
st.set_page_config(
    page_title="AdCheck AI",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------------
# 2. APIキーの準備 (Secretsから読み込み)
# ---------------------------------------------------------
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ APIキーが設定されていません。StreamlitのSettings > Secretsで設定してください。")
    st.stop()

# モデルの定義
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------------------------------------------------
# 3. 画面のデザイン (サイドバー：履歴)
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("⏳ 履歴")
    if not st.session_state.history:
        st.caption("履歴はまだありません")
    
    # 履歴を新しい順に表示
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item['platform']} ({item['time']})"):
            st.caption(item['query'][:40] + "...")
            st.write(f"判定: {item['verdict']}")

# ---------------------------------------------------------
# 4. メイン画面
# ---------------------------------------------------------
# ヘッダーエリア
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=60) # アイコン例
with col2:
    st.title("AdCheck AI")
    st.caption("Web広告フィジビリ確認ツール Powered by Gemini")

st.markdown("---")

# 入力フォームエリア
st.subheader("1. 媒体を選択")
selected_platform = st.selectbox(
    "確認したい媒体を選んでください",
    ["Google 広告", "Yahoo!広告", "Meta (Facebook/Instagram)", "TikTok Ads", "LINE Ads", "X (Twitter) Ads"],
    index=1
)

st.subheader("2. 確認したい内容")
query = st.text_area(
    "質問内容を入力",
    height=150,
    placeholder="例：Yahooディスプレイ広告で、画像内のテキスト占有率に20%の制限はありますか？"
)

# 注意書き（以前エラーになっていた部分を修正済み）
st.caption("※AIは公式ヘルプページ等の知識を基に回答しますが、最終的な判断は各媒体の公式ドキュメントを直接ご確認ください。")

# ---------------------------------------------------------
# 5. 実行ロジック
# ---------------------------------------------------------
if st.button("判定する", type="primary", use_container_width=True):
    if not query:
        st.warning("質問内容を入力してください。")
    else:
        with st.spinner(f"{selected_platform} の情報を確認中..."):
            try:
                # Geminiへのプロンプト作成
                prompt = f"""
                あなたはWeb広告運用のプロフェッショナルです。
                以下の媒体に関する質問に対して、入稿規定やポリシーに基づき回答してください。

                ■対象媒体: {selected_platform}
                ■質問: {query}

                回答は以下のフォーマットで出力してください：
                1. **判定**: (OK / NG / 条件付きOK / 要確認 のいずれか)
                2. **解説**: 簡潔な要約
                3. **詳細**: 理由や規定の背景
                """

                # AIからの回答を取得
                response = model.generate_content(prompt)
                result_text = response.text

                # 履歴に保存するための簡易判定ロジック
                verdict = "回答あり"
                if "NG" in result_text: verdict = "NG"
                elif "OK" in result_text: verdict = "OK"
                elif "条件付き" in result_text: verdict = "条件付き"

                # 履歴に追加
                import datetime
                st.session_state.history.append({
                    "platform": selected_platform,
                    "query": query,
                    "verdict": verdict,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })

                # 結果表示エリア
                st.markdown("### 📊 判定結果")
                
                # 結果の内容によって色を変える
                if "NG" in result_text:
                    st.error(result_text)
                elif "条件付き" in result_text:
                    st.warning(result_text)
                else:
                    st.success(result_text)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# ---------------------------------------------------------
# 6. 使い方のヒント（データがない時だけ表示）
# ---------------------------------------------------------
if not query:
    st.markdown("---")
    st.markdown("#### 💡 こんなことが確認できます")
    cols = st.columns(3)
    with cols[0]:
        st.info("**公式情報の確認**\n\n「バナーサイズの上限は？」など基本仕様の確認")
    with cols[1]:
        st.warning("**入稿規定チェック**\n\n「" + "最上級表現" + "は使えますか？」などのポリシー確認")
    with cols[2]:
        st.success("**判定の明確化**\n\nOKかNGか、条件付きかをAIが判断して回答")
