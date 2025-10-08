# 学習ヒストグラム（Streamlit）
学習項目の周回数をローカルJSONに保存し、棒グラフで可視化します。  
※ `.data/progress.json` は Git 管理外（公開されません）

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate  # Windowsは .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py

## 起動方法
streamlit run app.py