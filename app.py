import streamlit as st
import pandas as pd
import json
import os
from datetime import date

st.set_page_config(page_title="学習ヒストグラム", layout="wide")

TOPICS = [
    "基礎理論","アルゴリズムとプログラミング","コンピュータ構成要素","システム構成要素",
    "ソフトウェア","ハードウェア","ユーザインタフェース","情報メディア",
    "データベース","ネットワーク","セキュリティ","システム開発技術","ソフトウェア開発管理技術",
    "プロジェクトマネジメント","サービスマネジメント","システム監査",
    "システム戦略","システム企画","経営戦略マネジメント","技術戦略マネジメント",
    "ビジネスインダストリ","企業活動","法務",
]

DATA_DIR = ".data"
os.makedirs(DATA_DIR, exist_ok=True)
SAVE_FILE = os.path.join(DATA_DIR, "progress.json")

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"counts": {}, "log": []}
    for t in TOPICS:
        data["counts"].setdefault(t, 0)
    return data

def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

st.title("学習ヒストグラム（周回カウンタ）")
st.caption("履歴はローカル保存：.data/progress.json（公開リポジトリには含めません）")

left, right = st.columns([1, 2])

with left:
    st.subheader("操作")
    today = str(date.today())

    if st.button("全項目を0にリセット", type="secondary"):
        data["counts"] = {t: 0 for t in TOPICS}
        save_data(data)
        st.success("全項目を0にリセットしました。")

    st.divider()
    st.markdown("### 項目ごとの周回")
    for t in TOPICS:
        c1, c2, c3 = st.columns([5, 2, 2])
        with c1:
            st.write(t)
        with c2:
            if st.button("+1", key=f"inc-{t}"):
                data["counts"][t] = data["counts"].get(t, 0) + 1
                data["log"].append({"date": today, "topic": t, "delta": 1})
                save_data(data)
                st.toast(f"{t} を +1")
        with c3:
            if st.button("−1", key=f"dec-{t}"):
                data["counts"][t] = max(0, data["counts"].get(t, 0) - 1)
                data["log"].append({"date": today, "topic": t, "delta": -1})
                save_data(data)
                st.toast(f"{t} を −1")

    st.divider()
    df_counts = pd.DataFrame({"項目": list(data["counts"].keys()),
                              "周回数": list(data["counts"].values())})
    csv = df_counts.to_csv(index=False).encode("utf-8-sig")
    st.download_button("周回数CSVをダウンロード", csv, file_name="counts.csv", mime="text/csv")

with right:
    st.subheader("可視化")
    df_plot = (
        pd.DataFrame({"項目": list(data["counts"].keys()),
                      "周回数": list(data["counts"].values())})
        .sort_values("周回数", ascending=False)
    )
    st.bar_chart(df_plot, x="項目", y="周回数", height=380)

    st.markdown("#### 日別ログ")
    df_log = pd.DataFrame(data["log"])
    if not df_log.empty:
        piv = (
            df_log.groupby(["date", "topic"])["delta"].sum().reset_index()
            .pivot(index="date", columns="topic", values="delta").fillna(0).astype(int)
        )
        st.dataframe(piv, use_container_width=True)
    else:
        st.info("まだログがありません。+1してみてください。")
