import csv
import os
import requests
from bs4 import BeautifulSoup, NavigableString
from lxml import etree
import pykakasi
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../data/seitei_goroku_entries.csv')
URL = "https://w.atwiki.jp/seitei/pages/12.html"

NOISE_PATTERNS = [
    r"^(新規作成|編集|ページ一覧|タグ|ヘルプ|目次|ページ検索|ログイン|RSS|管理メニュー)$",
    r"^(最終更新|更新履歴|アクセスカウンター|最近更新されたページ|今日.*昨日.*合計)$",
    r"^(このページを|コメント|メニュー|サイドバー|メニューバー|フロントページ)$",
    r"^(広告|スポンサー|Image|クリックすると開きます)$",
    r"^[ぁ-ん]行$",
    r"^[ァ-ヶ]行$",
    r"^(その他|未分類|記号)$",
]
NOISE_RE = re.compile("|".join(NOISE_PATTERNS))

def normalize_line(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\t", " ").replace("\r", "")
    return s

def want_keep(s: str) -> bool:
    if not s:
        return False
    if NOISE_RE.search(s):
        return False
    if len(s) < 2 or len(s) > 120:
        return False
    return True

CSS_TARGET = "div#wikibody.atwiki-contents table.atwiki_plugin_region div.plugin_contents"
XPATH_TARGET = "/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr/td[3]/div"

def extract_entries(html: str) -> list:
    soup = BeautifulSoup(html, "lxml")
    body = soup.select_one(CSS_TARGET)
    if body is None:
        try:
            parser = etree.HTMLParser()
            root = etree.fromstring(html.encode("utf-8"), parser=parser)
            xpath_nodes = root.xpath(XPATH_TARGET)
        except (etree.XMLSyntaxError, etree.XPathEvalError):
            xpath_nodes = []
        if xpath_nodes:
            fragment_html = etree.tostring(xpath_nodes[0], encoding="unicode")
            body = BeautifulSoup(fragment_html, "lxml")
    if body is None:
        body = soup.select_one("div#wikibody")
        if body is None:
            return []
    def li_direct_text(li) -> str:
        parts = []
        for child in li.children:
            if isinstance(child, NavigableString):
                s = str(child).strip()
                if s:
                    parts.append(s)
            else:
                name = getattr(child, "name", None)
                if name in ("ul", "ol"):
                    continue
                if name is not None:
                    s = child.get_text(" ", strip=True)
                    if s:
                        parts.append(s)
        if not parts:
            return ""
        return normalize_line(" ".join(parts))
    texts = []
    for el in body.select("li, p"):
        if el.name == "li":
            raw = li_direct_text(el)
        else:
            raw = el.get_text(separator=" ", strip=True)
        t = normalize_line(raw)
        if want_keep(t):
            texts.append(t)
    seen = set()
    uniq = []
    for t in texts:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq

def add_yomi(entries):
    kks = pykakasi.kakasi()
    alphabet_map = {
        'a': 'えー', 'b': 'びー', 'c': 'しー', 'd': 'でぃー', 'e': 'いー', 'f': 'えふ', 'g': 'じー', 'h': 'えいち', 'i': 'あい', 'j': 'じぇい', 'k': 'けー', 'l': 'える', 'm': 'えむ', 'n': 'えぬ', 'o': 'おー', 'p': 'ぴー', 'q': 'きゅー', 'r': 'あーる', 's': 'えす', 't': 'てぃー', 'u': 'ゆー', 'v': 'ぶい', 'w': 'だぶりゅー', 'x': 'えっくす', 'y': 'わい', 'z': 'ぜっと',
        'A': 'えー', 'B': 'びー', 'C': 'しー', 'D': 'でぃー', 'E': 'いー', 'F': 'えふ', 'G': 'じー', 'H': 'えいち', 'I': 'あい', 'J': 'じぇい', 'K': 'けー', 'L': 'える', 'M': 'えむ', 'N': 'えぬ', 'O': 'おー', 'P': 'ぴー', 'Q': 'きゅー', 'R': 'あーる', 'S': 'えす', 'T': 'てぃー', 'U': 'ゆー', 'V': 'ぶい', 'W': 'だぶりゅー', 'X': 'えっくす', 'Y': 'わい', 'Z': 'ぜっと',
        '0': 'ぜろ', '1': 'いち', '2': 'に', '3': 'さん', '4': 'よん', '5': 'ご', '6': 'ろく', '7': 'なな', '8': 'はち', '9': 'きゅう'
    }
    hira_and_eisu = re.compile(r'[^ぁ-んa-zA-Z0-9]+')
    def convert_eisu_to_hira(s):
        return ''.join(alphabet_map.get(ch, ch) if ch.isalnum() else '' for ch in s)
    result = []
    for text in entries:
        yomi = ''.join([item['hira'] for item in kks.convert(text)])
        yomi = hira_and_eisu.sub('', yomi)
        yomi = convert_eisu_to_hira(yomi)
        result.append((text, yomi))
    return result

# --- CSV出力 ---
def write_csv(path, entries):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for entry, yomi in entries:
            writer.writerow([entry, yomi])
    print(f"[CSV生成] 聖帝語録CSV: {path} ({len(entries)} 行)")

def main():
    try:
        r = requests.get(URL, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"[error] Failed to fetch wiki page from {URL}: {e}")
        return 1
    wiki_entries = extract_entries(r.text)
    if not wiki_entries:
        print("[warn] no entries extracted")
        return 1

    csv_entries = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    csv_entries[row[0]] = row[1]
                elif len(row) == 1:
                    csv_entries[row[0]] = ''

    wiki_set = set(wiki_entries)
    csv_set = set(csv_entries.keys())

    added = [entry for entry in wiki_entries if entry not in csv_set]
    added_with_yomi = add_yomi(added)
    kept = [(entry, csv_entries[entry]) for entry in wiki_entries if entry in csv_set]
    new_entries = kept + added_with_yomi
    write_csv(CSV_PATH, new_entries)
    return 0

if __name__ == "__main__":
    main()
