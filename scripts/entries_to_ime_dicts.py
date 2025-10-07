import csv
import os

def generate_atok_dictionary(csv_path, atok_path, default_pos="名詞", add_header=True):
    lines = []
    if add_header:
        lines.append("!!ATOK_TANGO_TEXT_HEADER_1\n")
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                yomi = row[1].strip()
                word = row[0].strip()
                lines.append(f"{yomi}\t{word}\t{default_pos}\n")
    with open(atok_path, 'w', encoding='utf-16') as f:
        f.writelines(lines)
    print(f"[IME生成] ATOK: {atok_path}")

def generate_gboard_dictionary(csv_path, gboard_path, locale="ja-JP", add_header=True):
    lines = []
    if add_header:
        lines.append("# Gboard Dictionary version:1\n")
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                yomi = row[1].strip()
                word = row[0].strip()
                lines.append(f"{yomi}\t{word}\t{locale}\n")
    with open(gboard_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"[IME生成] Gboard: {gboard_path}")

def generate_google_ime_dictionary(csv_path, google_ime_path, default_pos="名詞"):
    lines = []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                yomi = row[1].strip()
                word = row[0].strip()
                lines.append(f"{yomi}\t{word}\t{default_pos}\n")
    with open(google_ime_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"[IME生成] Google日本語入力: {google_ime_path}")

def generate_microsoft_ime_dictionary(csv_path, ime_path, default_pos="名詞", add_header=True):
    lines = []
    if add_header:
        lines.append("!Microsoft IME Dictionary Tool\n!Format: TEXT\n")
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                yomi = row[1].strip()
                word = row[0].strip()
                lines.append(f"{yomi}\t{word}\t{default_pos}\n")
    with open(ime_path, 'w', encoding='utf-16') as f:
        f.writelines(lines)
    print(f"[IME生成] Microsoft IME: {ime_path}")

def generate_mac_ime_dictionary(csv_path, mac_ime_path, default_pos="普通名詞"):
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            if len(row) >= 2:
                yomi = row[1].strip()
                word = row[0].strip()
                pos = default_pos
                rows.append([yomi, word, pos])
    with open(mac_ime_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
    print(f"[IME生成] macOS IME: {mac_ime_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, '../data/seitei_goroku_entries.csv')
    ATOK_PATH = os.path.join(BASE_DIR, '../dictionaries/seitei_goroku_atok.txt')
    GBOARD_PATH = os.path.join(BASE_DIR, '../dictionaries/seitei_goroku_gboard.txt')
    GOOGLE_IME_PATH = os.path.join(BASE_DIR, '../dictionaries/seitei_goroku_google_ime.txt')
    IME_PATH = os.path.join(BASE_DIR, '../dictionaries/seitei_goroku_microsoft_ime.txt')
    MAC_IME_PATH = os.path.join(BASE_DIR, '../dictionaries/seitei_goroku_mac_ime.csv')

    generate_atok_dictionary(CSV_PATH, ATOK_PATH)
    generate_gboard_dictionary(CSV_PATH, GBOARD_PATH)
    generate_google_ime_dictionary(CSV_PATH, GOOGLE_IME_PATH)
    generate_microsoft_ime_dictionary(CSV_PATH, IME_PATH)
    generate_mac_ime_dictionary(CSV_PATH, MAC_IME_PATH)
