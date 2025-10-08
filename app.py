from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
from datetime import date

import streamlit as st

# -------------------- 基本 --------------------
st.set_page_config(page_title="学習ヒストグラム", layout="wide")

REPO_DIR = Path(__file__).resolve().parent
SAVE_FILE = REPO_DIR / "progress.json"

TOPICS: List[str] = [
    "基礎理論", "アルゴリズムとプログラミング", "コンピュータ構成要素", "システム構成要素",
    "ソフトウェア", "ハードウェア", "ユーザインタフェース", "情報メディア",
    "データベース", "ネットワーク", "セキュリティ", "システム開発技術", "ソフトウェア開発管理技術",
    "プロジェクトマネジメント", "サービスマネジメント", "システム監査",
    "システム戦略", "システム企画", "経営戦略マネジメント", "技術戦略マネジメント",
    "ビジネスインダストリ", "企業活動", "法務",
]

PALETTE = [
    "#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4", "#84CC16", "#EC4899",
    "#F97316", "#22C55E", "#0EA5E9", "#A855F7", "#D946EF", "#F43F5E", "#14B8A6", "#EAB308",
    "#6366F1", "#059669", "#EA580C", "#0891B2", "#7C3AED", "#65A30D", "#DB2777", "#3B82F6",
]
COLOR = {t: PALETTE[i % len(PALETTE)] for i, t in enumerate(TOPICS)}

# -------------------- スタイル --------------------
st.markdown(
    """
<style>
  /* 余白最適化 */
  .block-container{padding-top:2.2rem; padding-bottom:1.0rem;}
  :root{ --bg:#fff; --ink:#0f172a; --muted:#64748b; --card:#f8fbff; --border:#e2e8f0;}
  .stApp{background:var(--bg); color:var(--ink);}
  .stButton>button{background:#2563EB !important; color:#fff !important; border-radius:10px !important; padding:.45rem .9rem !important;}

  /* ---- 横並びの縦バー（||||） ---- */
  .hbars{
    display:flex;
    flex-wrap:wrap;
    gap:12px;                 /* 隣の柱との間隔 */
    align-items:flex-end;     /* ★ 全ての柱の下端を揃える */
    border:1px solid var(--border);
    background:#FFFFFF;
    border-radius:12px;
    padding:12px 14px;
  }
  .col{
    width:36px;               /* 柱の太さ */
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:flex-end; /* ★ 下方向に詰めて高さ差を吸収 */
  }
  .tube{
    position:relative;
    width:100%;
    height:200px;             /* 最大高さ */
    background:#edf2f7;
    border-radius:12px;
    overflow:hidden;
  }
  .bar{
    position:absolute; bottom:0; left:0;
    width:100%; height:0%;
    border-radius:12px;
    transition:height .25s ease;
  }
  /* ★ 数値とラベルで列の高さが変わらないよう固定高＋1行表示にする */
  .cnt{font-size:.78rem; color:var(--muted); margin-top:6px; line-height:1; height:16px; display:flex; align-items:center; justify-content:center;}
  .lbl{font-size:.74rem; color:#475569; line-height:1; height:14px; margin-top:2px; text-align:center;
       white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
  .kpi{border:1px solid var(--border); background:var(--card); padding:.55rem .75rem; border-radius:10px; font-size:.95rem; margin-top:.7rem;}

  @media (max-width: 560px){
    .col{width:32px}
    .tube{height:180px}
  }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------- データI/O --------------------
def _empty() -> Dict:
    return {"counts": {t: 0 for t in TOPICS}, "log": []}

def load() -> Dict:
    if not SAVE_FILE.exists():
        d = _empty()
        SAVE_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        return d
    try:
        txt = SAVE_FILE.read_text(encoding="utf-8").strip()
        d = json.loads(txt) if txt else _empty()
    except json.JSONDecodeError:
        d = _empty()
    d.setdefault("counts", {})
    for t in TOPICS:
        d["counts"].setdefault(t, 0)
    d.setdefault("log", [])
    SAVE_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return d

def save(d: Dict) -> None:
    SAVE_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def add_rounds(d: Dict, topic: str, rounds: int, when: date) -> None:
    if rounds == 0:
        return
    d["counts"][topic] = max(0, int(d["counts"].get(topic, 0)) + int(rounds))
    d["log"].append({"date": when.isoformat(), "topic": topic, "delta": int(rounds)})
    save(d)

# -------------------- 短縮ラベル --------------------
def make_short_labels(topics: List[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    used: set[str] = set()
    for t in topics:
        for n in (3, 4, 2):
            cand = t[:n]
            if cand and cand not in used:
                result[t] = cand
                used.add(cand)
                break
        else:
            base = t[:3] if len(t) >= 3 else t
            idx = 2
            cand = f"{base}{idx}"
            while cand in used:
                idx += 1
                cand = f"{base}{idx}"
            result[t] = cand
            used.add(cand)
    return result

SHORT = make_short_labels(TOPICS)

# -------------------- 入力 --------------------
st.title("学習ヒストグラム")
d = load()

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    t_sel = st.selectbox("単元", TOPICS)
with c2:
    n_sel = st.number_input("周回数（+/-）", value=1, step=1)
with c3:
    day_sel = st.date_input("日付", value=date.today())
with c4:
    st.write("")
    if st.button("記録", use_container_width=True):
        add_rounds(d, t_sel, int(n_sel), day_sel)
        st.success(f"{t_sel} に {int(n_sel):+} 周を記録")

# -------------------- サイドバー：バックアップのみ --------------------
with st.sidebar:
    st.header("バックアップ")
    dl = json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8-sig")
    st.download_button("JSONを保存", dl, file_name="progress-backup.json", use_container_width=True)
    up = st.file_uploader("JSONインポート", type=["json"])
    if up is not None:
        try:
            raw = up.read()
            imp = json.loads(raw.decode("utf-8-sig"))
        except Exception as e:
            st.error(f"JSONの読み込みに失敗: {e}")
        else:
            if not isinstance(imp, dict):
                st.error("不正なJSONです（ルートがオブジェクトではありません）。")
            else:
                counts = imp.get("counts", {})
                if not isinstance(counts, dict):
                    counts = {}
                for t in TOPICS:
                    counts.setdefault(t, 0)
                imp["counts"] = counts
                imp.setdefault("log", [])
                d = imp
                save(d)
                st.success("インポート完了。画面を再読み込みしてください。")

# -------------------- 可視化：|||| の横並び（ラベルずれ補正済み） --------------------
st.markdown("#### 進捗ボード")

# 表示はリニア固定。非ゼロ棒の最小高さだけ与える。
MIN_NONZERO_PCT = 15  # %

max_count = max(1, int(max(d["counts"].values())))  # 0除算回避

parts: List[str] = ["<div class='hbars'>"]
for t in TOPICS:
    v = int(d["counts"].get(t, 0))
    if v <= 0:
        pct = 0
    else:
        pct = v / max_count * 100.0
        pct = max(pct, float(MIN_NONZERO_PCT))  # 非ゼロの下限

    color = COLOR[t]
    short = SHORT[t]
    parts.append(
        f"<div class='col' title='{t}'>"
        f"<div class='tube'><div class='bar' style='height:{pct}%; background:{color};'></div></div>"
        f"<div class='cnt'>{v}</div>"
        f"<div class='lbl'>{short}</div>"
        f"</div>"
    )
parts.append("</div>")
st.markdown("".join(parts), unsafe_allow_html=True)

# KPI（合計のみ）
total = int(sum(d["counts"].values()))
st.markdown(f"<div class='kpi'>累積合計：<b>{total}</b> 周</div>", unsafe_allow_html=True)
