# seitei-ime-dict

聖帝語録（[w.atwiki](https://w.atwiki.jp/seitei/pages/12.html)）から語録を収集し、主要な日本語IME向けの辞書ファイルを自動生成するプロジェクトです。収録語句は `data/seitei_goroku_entries.csv` がソースになっており、スクリプトで辞書を再生成できます。

## 収録ファイル

| IME | 出力ファイル | 文字コード / 形式 |
| --- | --- | --- |
| ATOK | `dictionaries/seitei_goroku_atok.txt` | UTF-16 / テキスト |
| Google日本語入力 | `dictionaries/seitei_goroku_google_ime.txt` | UTF-8 / テキスト |
| Gboard | `dictionaries/seitei_goroku_gboard.txt` | UTF-8 / タブ区切り |
| Microsoft IME | `dictionaries/seitei_goroku_microsoft_ime.txt` | UTF-16 / テキスト |
| macOS IME | `dictionaries/seitei_goroku_mac_ime.csv` | UTF-8 / CSV |

辞書ファイルをそのままインポートして使うことも、次章の手順で新しい語句を含めて再生成することもできます。

## 使い方

### 環境準備

- Python 3.10 以上を推奨
- 必要なライブラリ（`requests`, `beautifulsoup4`, `lxml`, `pykakasi` など）をインストールしてください

```bash
python -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 lxml pykakasi
```

### 1. 語録CSVの更新

`scripts/wiki_page_to_entries.py` が wiki から語録を取得し、`data/seitei_goroku_entries.csv` に保存します。既存CSVにない語句は自動で読み仮名を推定します。

```bash
python scripts/wiki_page_to_entries.py
```

### 2. IME辞書の再生成

最新の CSV を基に各 IME 用辞書ファイルを作り直します。

```bash
python scripts/entries_to_ime_dicts.py
```

### 3. 差分サマリ（任意）

リリースノート向けに前後の CSV 差分を Markdown として整形したい場合は `scripts/csv_diff_summary.py` を使います。

```bash
python scripts/csv_diff_summary.py data/old_entries.csv data/seitei_goroku_entries.csv
```

## 開発メモ

- `data/seitei_goroku_entries.csv` が語録の基準データです。直接編集する場合は、後で辞書生成スクリプトを再実行してください。
- 読みの自動生成は完全ではないため、不自然な読みがあれば CSV を手動で調整してください。
- Google日本語入力と Gboard で動作確認済み。他IMEでの検証結果があれば Issue や Pull Request で共有いただけると助かります。

## クレジット

- 元データ: [聖帝語録 @ w.atwiki](https://w.atwiki.jp/seitei/pages/12.html)
- このリポジトリは有志による非公式ファンプロジェクトです。
