#!/usr/bin/env python3
"""index.src.html → index.html

허브 스펙 표 자리({{SPEC_*}})를 아래 SPEC 데이터로 채웁니다.
  python3 build.py            index.html, en/index.html, ja/index.html 생성
  python3 build.py --preview  preview*.html 생성 (이미지를 원본 CDN 주소로 연결)
번역: i18n/en.json, i18n/ja.json 의 strings는 "한국어 원문": "번역" 쌍입니다.
한국어 원문을 고치면 같은 키를 두 파일에서도 함께 고쳐야 합니다. 빌드 때 번역이 빠진 한국어가 있으면 목록을 출력합니다.
수치 출처: growtac.com EQUAL 브레이크 · 컨트롤 레버 제품 페이지 스펙 표 (단위 mm, g)
"""
import re, sys, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (행 이름, [열1, 열2])
SPEC = {
    "BRAKE": {
        "cols": [("FLAT MOUNT", "플랫마운트"), ("POST MOUNT", "포스트마운트")],
        "rows": [
            ("캘리퍼 무게", ["136g", "137g"]),
            ("방식", ["기계식 · 싱글 피스톤", "기계식 · 싱글 피스톤"]),
            ("소재", ["초두랄루민 CNC", "초두랄루민 CNC"]),
            ("레버", ["숏풀 (로드 · 칸티)", "숏풀 (로드 · 칸티)"]),
            ("로터", ["140 / 160mm", "140 / 160mm"]),
            ("패드", ["Vesrah EVO RESIN", "Vesrah EVO RESIN"]),
            ("컬러", ["7색", "7색"]),
            ("케이블", ["전용 하드 케이싱 · 이너", "전용 하드 케이싱 · 이너"]),
            ("하드웨어", ["프론트 어댑터 · 리어 볼트", "마운팅 볼트 2개"]),
        ],
    },
    "KASHIMA": {
        "cols": [("FLAT MOUNT", "플랫마운트"), ("POST MOUNT", "포스트마운트")],
        "rows": [
            ("캘리퍼 무게", ["136g", "137g"]),
            ("표면 처리", ["카시마 코트", "카시마 코트"]),
            ("피스톤", ["그리스리스", "그리스리스"]),
            ("레버", ["숏풀 (로드 · 칸티)", "숏풀 (로드 · 칸티)"]),
            ("로터", ["140 / 160mm", "140 / 160mm"]),
            ("패드", ["Vesrah EVO RESIN", "Vesrah EVO RESIN"]),
            ("구성", ["풀세트 (전 · 후)", "풀세트 (전 · 후)"]),
        ],
    },
    "LEVER": {
        "cols": [("STANDARD", "시프터"), ("SHIFTLESS", "브레이크 레버")],
        "rows": [
            ("무게", ["좌 210g · 우 205g", "좌 · 우 130g"]),
            ("변속", ["무단 (프릭션) 2~13단", "-"]),
            ("구동계", ["로드 · MTB · 내장기어", "-"]),
            ("케이블 풀리", ["17 ~ 24mm 동봉", "-"]),
            ("브레이크", ["숏풀", "숏풀"]),
            ("핸들바", ["드롭바", "드롭바"]),
            ("리치 조절", ["있음", "있음"]),
            ("옵션", ["클릭 플레이트", "-"]),
        ],
    },
}


def table(g):
    head = "".join(f"<th>{s}<small>{c}</small></th>" for s, c in g["cols"])
    body = "".join(
        f"<tr><th>{html.escape(name)}</th>" + "".join(f"<td>{html.escape(v)}</td>" for v in vals) + "</tr>"
        for name, vals in g["rows"]
    )
    for name, vals in g["rows"]:
        assert len(vals) == len(g["cols"]), name
    return f'<table class="geo"><thead><tr><th></th>{head}</tr></thead><tbody>{body}</tbody></table>'


# 표 안의 한국어 (행 이름과 셀 값) 번역
SPEC_LABELS = {
    "en": {"캘리퍼 무게": "Caliper weight", "방식": "Type", "소재": "Material", "레버": "Lever", "로터": "Rotor", "패드": "Pad",
           "컬러": "Colors", "케이블": "Cable", "하드웨어": "Hardware", "표면 처리": "Finish", "피스톤": "Piston", "구성": "Includes",
           "무게": "Weight", "변속": "Shifting", "구동계": "Drivetrain", "케이블 풀리": "Cable pulley", "브레이크": "Brake",
           "핸들바": "Handlebar", "리치 조절": "Reach adjust", "옵션": "Option",
           "기계식 · 싱글 피스톤": "Mechanical · single piston", "초두랄루민 CNC": "Super duralumin, CNC", "숏풀 (로드 · 칸티)": "Short pull (road · cantilever)",
           "7색": "7 colors", "전용 하드 케이싱 · 이너": "Dedicated hard housing · inner", "프론트 어댑터 · 리어 볼트": "Front adapter · rear bolts",
           "마운팅 볼트 2개": "2 mounting bolts", "카시마 코트": "Kashima Coat", "그리스리스": "Greaseless", "풀세트 (전 · 후)": "Full set (F · R)",
           "좌 210g · 우 205g": "L 210g · R 205g", "좌 · 우 130g": "L · R 130g", "무단 (프릭션) 2~13단": "Stepless (friction), 2–13s",
           "로드 · MTB · 내장기어": "Road · MTB · internal gear hub", "17 ~ 24mm 동봉": "17–24mm included", "숏풀": "Short pull",
           "드롭바": "Drop bar", "있음": "Yes", "클릭 플레이트": "Click Plate",
           "플랫마운트": "Flat mount", "포스트마운트": "Post mount", "시프터": "Shifter", "브레이크 레버": "Brake lever"},
    "ja": {"캘리퍼 무게": "キャリパー重量", "방식": "方式", "소재": "素材", "레버": "レバー", "로터": "ローター", "패드": "パッド",
           "컬러": "カラー", "케이블": "ケーブル", "하드웨어": "ハードウェア", "표면 처리": "表面処理", "피스톤": "ピストン", "구성": "構成",
           "무게": "重量", "변속": "変速", "구동계": "駆動系", "케이블 풀리": "ケーブルプーリー", "브레이크": "ブレーキ",
           "핸들바": "ハンドルバー", "리치 조절": "リーチ調整", "옵션": "オプション",
           "기계식 · 싱글 피스톤": "機械式 · シングルピストン", "초두랄루민 CNC": "超々ジュラルミン CNC", "숏풀 (로드 · 칸티)": "ショートプル (ロード · カンチ)",
           "7색": "7色", "전용 하드 케이싱 · 이너": "専用ハードアウター · インナー", "프론트 어댑터 · 리어 볼트": "フロントアダプター · リアボルト",
           "마운팅 볼트 2개": "取付ボルト 2本", "카시마 코트": "カシマコート", "그리스리스": "グリスレス", "풀세트 (전 · 후)": "フルセット (前後)",
           "좌 210g · 우 205g": "左 210g · 右 205g", "좌 · 우 130g": "左 · 右 130g", "무단 (프릭션) 2~13단": "無段 (フリクション) 2〜13速",
           "로드 · MTB · 내장기어": "ロード · MTB · 内装変速", "17 ~ 24mm 동봉": "17〜24mm 付属", "숏풀": "ショートプル",
           "드롭바": "ドロップバー", "있음": "あり", "클릭 플레이트": "クリックプレート",
           "플랫마운트": "フラットマウント", "포스트마운트": "ポストマウント", "시프터": "シフター", "브레이크 레버": "ブレーキレバー"},
}

SITE = "https://growtac.rubiworkshop.com/"
LANGS = [("ko", "KO", ""), ("en", "EN", "en/"), ("ja", "JA", "ja/")]
HANGUL = re.compile("[가-힣]")
JA_FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400&display=swap" rel="stylesheet">'
           '<style>:root{--font:"RubiLatin","Noto Sans JP","Hiragino Sans","Yu Gothic",system-ui,sans-serif}</style>')


def lang_switch(cur):
    depth = "" if cur == "ko" else "../"
    return "".join(
        f'<a href="{depth}{path or "./"}" hreflang="{code}" lang="{code}"{" class=\"on\" aria-current=\"true\"" if code == cur else ""}>{label}</a>'
        for code, label, path in LANGS
    ).replace('href=".././"', 'href="../"')


HREFLANG = "\n".join(
    [f'<link rel="alternate" hreflang="{c}" href="{SITE}{p}">' for c, _, p in LANGS]
    + [f'<link rel="alternate" hreflang="x-default" href="{SITE}">']
)


def translate(html_text, tr):
    out = html_text
    for key in sorted(tr["strings"], key=len, reverse=True):
        val = tr["strings"][key]
        k = re.escape(key)
        out = re.sub(r"(>\s*)" + k + r"(\s*<)", lambda m: m.group(1) + val + m.group(2), out)
        out = out.replace(f'"{key}"', f'"{val}"')
    for pat, rep in tr["patterns"]:
        out = re.sub(pat, rep, out)
    return out


def render(code):
    src = (ROOT / "index.src.html").read_text(encoding="utf-8")
    out = re.sub(r"\{\{SPEC_(\w+)\}\}", lambda m: table(SPEC[m.group(1)]), src)
    out = out.replace("{{LANG}}", lang_switch(code)).replace("{{HREFLANG}}", HREFLANG)
    assert "{{" not in out, "채워지지 않은 자리표시자가 있습니다"
    if code == "ko":
        return out
    tr = json.loads((ROOT / f"i18n/{code}.json").read_text(encoding="utf-8"))
    for ko, t in sorted(SPEC_LABELS[code].items(), key=lambda x: -len(x[0])):
        out = out.replace(f"<th>{ko}</th>", f"<th>{t}</th>").replace(f"<td>{ko}</td>", f"<td>{t}</td>").replace(f"<small>{ko}</small>", f"<small>{t}</small>")
    out = translate(out, tr)
    m = tr["meta"]
    out = out.replace('<html lang="ko">', f'<html lang="{m["lang"]}">')
    out = out.replace(f'<link rel="canonical" href="{SITE}">', f'<link rel="canonical" href="{SITE}{m["path"]}">')
    out = out.replace(f'<meta property="og:url" content="{SITE}">', f'<meta property="og:url" content="{SITE}{m["path"]}">')
    out = out.replace('content="ko_KR"', f'content="{m["locale"]}"')
    out = out.replace('"inLanguage": "ko-KR"', f'"inLanguage": "{m["lang"]}"')
    if code == "ja":
        # 일본어는 한글 서체(에스코어 드림) 대신 Noto Sans JP (영문·숫자는 Pretendard 유지)
        out = out.replace("</style>\n</head>", "</style>\n" + JA_FONT + "\n</head>", 1)
    # 하위 폴더에서 이미지 경로
    out = re.sub(r'((?:src|href)=")images/', r"\1../images/", out)
    out = out.replace("url(images/", "url(../images/")
    left = sorted(set(re.findall(r"[^<>\"]*[가-힣][^<>\"]*", out)))
    left = [x.strip() for x in left if x.strip() and "/*" not in x]
    if left:
        print(f"[{code}] 번역되지 않은 한국어 {len(left)}건:", left[:30])
    return out


def main():
    manifest = (ROOT / ".github/image-manifest.txt").read_text().splitlines()
    cdn = dict(reversed(l.split()) for l in manifest if l.strip())
    for code, _, path in LANGS:
        out = render(code)
        used = set(re.findall(r"images/[\w/.-]+\.(?:jpg|png|svg|gif)", out))
        for u in sorted(used - set(cdn)):
            print("매니페스트에 없는 이미지:", u)
        if "--preview" in sys.argv:
            out = re.sub(r"(?:\.\./)?images/[\w/.-]+\.(?:jpg|png|svg|gif)", lambda m: cdn.get(m.group(0).replace("../", ""), m.group(0)), out)
            name = f"preview{'-' + code if code != 'ko' else ''}.html"
            (ROOT / name).write_text(out, encoding="utf-8")
            print(name)
        else:
            dest = ROOT / path / "index.html"
            dest.parent.mkdir(exist_ok=True)
            dest.write_text(out, encoding="utf-8")
            print(dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
