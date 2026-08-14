# Spring of Life 웹사이트 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Spring of Life(SL)를 소개하는 6페이지 정적 웹사이트를 만들고 GitHub Pages로 배포한다.

**Architecture:** 빌드 도구 없는 순수 정적 사이트. HTML 6장이 공유 `styles.css` 1개와 `script.js` 1개를 참조한다. 헤더/푸터는 인클루드 없이 각 HTML에 그대로 복사한다(LCC와 동일 방식). 이미지는 원본 PPT PDF에서 추출한다. 검증은 파이썬 스크립트 2개(정적 검사 / 브라우저 검사)로 자동화한다.

**Tech Stack:** HTML5 · Vanilla CSS(커스텀 프로퍼티, Grid, `clamp()`) · Vanilla JS(IntersectionObserver) · Poppins/Playfair Display/Inter(Google Fonts) + Pretendard(CDN) · 검증용 Python 3.12 + Pillow + Playwright

**Spec:** `docs/superpowers/specs/2026-08-15-sl-website-design.md`

## Global Constraints

- **언어**: 사이트 전체 영어. 한글은 고유명사 병기(`Seonbae (선배)`)에만 허용.
- **빌드 도구 금지**: 번들러·프레임워크·전처리기 없음. 브라우저가 바로 여는 파일만.
- **CSS는 `assets/css/styles.css` 단 하나, JS는 `assets/js/script.js` 단 하나.** 페이지별 파일을 새로 만들지 않는다.
- **JS 의존성 0개.** 외부 라이브러리 로드 금지.
- **인라인 `style=` 속성 금지.** 모든 스타일은 styles.css에.
- **컬러는 반드시 `:root` 토큰 사용.** 하드코딩된 hex 금지(토큰 정의부 제외).
- **`--teal`(#7FCFD4) 배경 위에 흰 텍스트 금지** (대비 1.8:1). `--ink`만 얹는다.
- **모든 `<img>`에 `alt` 속성 필수.** 장식용은 `alt=""`.
- **내부 링크는 전부 상대 경로.** 절대 URL은 canonical/og:url/sitemap에만.
- **콘텐츠 정본**: 사용자 제공 SL Concept 텍스트 > PPT. 충돌 시 전자를 따른다.
- **사실 날조 금지.** 원본에 없는 통계·연락처·일정·가격을 만들어내지 않는다. 필요하면 자리표시자로 둔다.
- **canonical 기준 URL**: `https://ondo1400-dotcom.github.io/SL/` (커스텀 도메인 확정 시 일괄 치환)
- **커밋 메시지**: 한국어 한 줄 요약 + 필요시 본문. 각 Task 끝에 1커밋.

---

## 파일 구조

| 경로 | 책임 | 생성 Task |
|---|---|---|
| `_archive/extract_assets.py` | PDF → 이미지 추출 (일회용, git 미추적) | 1 |
| `assets/images/logo.png` | 투명 배경 물방울 로고 | 1 |
| `assets/images/posters/01~05.png` | 행사 포스터 | 1 |
| `assets/images/gallery/01~05.jpg` | 행사 현장 사진 | 1 |
| `assets/images/people/01~04.jpg` | 간증자 프로필(정사각 크롭) | 1 |
| `tools/verify.py` | 링크 무결성 · alt 커버리지 정적 검사 | 2 |
| `tools/fixtures/` | verify.py 자체 테스트용 픽스처 | 2 |
| `assets/css/styles.css` | 전체 스타일 (토큰 → 컴포넌트 → 페이지별 블록) | 3~10 |
| `index.html` | 홈 | 3, 5 |
| `assets/js/script.js` | reveal · 모바일 내비 · 헤더 스크롤 · 라이트박스 | 4, 8 |
| `tools/browser_check.py` | 반응형 폭 · 콘솔 에러 · 스크린샷 (Playwright) | 4 |
| `about.html` | 소개 | 6 |
| `programs.html` | 프로그램 · How to Start | 7 |
| `events.html` | 지난 행사 | 8 |
| `stories.html` | 간증 | 9 |
| `contact.html` | 문의 · FAQ | 10 |
| `README.md` `robots.txt` `sitemap.xml` | 문서 · SEO | 11 |

**스펙과의 차이 1건**: 스펙 §4의 파일 트리에 없는 `tools/` 디렉터리를 추가한다. 스펙 §11이 스크립트 기반 검증을 요구하는데, 매 Task마다 반복 실행해야 하므로 git 미추적 `_archive/`에 둘 수 없다. 일회용인 추출 스크립트만 스펙대로 `_archive/`에 남긴다.

---

## Task 1: PDF 에셋 추출

**Files:**
- Create: `_archive/extract_assets.py`
- Create: `assets/images/logo.png`, `assets/images/posters/01~05.png`, `assets/images/gallery/01~05.jpg`, `assets/images/people/01~04.jpg`
- Move: `Blue and White Minimalist Company Introduction Business Presentation.pdf` → `_archive/source-deck.pdf`

**Interfaces:**
- Consumes: 없음 (첫 Task)
- Produces: `assets/images/` 하위 15개 이미지 파일. 이후 모든 페이지 Task가 이 경로를 참조한다. 파일명 규약은 위 표 그대로이며, 확장자를 바꾸지 않는다.

**배경:** `pdfimages -list`로 확인한 PDF 내장 비트맵 인덱스는 다음과 같다. 이 번호는 확정값이 아니라 **검증 대상**이다 — 스크립트는 번호를 하드코딩하되, 추출 후 눈으로 확인하는 단계를 반드시 거친다.

| 대상 | pdfimages 인덱스 | 원본 크기 |
|---|---|---|
| 로고 (RGB) | 4 | 432×432 |
| 로고 (알파 마스크) | 5 | 432×432 |
| 포스터 5장 | 16, 17, 18, 19, 20 | ~453×640 |
| 현장 사진 5장 | 21, 22, 23, 24, 25 | ~512×384 |
| 인물 사진 4장 | 28, 29, 30, 31 | ~448×640 |

- [ ] **Step 1: PDF를 `_archive/`로 옮기고 디렉터리 준비**

```bash
cd /mnt/c/Users/jdino/Desktop/SL
mkdir -p _archive assets/images/posters assets/images/gallery assets/images/people
mv "Blue and White Minimalist Company Introduction Business Presentation.pdf" _archive/source-deck.pdf
ls -la _archive/
```

기대: `_archive/source-deck.pdf` 존재, 루트에 PDF 없음.

- [ ] **Step 2: 추출 스크립트 작성**

`_archive/extract_assets.py`:

```python
#!/usr/bin/env python3
"""SL PPT(PDF)에서 웹사이트용 이미지를 추출한다. 일회용 스크립트.

사용법: python3 _archive/extract_assets.py
전제:  pdfimages(poppler-utils), Pillow
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "_archive" / "source-deck.pdf"
RAW = ROOT / "_archive" / "raw"
IMG = ROOT / "assets" / "images"

# pdfimages 인덱스 → 산출물
LOGO_RGB, LOGO_MASK = 4, 5
POSTERS = [16, 17, 18, 19, 20]
GALLERY = [21, 22, 23, 24, 25]
PEOPLE = [28, 29, 30, 31]


def extract_raw() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdfimages", "-png", "-p", str(PDF), str(RAW / "img")],
        check=True,
    )


def raw_path(index: int) -> Path:
    """pdfimages는 img-<page>-<index>.png 형태로 저장한다."""
    matches = sorted(RAW.glob(f"img-*-{index:03d}.png"))
    if not matches:
        sys.exit(f"인덱스 {index}에 해당하는 추출 파일이 없습니다. "
                 f"'pdfimages -list'로 인덱스를 다시 확인하세요.")
    return matches[0]


def build_logo() -> None:
    rgb = Image.open(raw_path(LOGO_RGB)).convert("RGB")
    mask = Image.open(raw_path(LOGO_MASK)).convert("L")
    if rgb.size != mask.size:
        mask = mask.resize(rgb.size, Image.LANCZOS)
    out = rgb.copy()
    out.putalpha(mask)
    out.save(IMG / "logo.png")
    print(f"logo.png  {out.size}  alpha={out.mode}")


def copy_set(indices: list[int], subdir: str, ext: str,
             square: bool = False) -> None:
    target = IMG / subdir
    target.mkdir(parents=True, exist_ok=True)
    for n, index in enumerate(indices, start=1):
        im = Image.open(raw_path(index)).convert("RGB")
        if square:
            side = min(im.size)
            left = (im.width - side) // 2
            top = int((im.height - side) * 0.25)  # 얼굴은 위쪽에 있다
            im = im.crop((left, top, left + side, top + side))
        name = f"{n:02d}.{ext}"
        if ext == "jpg":
            im.save(target / name, quality=88, optimize=True)
        else:
            im.save(target / name, optimize=True)
        print(f"{subdir}/{name}  {im.size}")


def main() -> None:
    if not PDF.exists():
        sys.exit(f"{PDF} 가 없습니다.")
    IMG.mkdir(parents=True, exist_ok=True)
    extract_raw()
    build_logo()
    copy_set(POSTERS, "posters", "png")
    copy_set(GALLERY, "gallery", "jpg")
    copy_set(PEOPLE, "people", "jpg", square=True)
    print("\n완료. assets/images/ 를 눈으로 확인하세요.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 실행하고 산출물 개수를 확인**

```bash
python3 _archive/extract_assets.py
find assets/images -type f | sort
```

기대: 정확히 15개 파일 — `logo.png`, `posters/01~05.png`, `gallery/01~05.jpg`, `people/01~04.jpg`.
개수가 다르면 인덱스가 어긋난 것이다. `pdfimages -list _archive/source-deck.pdf`로 다시 확인하고 스크립트 상수를 고친다.

- [ ] **Step 4: 로고 투명도 검증**

```bash
python3 -c "
from PIL import Image
im = Image.open('assets/images/logo.png')
print('mode:', im.mode, 'size:', im.size)
a = im.getchannel('A')
print('alpha min/max:', a.getextrema())
corner = im.getpixel((2, 2))
print('corner pixel:', corner)
"
```

기대: `mode: RGBA`, alpha 최솟값 0(투명 영역 존재), 모서리 픽셀의 알파가 0에 가까움.
알파가 전부 255면 마스크 합성이 안 된 것이다 — 인덱스 5가 실제 smask인지 확인한다.

- [ ] **Step 5: 이미지 내용을 눈으로 확인하고 순서를 기록**

각 이미지를 Read 도구로 열어 실제 내용을 확인한다. 특히 **인물 사진 4장의 순서**를 확정해야 한다.
PPT 6쪽의 배치 순서는 **Lorena(Brazil) → Gracia(Indonesia) → Mahdi(Iran) → Jenny(Chile)** 이므로
`people/01~04`가 이 순서와 맞는지 확인한다. 다르면 파일을 바꿔 저장한다.

포스터 5장의 순서도 확인한다. PPT 5쪽 배치는
**Trivia Night → Movie Night → Beyond Small Talk → New Year Check-in → New Year, New Me** 순이다.

확인 결과를 `_archive/asset-map.md`에 기록한다:

```markdown
# 에셋 매핑 (2026-08-15 확인)

## people/
- 01.jpg — Lorena, Brazil
- 02.jpg — Gracia, Indonesia
- 03.jpg — Mahdi, Iran
- 04.jpg — Jenny, Chile

## posters/
- 01.png — Trivia Night (Topic: The Chosen)
- 02.png — Movie Night
- 03.png — Beyond Small Talk
- 04.png — New Year Check-in
- 05.png — New Year, New Me: The Path to Happiness

## gallery/
- 01~05.jpg — 행사 현장 사진 (특정 행사 귀속 불명, 순서 무관)
```

- [ ] **Step 6: 커밋**

```bash
git add assets/images .gitignore
git status --short
git commit -m "feat: PPT에서 사이트 이미지 에셋 추출

로고(투명 PNG) 1장, 행사 포스터 5장, 현장 사진 5장, 간증자 프로필 4장.
원본 PDF와 추출 스크립트는 _archive/(git 미추적)에 보관."
```

기대: `_archive/`와 `*.pdf`는 `.gitignore`에 걸려 커밋에 포함되지 않는다. `git status --short`로 확인할 것.

---

## Task 2: 검증 하네스

**Files:**
- Create: `tools/verify.py`
- Create: `tools/fixtures/good.html`, `tools/fixtures/bad.html`, `tools/fixtures/exists.png`

**Interfaces:**
- Consumes: 없음
- Produces: `python3 tools/verify.py [디렉터리]` — 기본값은 저장소 루트. 문제가 없으면 exit 0, 있으면 문제 목록을 출력하고 exit 1. 이후 **모든 Task가 이 명령으로 자기 작업을 검증한다.**

검사 항목 3가지:
1. `href`/`src`의 로컬 경로가 실재하는 파일을 가리키는가
2. 모든 `<img>`에 `alt` 속성이 있는가
3. 같은 문서 내 앵커(`#foo`)에 대응하는 `id="foo"`가 있는가

- [ ] **Step 1: 실패하는 테스트(픽스처)를 먼저 만든다**

`tools/fixtures/exists.png` — 1×1 투명 PNG:

```bash
mkdir -p tools/fixtures
python3 -c "
from PIL import Image
Image.new('RGBA', (1, 1), (0, 0, 0, 0)).save('tools/fixtures/exists.png')
"
```

`tools/fixtures/good.html` — 문제가 하나도 없어야 하는 파일:

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>good</title></head>
<body>
  <a href="bad.html">local page</a>
  <a href="#anchor">jump</a>
  <a href="https://example.com/">external</a>
  <a href="mailto:hi@example.com">mail</a>
  <img src="exists.png" alt="a pixel">
  <img src="exists.png" alt="">
  <h2 id="anchor">Anchor</h2>
</body>
</html>
```

`tools/fixtures/bad.html` — 정확히 3가지 문제를 심는다:

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>bad</title></head>
<body>
  <a href="nope.html">missing page</a>
  <a href="#ghost">missing anchor</a>
  <img src="exists.png">
</body>
</html>
```

- [ ] **Step 2: 검사 스크립트를 작성**

`tools/verify.py`:

```python
#!/usr/bin/env python3
"""정적 사이트 검사: 링크 무결성 · alt 커버리지 · 내부 앵커.

사용법: python3 tools/verify.py [디렉터리]
종료코드: 0 = 문제 없음, 1 = 문제 있음
"""
import re
import sys
from pathlib import Path

IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
ALT_ATTR = re.compile(r"\balt\s*=", re.IGNORECASE)
LINK_ATTR = re.compile(r"\b(?:href|src)\s*=\s*[\"']([^\"']*)[\"']", re.IGNORECASE)
ID_ATTR = re.compile(r"\bid\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:")


def check(root: Path) -> list[str]:
    problems: list[str] = []
    pages = sorted(root.rglob("*.html"))
    if not pages:
        return [f"{root}: html 파일이 없습니다"]

    for page in pages:
        rel = page.relative_to(root)
        html = page.read_text(encoding="utf-8")
        ids = set(ID_ATTR.findall(html))

        for tag in IMG_TAG.findall(html):
            if not ALT_ATTR.search(tag):
                problems.append(f"{rel}: alt 없는 img — {tag[:70]}")

        for target in LINK_ATTR.findall(html):
            target = target.strip()
            if not target or target.startswith(SKIP_PREFIX):
                continue
            if target.startswith("#"):
                if target[1:] not in ids:
                    problems.append(f"{rel}: 앵커 대상 없음 — {target}")
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            if not (page.parent / path_part).resolve().exists():
                problems.append(f"{rel}: 파일 없음 — {target}")

    return problems


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    problems = check(root)
    for problem in problems:
        print(problem)
    total = len(sorted(root.rglob("*.html")))
    if problems:
        print(f"\n✗ {total}개 페이지에서 {len(problems)}건 발견")
        sys.exit(1)
    print(f"✓ {total}개 페이지 통과 (링크 · alt · 앵커)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 픽스처로 스크립트를 검증**

```bash
python3 tools/verify.py tools/fixtures
```

기대: exit 1, 그리고 **정확히 3건**이 출력된다.
- `bad.html: alt 없는 img — <img src="exists.png">`
- `bad.html: 앵커 대상 없음 — #ghost`
- `bad.html: 파일 없음 — nope.html`

`good.html`에서는 한 건도 나오면 안 된다. 외부 링크·mailto·`alt=""`를 오탐하면 스크립트를 고친다.

- [ ] **Step 4: 정상 케이스만 있을 때 통과하는지 확인**

```bash
mkdir -p /tmp/verify-ok && cp tools/fixtures/good.html tools/fixtures/exists.png /tmp/verify-ok/
python3 -c "
from pathlib import Path
p = Path('/tmp/verify-ok/good.html')
p.write_text(p.read_text().replace('<a href=\"bad.html\">local page</a>', ''))
"
python3 tools/verify.py /tmp/verify-ok; echo "exit=$?"
rm -rf /tmp/verify-ok
```

기대: `✓ 1개 페이지 통과`, `exit=0`.

- [ ] **Step 5: 커밋**

```bash
git add tools/
git commit -m "feat: 링크·alt·앵커 정적 검사 스크립트 추가

픽스처(good/bad)로 스크립트 자체를 검증한다.
이후 모든 페이지 작업은 python3 tools/verify.py 로 확인한다."
```

---

## Task 3: 디자인 시스템 + 사이트 셸

**Files:**
- Create: `assets/css/styles.css`
- Create: `index.html` (이 Task에서는 헤더 + 히어로 + 푸터까지만)

**Interfaces:**
- Consumes: `assets/images/logo.png` (Task 1)
- Produces:
  - CSS 토큰 `--navy --navy-deep --teal --teal-soft --forest --sun --lavender --paper --ink --muted --font-head --font-display --font-body --max --gutter --radius --radius-sm --border --section-y --ease`
  - 공통 클래스 `.wrap .panel .card .marker .chip .btn .btn--primary .section .section--navy .eyebrow .lead .reveal`
  - **공유 헤더/푸터 마크업** — Task 5~10이 이 마크업을 문자 그대로 복사한다.
  - `.header--scrolled` `.menu-btn` `#mobileNav` — Task 4의 JS가 이 이름에 의존한다.

- [ ] **Step 1: `assets/css/styles.css` 작성 — 토큰과 기반**

```css
/* =========================================================
   Spring of Life — 정적 다중 페이지 사이트
   Palette / type 출처: SL 소개 덱 (2026)
   ========================================================= */

:root {
  /* Brand */
  --navy:       #0B3C5D;
  --navy-deep:  #072A42;
  --teal:       #7FCFD4;
  --teal-soft:  #BEE7E9;
  --forest:     #1F4B3F;
  --sun:        #FBF3A8;
  --lavender:   #E8EDFB;
  --paper:      #FFFFFF;
  --ink:        #1A1A1A;
  --muted:      #5C6470;

  /* Type */
  --font-head:    'Poppins', 'Pretendard', system-ui, sans-serif;
  --font-display: 'Playfair Display', Georgia, serif;
  --font-body:    'Inter', 'Pretendard', system-ui, sans-serif;

  /* Layout */
  --max:       1200px;
  --gutter:    clamp(20px, 5vw, 40px);
  --radius:    22px;
  --radius-sm: 14px;
  --border:    2.5px solid var(--ink);
  --section-y: clamp(64px, 10vw, 120px);

  /* Motion */
  --ease: cubic-bezier(.2, .7, .2, 1);
}

*, *::before, *::after { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  margin: 0;
  background: var(--lavender);
  color: var(--ink);
  font-family: var(--font-body);
  font-size: clamp(15px, 1.05vw, 17px);
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}

img { max-width: 100%; display: block; }

a { color: inherit; }

h1, h2, h3, h4 {
  font-family: var(--font-head);
  font-weight: 800;
  line-height: 1.12;
  margin: 0 0 .5em;
  letter-spacing: .01em;
}

h1 { font-size: clamp(2.1rem, 6vw, 3.6rem); text-transform: uppercase; }
h2 { font-size: clamp(1.55rem, 4vw, 2.5rem); text-transform: uppercase; }
h3 { font-size: clamp(1.1rem, 2.2vw, 1.4rem); }

p { margin: 0 0 1em; }

.script {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0;
}

.eyebrow {
  font-family: var(--font-head);
  font-weight: 700;
  font-size: .8rem;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 .8em;
}

.lead { font-size: clamp(1rem, 1.5vw, 1.2rem); color: var(--muted); max-width: 62ch; }

.marker {
  background: linear-gradient(180deg, transparent 58%, var(--sun) 58%);
  padding: 0 .14em;
}

/* Layout primitives ------------------------------------- */

.wrap {
  width: min(var(--max), calc(100% - var(--gutter) * 2));
  margin-inline: auto;
}

.section { padding-block: var(--section-y); }

.section--navy {
  background: linear-gradient(160deg, var(--navy), var(--navy-deep));
  color: var(--paper);
}
.section--navy .lead,
.section--navy .eyebrow { color: rgba(255, 255, 255, .72); }

.panel {
  background: var(--paper);
  border: var(--border);
  border-radius: var(--radius);
  padding: clamp(24px, 4vw, 56px);
}

.card {
  background: var(--paper);
  border: var(--border);
  border-radius: var(--radius);
  padding: clamp(20px, 2.6vw, 30px);
}

.grid { display: grid; gap: clamp(16px, 2.4vw, 26px); }
.grid--auto { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }

.chip {
  display: grid;
  place-items: center;
  width: 56px; height: 56px;
  flex: none;
  border-radius: 50%;
  background: var(--teal-soft);
}
.chip svg {
  width: 28px; height: 28px;
  fill: none;
  stroke: var(--forest);
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Buttons ----------------------------------------------- */

.btn {
  display: inline-flex;
  align-items: center;
  gap: .5em;
  font-family: var(--font-head);
  font-weight: 700;
  font-size: .82rem;
  letter-spacing: .06em;
  text-transform: uppercase;
  padding: .9em 1.6em;
  border: var(--border);
  border-radius: 999px;
  background: var(--paper);
  color: var(--ink);
  text-decoration: none;
  cursor: pointer;
  transition: transform .25s var(--ease), background .25s var(--ease);
}
.btn:hover { transform: translateY(-2px); background: var(--sun); }
.btn:focus-visible { outline: 3px solid var(--navy); outline-offset: 3px; }

.btn--primary { background: var(--navy); border-color: var(--navy); color: var(--paper); }
.btn--primary:hover { background: var(--navy-deep); color: var(--paper); }

/* Reveal ------------------------------------------------ */

.reveal {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity .7s var(--ease), transform .7s var(--ease);
}
.reveal.is-visible { opacity: 1; transform: none; }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .reveal { opacity: 1; transform: none; transition: none; }
  * { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
```

- [ ] **Step 2: 헤더·푸터·히어로 스타일을 이어서 작성**

같은 파일 뒤에 추가:

```css
/* Header ------------------------------------------------ */

.header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(232, 237, 251, .82);
  backdrop-filter: blur(10px);
  transition: background .3s var(--ease), box-shadow .3s var(--ease);
}
.header--scrolled {
  background: rgba(255, 255, 255, .94);
  box-shadow: 0 1px 0 rgba(26, 26, 26, .14);
}

.header__inner {
  width: min(var(--max), calc(100% - var(--gutter) * 2));
  margin-inline: auto;
  display: flex;
  align-items: center;
  gap: 20px;
  padding-block: 14px;
}

.logo { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.logo__mark { width: 42px; height: 42px; }
.logo__text {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 1.35rem;
  color: var(--navy);
  white-space: nowrap;
}

.nav { margin-left: auto; }
.nav ul { display: flex; gap: 28px; list-style: none; margin: 0; padding: 0; }
.nav__link {
  font-family: var(--font-head);
  font-weight: 600;
  font-size: .9rem;
  text-decoration: none;
  padding-block: 6px;
  border-bottom: 2px solid transparent;
}
.nav__link:hover { border-bottom-color: var(--teal); }
.nav__link[aria-current="page"] { border-bottom-color: var(--navy); }

.menu-btn {
  display: none;
  width: 44px; height: 44px;
  padding: 0;
  background: var(--paper);
  border: var(--border);
  border-radius: 12px;
  cursor: pointer;
}
.menu-btn span {
  display: block;
  width: 18px; height: 2px;
  margin: 3px auto;
  background: var(--ink);
  transition: transform .3s var(--ease), opacity .3s var(--ease);
}
.menu-btn[aria-expanded="true"] span:nth-child(1) { transform: translateY(5px) rotate(45deg); }
.menu-btn[aria-expanded="true"] span:nth-child(2) { opacity: 0; }
.menu-btn[aria-expanded="true"] span:nth-child(3) { transform: translateY(-5px) rotate(-45deg); }

.mobile-nav {
  display: grid;
  gap: 4px;
  padding: 12px var(--gutter) 22px;
  background: var(--paper);
  border-top: 2px solid var(--ink);
}
.mobile-nav a {
  font-family: var(--font-head);
  font-weight: 600;
  text-decoration: none;
  padding: 12px 4px;
  border-bottom: 1px solid rgba(26, 26, 26, .1);
}
.mobile-nav[hidden] { display: none; }

@media (max-width: 860px) {
  .nav, .header .btn { display: none; }
  .menu-btn { display: block; margin-left: auto; }
}

/* Hero -------------------------------------------------- */

.hero { padding-block: clamp(48px, 8vw, 96px); }
.hero__panel { display: grid; gap: clamp(20px, 3vw, 34px); text-align: center; }
.hero__mark { width: clamp(84px, 12vw, 128px); height: auto; margin-inline: auto; }
.hero h1 { margin: 0; }
.hero h1 .script { display: block; font-size: 1.16em; }
.hero .lead { margin-inline: auto; }
.hero__actions { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; }

/* Footer ------------------------------------------------ */

.footer { background: var(--navy); color: var(--paper); padding-block: clamp(44px, 6vw, 72px) 0; }
.footer__inner {
  width: min(var(--max), calc(100% - var(--gutter) * 2));
  margin-inline: auto;
  display: grid;
  gap: clamp(28px, 4vw, 56px);
  grid-template-columns: minmax(260px, 1.4fr) 1fr;
}
@media (max-width: 720px) { .footer__inner { grid-template-columns: 1fr; } }

.footer__brand img { width: 52px; height: 52px; margin-bottom: 14px; }
.footer__tagline { color: rgba(255, 255, 255, .74); max-width: 44ch; }

.footer__nav { display: flex; gap: clamp(28px, 5vw, 64px); }
.footer__group { display: grid; align-content: start; gap: 10px; }
.footer__group strong {
  font-family: var(--font-head);
  font-size: .78rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--teal);
}
.footer__group a { color: rgba(255, 255, 255, .82); text-decoration: none; }
.footer__group a:hover { color: var(--paper); text-decoration: underline; }

.footer__base {
  width: min(var(--max), calc(100% - var(--gutter) * 2));
  margin: clamp(32px, 5vw, 56px) auto 0;
  padding-block: 20px;
  border-top: 1px solid rgba(255, 255, 255, .18);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
  justify-content: space-between;
  font-size: .84rem;
  color: rgba(255, 255, 255, .62);
}
```

- [ ] **Step 3: `index.html`의 셸을 작성 (헤더 + 히어로 + 푸터)**

**이 마크업의 `<header>`와 `<footer>` 블록은 Task 5~10에서 그대로 복사한다.**
페이지마다 바뀌는 것은 `aria-current="page"`의 위치뿐이다.

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Spring of Life | Bible Study &amp; Mentoring for Youth in Korea</title>
  <meta name="description"
    content="Spring of Life is a non-denominational Bible institution rooted in missionary work from Germany, walking with youth in Korea and around the world since 2014." />
  <link rel="canonical" href="https://ondo1400-dotcom.github.io/SL/" />
  <link rel="icon" href="assets/images/logo.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:ital,wght@1,500;1,600&family=Poppins:wght@600;700;800&display=swap" />
  <link rel="stylesheet" as="style" crossorigin
    href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <link rel="stylesheet" href="assets/css/styles.css" />
</head>

<body>

  <!-- ============== HEADER (shared) ============== -->
  <header class="header" id="header">
    <div class="header__inner">
      <a href="index.html" class="logo" aria-label="Spring of Life — home">
        <img src="assets/images/logo.png" alt="" class="logo__mark" width="42" height="42" />
        <span class="logo__text">Spring of Life</span>
      </a>
      <nav class="nav" aria-label="Primary">
        <ul>
          <li><a class="nav__link" href="about.html">About</a></li>
          <li><a class="nav__link" href="programs.html">Programs</a></li>
          <li><a class="nav__link" href="events.html">Events</a></li>
          <li><a class="nav__link" href="stories.html">Stories</a></li>
        </ul>
      </nav>
      <a href="contact.html" class="btn">Get in Touch <span aria-hidden="true">&rarr;</span></a>
      <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="mobileNav">
        <span></span><span></span><span></span>
      </button>
    </div>
    <div class="mobile-nav" id="mobileNav" hidden>
      <a href="about.html">About</a>
      <a href="programs.html">Programs</a>
      <a href="events.html">Events</a>
      <a href="stories.html">Stories</a>
      <a href="contact.html">Get in Touch</a>
    </div>
  </header>

  <main>

    <!-- ============== HERO ============== -->
    <section class="hero">
      <div class="wrap">
        <div class="panel hero__panel">
          <img src="assets/images/logo.png" alt="Spring of Life logo" class="hero__mark" width="128" height="128" />
          <h1>Get to Know <span class="script">Spring of Life</span></h1>
          <p class="lead">A non-denominational Bible institution rooted in missionary work from Germany
            &mdash; walking with youth in Korea and around the world since 2014.</p>
          <div class="hero__actions">
            <a href="programs.html" class="btn btn--primary">See our programs</a>
            <a href="about.html" class="btn">Read our story</a>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- ============== FOOTER (shared) ============== -->
  <footer class="footer">
    <div class="footer__inner">
      <div class="footer__brand">
        <img src="assets/images/logo.png" alt="" width="52" height="52" />
        <p class="footer__tagline">A non-denominational Bible institution rooted in missionary work from
          Germany, reaching youth and communities across Africa, South America, and Asia.</p>
      </div>
      <nav class="footer__nav" aria-label="Footer">
        <div class="footer__group">
          <strong>Explore</strong>
          <a href="about.html">About</a>
          <a href="programs.html">Programs</a>
          <a href="events.html">Events</a>
        </div>
        <div class="footer__group">
          <strong>Connect</strong>
          <a href="stories.html">Stories</a>
          <a href="contact.html">Get in Touch</a>
        </div>
      </nav>
    </div>
    <div class="footer__base">
      <span>&copy; 2026 Spring of Life. All rights reserved.</span>
      <span>Seoul, Korea &middot; Since 2014</span>
    </div>
  </footer>

  <script src="assets/js/script.js"></script>
</body>

</html>
```

- [ ] **Step 4: 검사 실행**

```bash
python3 tools/verify.py .
```

기대: 이 시점에는 `about.html` 등이 아직 없으므로 **파일 없음 오류가 여러 건 나오는 것이 정상**이다.
`assets/images/logo.png`, `assets/css/styles.css`에 대한 오류는 나오면 안 된다.
`assets/js/script.js`는 Task 4에서 만들므로 여기서는 오류가 나온다.

로고와 CSS 경로 오류가 0건인지만 확인한다:

```bash
python3 tools/verify.py . | grep -E "logo\.png|styles\.css" || echo "✓ 에셋 경로 정상"
```

기대: `✓ 에셋 경로 정상`

- [ ] **Step 5: 브라우저로 실제 렌더 확인**

```bash
python3 -m http.server 8000 --directory . &
sleep 1
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:8000/index.html")
    pg.wait_for_timeout(1200)
    print("title:", pg.title())
    print("scrollWidth:", pg.evaluate("document.documentElement.scrollWidth"),
          "innerWidth:", pg.evaluate("window.innerWidth"))
    pg.screenshot(path="/tmp/sl-shell.png", full_page=True)
    b.close()
PY
kill %1
```

Read 도구로 `/tmp/sl-shell.png`를 열어 확인한다. 체크할 것:
- 헤더에 로고와 5개 링크가 보인다
- 히어로가 흰 카드 + 검은 라운드 테두리로 렌더된다
- "Spring of Life"가 이탤릭 세리프로 보인다
- 푸터가 네이비 배경이다
- `scrollWidth <= innerWidth`

- [ ] **Step 6: 커밋**

```bash
git add assets/css/styles.css index.html
git commit -m "feat: 디자인 시스템과 사이트 셸 구축

컬러/타이포 토큰, 흰 카드+검정 테두리 시그니처 컴포넌트,
공유 헤더/푸터 마크업, 홈 히어로."
```

---

## Task 4: 인터랙션 스크립트 + 브라우저 검사기

**Files:**
- Create: `assets/js/script.js`
- Create: `tools/browser_check.py`

**Interfaces:**
- Consumes: `#header` `#menuBtn` `#mobileNav` `.reveal` (Task 3)
- Produces:
  - `.reveal` → `.is-visible` 토글
  - `.header--scrolled` 클래스 토글
  - `python3 tools/browser_check.py` — 모든 HTML을 3개 폭에서 열어 가로 오버플로와 콘솔 에러를 검사하고 스크린샷을 남긴다. exit 0/1.
  - Task 8이 이 파일에 라이트박스 모듈을 **추가**한다 (재작성 아님).

- [ ] **Step 1: `assets/js/script.js` 작성**

```javascript
/* Spring of Life — shared interactions. 의존성 없음. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- Reveal on scroll --- */
  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

    items.forEach(function (el) { observer.observe(el); });
  }

  /* --- Mobile navigation --- */
  function initMobileNav() {
    var btn = document.getElementById('menuBtn');
    var nav = document.getElementById('mobileNav');
    if (!btn || !nav) return;

    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      btn.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
      nav.hidden = open;
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || nav.hidden) return;
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-label', 'Open menu');
      nav.hidden = true;
      btn.focus();
    });
  }

  /* --- Header scroll state --- */
  function initHeaderState() {
    var header = document.getElementById('header');
    if (!header) return;
    var ticking = false;

    function update() {
      header.classList.toggle('header--scrolled', window.scrollY > 8);
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });

    update();
  }

  document.addEventListener('DOMContentLoaded', function () {
    initReveal();
    initMobileNav();
    initHeaderState();
  });
})();
```

- [ ] **Step 2: `tools/browser_check.py` 작성**

```python
#!/usr/bin/env python3
"""브라우저 검사: 가로 오버플로 · 콘솔 에러 · 스크린샷.

사용법: python3 tools/browser_check.py [--shots 출력디렉터리]
로컬 정적 서버를 직접 띄우고 종료한다.
"""
import argparse
import http.server
import socketserver
import threading
from functools import partial
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = [360, 768, 1440]
PORT = 8765


def serve() -> socketserver.TCPServer:
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", default="")
    args = parser.parse_args()

    pages = sorted(p.name for p in ROOT.glob("*.html"))
    if not pages:
        raise SystemExit("루트에 html 파일이 없습니다")

    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    httpd = serve()
    problems: list[str] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for width in WIDTHS:
                page = browser.new_page(viewport={"width": width, "height": 900})
                errors: list[str] = []
                page.on("console", lambda m: errors.append(m.text)
                        if m.type == "error" else None)
                page.on("pageerror", lambda e: errors.append(str(e)))

                for name in pages:
                    del errors[:]
                    page.goto(f"http://127.0.0.1:{PORT}/{name}",
                              wait_until="networkidle")
                    page.wait_for_timeout(400)

                    scroll_w = page.evaluate("document.documentElement.scrollWidth")
                    inner_w = page.evaluate("window.innerWidth")
                    if scroll_w > inner_w + 1:
                        problems.append(
                            f"{name} @{width}px: 가로 오버플로 "
                            f"scrollWidth={scroll_w} > innerWidth={inner_w}")
                    for err in errors:
                        problems.append(f"{name} @{width}px: 콘솔 에러 — {err}")

                    if shots and width == 1440:
                        page.screenshot(path=str(shots / f"{Path(name).stem}.png"),
                                        full_page=True)
                page.close()
            browser.close()
    finally:
        httpd.shutdown()

    for problem in problems:
        print(problem)
    if problems:
        print(f"\n✗ {len(problems)}건 발견")
        raise SystemExit(1)
    print(f"✓ {len(pages)}개 페이지 × {len(WIDTHS)}개 폭 통과")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 스크립트가 실제로 동작하는지 검사기로 확인**

```bash
python3 tools/browser_check.py --shots /tmp/sl-shots
```

기대: `✓ 1개 페이지 × 3개 폭 통과` (이 시점에는 index.html만 존재).
콘솔 에러가 나오면 script.js를 고친다.

- [ ] **Step 4: 모바일 내비가 실제로 열리는지 확인**

```bash
python3 - <<'PY'
import http.server, socketserver, threading
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path.cwd()
handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
httpd = socketserver.TCPServer(("127.0.0.1", 8766), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.goto("http://127.0.0.1:8766/index.html", wait_until="networkidle")
    assert pg.locator("#mobileNav").is_hidden(), "초기에 메뉴가 열려 있음"
    pg.click("#menuBtn")
    assert pg.locator("#mobileNav").is_visible(), "버튼을 눌러도 안 열림"
    assert pg.get_attribute("#menuBtn", "aria-expanded") == "true"
    pg.keyboard.press("Escape")
    assert pg.locator("#mobileNav").is_hidden(), "ESC로 안 닫힘"
    assert pg.get_attribute("#menuBtn", "aria-expanded") == "false"
    print("✓ 모바일 내비 열기/ESC 닫기/aria 동기화 정상")
    b.close()
httpd.shutdown()
PY
```

기대: `✓ 모바일 내비 열기/ESC 닫기/aria 동기화 정상`. assert가 터지면 고친다.

- [ ] **Step 5: 커밋**

```bash
git add assets/js/script.js tools/browser_check.py
git commit -m "feat: 공유 인터랙션 스크립트와 브라우저 검사기 추가

reveal 애니메이션, 모바일 내비, 헤더 스크롤 상태.
검사기는 3개 폭에서 가로 오버플로와 콘솔 에러를 잡는다."
```

---

## Task 5: 홈 본문 섹션

**Files:**
- Modify: `index.html` (히어로 뒤에 섹션 6개 추가)
- Modify: `assets/css/styles.css` (섹션별 스타일 추가)

**Interfaces:**
- Consumes: Task 3의 토큰·컴포넌트, Task 4의 `.reveal`
- Produces: `.stats` `.pillar` `.prog-list` `.quote` `.strip` `.cta-band` 클래스. Task 6~10이 재사용한다.

**콘텐츠 원칙:** 아래 문구를 그대로 쓴다. 새로운 사실을 만들어내지 않는다.

- [ ] **Step 1: `</section>` (히어로) 뒤에 Who We Are + 통계 추가**

```html
    <!-- ============== WHO WE ARE ============== -->
    <section class="section" id="who">
      <div class="wrap">
        <div class="panel reveal">
          <p class="eyebrow">Who we are</p>
          <h2>Rooted in Germany, <span class="marker">growing worldwide</span></h2>
          <p class="lead">Spring of Life began with missionary work from Germany. From those roots, SL has
            continued to expand internationally, reaching youth and communities across Africa, South America,
            and Asia &mdash; including Korea.</p>
          <p class="lead">Since 2014, SL has been on campuses in Korea encouraging young people to read the
            Bible for themselves. Today we work alongside international churches here, including New Hope
            Church and Shining Light Church.</p>
          <ul class="stats">
            <li><strong>2014</strong><span>In Korea since</span></li>
            <li><strong>3</strong><span>Continents reached</span></li>
            <li><strong>5</strong><span>Programs</span></li>
          </ul>
        </div>
      </div>
    </section>
```

CSS 추가:

```css
.stats {
  list-style: none;
  margin: clamp(24px, 4vw, 40px) 0 0;
  padding: 0;
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  border-top: 2px solid var(--ink);
  padding-top: clamp(20px, 3vw, 32px);
}
.stats li { display: grid; gap: 2px; }
.stats strong {
  font-family: var(--font-head);
  font-weight: 800;
  font-size: clamp(1.9rem, 4vw, 2.6rem);
  line-height: 1;
  color: var(--navy);
}
.stats span { font-size: .86rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
```

- [ ] **Step 2: Four Pillars 섹션 추가**

```html
    <!-- ============== FOUR PILLARS ============== -->
    <section class="section" id="pillars">
      <div class="wrap">
        <p class="eyebrow reveal">What we stand for</p>
        <h2 class="reveal">Four things we keep coming back to</h2>
        <div class="grid grid--auto">
          <article class="card pillar reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M7 20h10" /><path d="M12 20V9" />
                <path d="M12 9C12 6 9 4 6 4c0 3 2 5 6 5z" />
                <path d="M12 9c0-2.5 2.5-4.5 5.5-4.5 0 2.5-2 4.5-5.5 4.5z" /></svg>
            </span>
            <h3>Personal Growth</h3>
            <p>Developing ourselves through the Word and various activities, and applying it in our daily life.</p>
          </article>
          <article class="card pillar reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M2 4h6a4 4 0 014 4v12a3 3 0 00-3-3H2z" />
                <path d="M22 4h-6a4 4 0 00-4 4v12a3 3 0 013-3h7z" /></svg>
            </span>
            <h3>Putting the Word into Practice</h3>
            <p>Turning the Word into action in society, our community, and around the world.</p>
          </article>
          <article class="card pillar reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M3 12h18" />
                <path d="M12 3a15 15 0 010 18a15 15 0 010-18z" /></svg>
            </span>
            <h3>Creating Global Positive Influence</h3>
            <p>Inspiring positive change and making a meaningful impact globally through the Word.</p>
          </article>
          <article class="card pillar reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M20.8 5.6a5 5 0 00-7.1 0L12 7.3l-1.7-1.7a5 5 0 10-7.1 7.1L12 21.5l8.8-8.8a5 5 0 000-7.1z" />
              </svg>
            </span>
            <h3>Partners</h3>
            <p>We work alongside international churches in Korea, including New Hope Church and Shining Light Church.</p>
          </article>
        </div>
      </div>
    </section>
```

CSS 추가:

```css
.pillar { display: grid; gap: 12px; align-content: start; }
.pillar h3 { margin: 4px 0 0; color: var(--forest); }
.pillar p { margin: 0; color: var(--muted); }
```

- [ ] **Step 3: Programs 프리뷰 + Stories 프리뷰 추가**

```html
    <!-- ============== PROGRAMS PREVIEW ============== -->
    <section class="section section--navy" id="programs-preview">
      <div class="wrap">
        <p class="eyebrow reveal">Programs</p>
        <h2 class="reveal">Five ways to start</h2>
        <ul class="prog-list reveal">
          <li><strong>Bible Deep Dive</strong><span>Explore the Bible, one on one</span></li>
          <li><strong>Faith &amp; You</strong><span>Discover yourself through faith</span></li>
          <li><strong>Word &amp; Reflect</strong><span>Build a Bible reflection habit</span></li>
          <li><strong>Bible Mentoring</strong><span>Grow through biblical guidance</span></li>
          <li><strong>Finding Inner Peace</strong><span>Discover the roots of true peace</span></li>
        </ul>
        <p><a href="programs.html" class="btn">See all programs</a></p>
      </div>
    </section>

    <!-- ============== STORIES PREVIEW ============== -->
    <section class="section" id="stories-preview">
      <div class="wrap">
        <p class="eyebrow reveal">Stories</p>
        <h2 class="reveal">Testimony from our <span class="script">Seonbae (선배)</span></h2>
        <div class="grid grid--auto">
          <figure class="card quote reveal">
            <img src="assets/images/people/01.jpg" alt="Lorena from Brazil" width="88" height="88" />
            <blockquote>&ldquo;I was a non-believer, and I had a lot of doubts about religion and the Bible.
              But through SL, I started to see that the Bible actually makes sense and that God has a purpose
              for my life.&rdquo;</blockquote>
            <figcaption><strong>Lorena</strong> &middot; Brazil</figcaption>
          </figure>
          <figure class="card quote reveal">
            <img src="assets/images/people/03.jpg" alt="Mahdi from Iran" width="88" height="88" />
            <blockquote>&ldquo;I wasn&rsquo;t a Christian, but after learning God&rsquo;s Word through SL, I
              began to understand why I went through those experiences and realized how blessed I am.&rdquo;
            </blockquote>
            <figcaption><strong>Mahdi</strong> &middot; Iran</figcaption>
          </figure>
        </div>
        <p><a href="stories.html" class="btn">Read all four stories</a></p>
      </div>
    </section>
```

CSS 추가:

```css
.prog-list {
  list-style: none;
  margin: 0 0 clamp(24px, 4vw, 36px);
  padding: 0;
  display: grid;
  gap: 10px;
}
.prog-list li {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 14px;
  padding: 16px 22px;
  background: rgba(255, 255, 255, .07);
  border: 2px solid rgba(255, 255, 255, .28);
  border-radius: var(--radius-sm);
}
.prog-list strong { font-family: var(--font-head); font-size: 1.05rem; }
.prog-list span { color: rgba(255, 255, 255, .7); font-size: .94rem; }

.quote { display: grid; gap: 14px; align-content: start; margin: 0; }
.quote img { width: 88px; height: 88px; border-radius: 50%; object-fit: cover; border: 2px solid var(--ink); }
.quote blockquote { margin: 0; font-size: 1.02rem; }
.quote figcaption { font-size: .9rem; color: var(--muted); }
.quote figcaption strong { font-family: var(--font-head); color: var(--ink); }
```

- [ ] **Step 4: Events 스트립 + CTA 밴드 추가**

```html
    <!-- ============== EVENTS STRIP ============== -->
    <section class="section" id="events-preview">
      <div class="wrap">
        <p class="eyebrow reveal">Past events</p>
        <h2 class="reveal">We gather, and we talk about real things</h2>
        <ul class="strip reveal">
          <li><img src="assets/images/posters/01.png" alt="Trivia Night poster" /></li>
          <li><img src="assets/images/posters/02.png" alt="Movie Night poster" /></li>
          <li><img src="assets/images/posters/03.png" alt="Beyond Small Talk poster" /></li>
          <li><img src="assets/images/posters/04.png" alt="New Year Check-in poster" /></li>
          <li><img src="assets/images/posters/05.png" alt="New Year, New Me poster" /></li>
        </ul>
        <p><a href="events.html" class="btn">See past events</a></p>
      </div>
    </section>

    <!-- ============== CTA ============== -->
    <section class="section" id="start">
      <div class="wrap">
        <div class="panel cta-band reveal">
          <h2>Ready to <span class="marker">start</span>?</h2>
          <p class="lead">No background in the Bible required. Grow together with a mentor and find peace
            through God in just three sessions.</p>
          <div class="hero__actions">
            <a href="programs.html#start" class="btn btn--primary">How to start</a>
            <a href="contact.html" class="btn">Ask a question</a>
          </div>
        </div>
      </div>
    </section>
```

CSS 추가:

```css
.strip {
  list-style: none;
  margin: 0 0 clamp(24px, 4vw, 36px);
  padding: 0 0 8px;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(180px, 1fr);
  gap: 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
}
.strip li { scroll-snap-align: start; }
.strip img {
  width: 100%;
  aspect-ratio: 9 / 13;
  object-fit: cover;
  border: var(--border);
  border-radius: var(--radius-sm);
}

.cta-band { text-align: center; display: grid; gap: 16px; justify-items: center; }
.cta-band .lead { margin-inline: auto; }
```

**주의:** `.strip`은 가로 스크롤 컨테이너다. `overflow-x: auto`가 자기 안에서만 스크롤되므로 `<body>` 가로 오버플로를 만들지 않는다. Step 6 검사에서 이 점이 확인된다.

- [ ] **Step 5: 정적 검사**

```bash
python3 tools/verify.py .
```

기대: `about.html` `programs.html` `events.html` `stories.html` `contact.html` 파일 없음 오류 5건만 남는다.
이미지 경로·alt·앵커 오류는 0건이어야 한다.

```bash
python3 tools/verify.py . | grep -vE "about\.html|programs\.html|events\.html|stories\.html|contact\.html|발견" || echo "✓ 나머지 문제 없음"
```

- [ ] **Step 6: 브라우저 검사 + 시각 확인**

```bash
python3 tools/browser_check.py --shots /tmp/sl-shots
```

기대: `✓ 1개 페이지 × 3개 폭 통과`. 특히 360px에서 가로 오버플로가 없어야 한다.
Read 도구로 `/tmp/sl-shots/index.png`를 열어 전체 흐름을 확인한다.

- [ ] **Step 7: 커밋**

```bash
git add index.html assets/css/styles.css
git commit -m "feat: 홈 본문 섹션 구성

Who We Are·통계, Four Pillars, 프로그램 프리뷰,
간증 프리뷰, 행사 스트립, 시작 CTA."
```

---

## Task 6: About 페이지

**Files:**
- Create: `about.html`
- Modify: `assets/css/styles.css`

**Interfaces:**
- Consumes: Task 3 헤더/푸터 마크업, Task 5의 `.pillar` `.stats`
- Produces: `.journey` `.timeline` `.partner-list` 클래스

- [ ] **Step 1: `index.html`을 복사해 셸을 만든다**

```bash
cp index.html about.html
```

그다음 `about.html`에서:
1. `<title>`을 `About | Spring of Life`로
2. `<meta name="description">`을 `Spring of Life began with missionary work from Germany and now reaches youth across Africa, South America, and Asia. In Korea since 2014.`로
3. `<link rel="canonical">`을 `https://ondo1400-dotcom.github.io/SL/about.html`로
4. 헤더의 `<a class="nav__link" href="about.html">About</a>`에 `aria-current="page"` 추가
5. `<main>` 안의 모든 `<section>`을 삭제하고 아래 Step들의 내용으로 교체

- [ ] **Step 2: 히어로 + Who is SL 섹션**

```html
    <section class="hero">
      <div class="wrap">
        <div class="panel hero__panel">
          <p class="eyebrow">About us</p>
          <h1>Who is <span class="script">Spring of Life</span>?</h1>
          <p class="lead">A non-denominational Bible institution that has its roots in missionary work
            from Germany.</p>
        </div>
      </div>
    </section>

    <section class="section" id="roots">
      <div class="wrap">
        <div class="panel reveal">
          <p class="eyebrow">Our roots</p>
          <h2>It started in <span class="marker">Germany</span></h2>
          <p class="lead">Spring of Life is not tied to any single denomination. What holds us together is
            the Word itself &mdash; and the conviction that anyone can read it, question it, and find
            something true in it.</p>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Global Expansion 섹션 (지도 없이 카드 레이아웃)**

스펙 §4에 따라 세계지도 이미지나 SVG 지도는 만들지 않는다.

```html
    <section class="section section--navy" id="expansion">
      <div class="wrap">
        <p class="eyebrow reveal">Global expansion</p>
        <h2 class="reveal">From one place, outward</h2>
        <p class="lead reveal">From its roots in Germany, SL has continued to expand its work
          internationally, reaching youth and communities across the world.</p>
        <div class="journey reveal">
          <div class="journey__origin">
            <span class="journey__label">From</span>
            <strong>Germany</strong>
          </div>
          <ul class="journey__targets">
            <li><span class="journey__label">To</span><strong>Africa</strong></li>
            <li><span class="journey__label">To</span><strong>South America</strong></li>
            <li><span class="journey__label">To</span><strong>Asia</strong></li>
          </ul>
        </div>
      </div>
    </section>
```

CSS 추가:

```css
.journey {
  margin-top: clamp(24px, 4vw, 40px);
  display: grid;
  gap: clamp(18px, 3vw, 30px);
  grid-template-columns: minmax(180px, .8fr) 2fr;
  align-items: center;
}
@media (max-width: 720px) { .journey { grid-template-columns: 1fr; } }

.journey__origin {
  display: grid;
  gap: 4px;
  padding: clamp(20px, 3vw, 28px);
  border: 2px solid var(--teal);
  border-radius: var(--radius);
  background: rgba(127, 207, 212, .12);
}
.journey__origin strong { font-family: var(--font-head); font-size: 1.6rem; }

.journey__targets {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}
.journey__targets li {
  display: grid;
  gap: 4px;
  padding: 18px 20px;
  border: 2px solid rgba(255, 255, 255, .28);
  border-radius: var(--radius-sm);
}
.journey__targets strong { font-family: var(--font-head); font-size: 1.15rem; }

.journey__label {
  font-size: .74rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--teal);
}
```

- [ ] **Step 4: Since 2014 in Korea + Mission & Vision**

```html
    <section class="section" id="korea">
      <div class="wrap">
        <div class="panel reveal">
          <p class="eyebrow">In Korea</p>
          <h2>Since <span class="marker">2014</span></h2>
          <ol class="timeline">
            <li>
              <h3>On campus</h3>
              <p>SL started on campuses in Korea to encourage Bible reading among young people.</p>
            </li>
            <li>
              <h3>Alongside churches</h3>
              <p>SL has since branched out to cooperate with various international churches in Korea,
                including New Hope Church and Shining Light Church.</p>
            </li>
            <li>
              <h3>In Hongdae and beyond</h3>
              <p>Our gatherings &mdash; movie nights, trivia nights, honest conversations &mdash; have
                brought together people from all over the world.</p>
            </li>
          </ol>
        </div>
      </div>
    </section>

    <section class="section" id="mission">
      <div class="wrap">
        <div class="grid grid--auto">
          <div class="card reveal">
            <p class="eyebrow">Mission</p>
            <p>SL and its volunteers aim to achieve personal growth through various activities by putting
              the Word into practice in society, their daily life, and around the world.</p>
          </div>
          <div class="card reveal">
            <p class="eyebrow">Vision</p>
            <p>SL is a global organization seeking to create positive influence through the Word.</p>
          </div>
        </div>
      </div>
    </section>
```

CSS 추가:

```css
.timeline { list-style: none; margin: clamp(20px, 3vw, 32px) 0 0; padding: 0; display: grid; gap: 0; }
.timeline li {
  position: relative;
  padding: 0 0 clamp(24px, 3vw, 34px) clamp(28px, 4vw, 40px);
  border-left: 2px solid var(--teal);
}
.timeline li:last-child { border-left-color: transparent; padding-bottom: 0; }
.timeline li::before {
  content: "";
  position: absolute;
  left: -9px; top: 4px;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: var(--sun);
  border: 2px solid var(--ink);
}
.timeline h3 { margin: 0 0 6px; color: var(--forest); }
.timeline p { margin: 0; color: var(--muted); }
```

- [ ] **Step 5: Four Pillars(홈과 동일 마크업) + Partners 섹션을 이어 붙인다**

`index.html`의 Four Pillars `<section>` 전체를 복사해 붙인다. 그 뒤에:

```html
    <section class="section" id="partners">
      <div class="wrap">
        <div class="panel reveal">
          <p class="eyebrow">Partners</p>
          <h2>We don&rsquo;t do this alone</h2>
          <ul class="partner-list">
            <li>New Hope Church</li>
            <li>Shining Light Church</li>
            <li>and others</li>
          </ul>
        </div>
      </div>
    </section>
```

CSS 추가:

```css
.partner-list {
  list-style: none;
  margin: clamp(18px, 3vw, 28px) 0 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.partner-list li {
  font-family: var(--font-head);
  font-weight: 600;
  padding: 12px 22px;
  border: var(--border);
  border-radius: 999px;
  background: var(--sun);
}
```

- [ ] **Step 6: 검사**

```bash
python3 tools/verify.py .
python3 tools/browser_check.py --shots /tmp/sl-shots
```

기대: verify는 남은 4개 페이지 파일 없음 오류만, browser_check는 `✓ 2개 페이지 × 3개 폭 통과`.
Read 도구로 `/tmp/sl-shots/about.png` 확인.

- [ ] **Step 7: 커밋**

```bash
git add about.html assets/css/styles.css
git commit -m "feat: About 페이지 추가

독일 뿌리, 글로벌 확장(카드 레이아웃), 2014년 한국 타임라인,
Mission & Vision, Four Pillars, 파트너 교회."
```

---

## Task 7: Programs 페이지

**Files:**
- Create: `programs.html`
- Modify: `assets/css/styles.css`

**Interfaces:**
- Consumes: Task 3 셸, Task 5의 `.chip` 아이콘 SVG
- Produces: `.prog-card` `.steps` 클래스, `#start` 앵커 (홈의 `programs.html#start` 링크 대상)

- [ ] **Step 1: 셸 준비**

```bash
cp about.html programs.html
```

`programs.html`에서 `<title>` → `Programs | Spring of Life`,
description → `Five programs to explore the Bible: Bible Deep Dive, Faith & You, Word & Reflect, Bible Mentoring, and Finding Inner Peace.`,
canonical → `https://ondo1400-dotcom.github.io/SL/programs.html`,
`aria-current="page"`를 About에서 Programs로 옮기고, `<main>` 내용을 교체한다.

- [ ] **Step 2: 히어로 + 프로그램 5종 카드**

```html
    <section class="hero">
      <div class="wrap">
        <div class="panel hero__panel">
          <p class="eyebrow">Programs</p>
          <h1>How we walk with <span class="script">the youth</span></h1>
          <p class="lead">Five ways in. Pick the one that sounds like you &mdash; or tell us where you are
            and we&rsquo;ll help you choose.</p>
        </div>
      </div>
    </section>

    <section class="section" id="list">
      <div class="wrap">
        <div class="grid grid--auto">

          <article class="card prog-card reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M12 2.7l5.7 5.7a8 8 0 11-11.3 0z" /></svg>
            </span>
            <div>
              <h3>Bible Deep Dive</h3>
              <p class="prog-card__sub">Explore the Bible, one on one</p>
              <p>Go through the text with someone who has read it closely. Bring your questions &mdash;
                especially the uncomfortable ones.</p>
            </div>
          </article>

          <article class="card prog-card reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M10 3h4v5h5v4h-5v9h-4v-9H5V8h5z" /></svg>
            </span>
            <div>
              <h3>Faith &amp; You</h3>
              <p class="prog-card__sub">Discover yourself through faith</p>
              <p>Less about doctrine, more about you. What you believe, why you believe it, and what that
                means for the life you&rsquo;re actually living.</p>
            </div>
          </article>

          <article class="card prog-card reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><rect x="3.5" y="3" width="7" height="18" rx="1.5" />
                <rect x="13.5" y="3" width="7" height="18" rx="1.5" /></svg>
            </span>
            <div>
              <h3>Word &amp; Reflect</h3>
              <p class="prog-card__sub">Build a Bible reflection habit</p>
              <p>A rhythm you can keep. Short readings, honest reflection, and a group that notices when
                you go quiet.</p>
            </div>
          </article>

          <article class="card prog-card reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M2 4h6a4 4 0 014 4v12a3 3 0 00-3-3H2z" />
                <path d="M22 4h-6a4 4 0 00-4 4v12a3 3 0 013-3h7z" /></svg>
            </span>
            <div>
              <h3>Bible Mentoring</h3>
              <p class="prog-card__sub">Grow through biblical guidance</p>
              <p>One mentor, over time. Someone who knows your name, your story, and where you said you
                wanted to go.</p>
            </div>
          </article>

          <article class="card prog-card reveal">
            <span class="chip" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M20.2 12.2a6 6 0 00-8.5-8.5L5 10.5V19h8.5z" />
                <path d="M16 8L2 22" /></svg>
            </span>
            <div>
              <h3>Finding Inner Peace</h3>
              <p class="prog-card__sub">Discover the roots of true peace</p>
              <p>Start here if you&rsquo;re tired. Three sessions on where peace actually comes from, and
                why it keeps slipping away.</p>
            </div>
          </article>

        </div>
      </div>
    </section>
```

CSS 추가:

```css
.prog-card { display: flex; gap: 18px; align-items: flex-start; }
.prog-card h3 { margin: 0 0 2px; color: var(--forest); }
.prog-card p { margin: 0 0 .6em; }
.prog-card p:last-child { margin-bottom: 0; }
.prog-card__sub {
  font-family: var(--font-head);
  font-weight: 600;
  font-size: .84rem;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--muted);
}
```

- [ ] **Step 3: How to Start 3스텝 + CTA**

```html
    <section class="section section--navy" id="start">
      <div class="wrap">
        <p class="eyebrow reveal">How to start</p>
        <h2 class="reveal">Three steps, no pressure</h2>
        <ol class="steps">
          <li class="reveal">
            <span class="steps__num">01</span>
            <h3>Reach out</h3>
            <p>Tell us what you&rsquo;re looking for. No background in the Bible is required, and you
              don&rsquo;t have to call yourself a believer.</p>
          </li>
          <li class="reveal">
            <span class="steps__num">02</span>
            <h3>Meet a mentor</h3>
            <p>We match you with a mentor and find a time that fits your week.</p>
          </li>
          <li class="reveal">
            <span class="steps__num">03</span>
            <h3>Grow together</h3>
            <p>Start with three sessions. After that, it&rsquo;s up to you how far you want to go.</p>
          </li>
        </ol>
        <p class="reveal">
          <a href="#" class="btn btn--primary">Apply now</a>
          <a href="contact.html" class="btn">Ask first</a>
        </p>
      </div>
    </section>
```

**자리표시자 주의:** `Apply now`의 `href="#"`는 의도된 자리표시자다(스펙 §12). 링크 확정 시 교체한다.
`tools/verify.py`는 `#`만 있는 href를 건너뛰므로 검사에 걸리지 않는다.

CSS 추가:

```css
.steps {
  list-style: none;
  margin: clamp(24px, 4vw, 40px) 0 clamp(24px, 4vw, 36px);
  padding: 0;
  display: grid;
  gap: clamp(16px, 2.4vw, 26px);
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  counter-reset: step;
}
.steps li {
  display: grid;
  gap: 8px;
  align-content: start;
  padding: clamp(20px, 2.6vw, 30px);
  border: 2px solid rgba(255, 255, 255, .28);
  border-radius: var(--radius);
}
.steps__num {
  font-family: var(--font-head);
  font-weight: 800;
  font-size: 1.9rem;
  line-height: 1;
  color: var(--teal);
}
.steps h3 { margin: 0; }
.steps p { margin: 0; color: rgba(255, 255, 255, .74); }
```

- [ ] **Step 4: 검사**

```bash
python3 tools/verify.py .
python3 tools/browser_check.py --shots /tmp/sl-shots
```

기대: browser_check `✓ 3개 페이지 × 3개 폭 통과`.
verify에서 `index.html: 앵커 대상 없음 — #start` 같은 오류가 나오면 안 된다
(홈의 링크는 `programs.html#start`이고 이 페이지에 `id="start"`가 있다).
`/tmp/sl-shots/programs.png` 확인.

- [ ] **Step 5: 커밋**

```bash
git add programs.html assets/css/styles.css
git commit -m "feat: Programs 페이지 추가

프로그램 5종 카드와 How to Start 3단계.
신청 버튼은 링크 확정 전까지 자리표시자."
```

---

## Task 8: Events 페이지 + 라이트박스

**Files:**
- Create: `events.html`
- Modify: `assets/css/styles.css`
- Modify: `assets/js/script.js` (라이트박스 모듈 **추가**, 기존 코드 유지)

**Interfaces:**
- Consumes: `assets/images/posters/01~05.png`, `assets/images/gallery/01~05.jpg` (Task 1), Task 4의 IIFE 구조
- Produces: `.poster-grid` `.gallery` `.lightbox` 클래스와 `#lightbox` 요소

**행사 정보 출처:** PPT 5쪽 포스터에 인쇄된 문구. 아래 값만 사용하고 추측을 더하지 않는다.

| 포스터 | 제목 | 세부 |
|---|---|---|
| 01 | Trivia Night | Topic: The Chosen · Sept 27, 7:30PM · Hongdae · Sponsored by NHC |
| 02 | Movie Night | Saturday, February 25 · 5PM · PJ Hotel, Mareunnae-ro 61-5 |
| 03 | Beyond Small Talk | January 24 · 6:00PM · Hongdae |
| 04 | New Year Check-in | Saturday, February 21 · 6:30PM · Hongdae |
| 05 | New Year, New Me: The Path to Happiness | January 18, 2025 · 5PM · Hongdae |

- [ ] **Step 1: 셸 준비 후 포스터 그리드 작성**

```bash
cp programs.html events.html
```

`<title>` → `Past Events | Spring of Life`,
description → `Trivia nights, movie nights, and honest conversations — a look back at Spring of Life gatherings in Hongdae, Seoul.`,
canonical → `https://ondo1400-dotcom.github.io/SL/events.html`,
`aria-current="page"`를 Events로 옮기고 `<main>` 교체:

```html
    <section class="hero">
      <div class="wrap">
        <div class="panel hero__panel">
          <p class="eyebrow">Past events</p>
          <h1>Our past <span class="script">events</span></h1>
          <p class="lead">Trivia nights, movie nights, and conversations that went past small talk.
            Mostly in Hongdae, mostly on a Saturday.</p>
        </div>
      </div>
    </section>

    <section class="section" id="archive">
      <div class="wrap">
        <p class="eyebrow reveal">Posters</p>
        <h2 class="reveal">What we&rsquo;ve been up to</h2>
        <ul class="poster-grid">
          <li class="reveal">
            <button type="button" class="poster" data-full="assets/images/posters/01.png"
              data-caption="Trivia Night — Topic: The Chosen">
              <img src="assets/images/posters/01.png" alt="Trivia Night poster" />
            </button>
            <h3>Trivia Night</h3>
            <p>Topic: The Chosen &middot; Sept 27, 7:30PM &middot; Hongdae</p>
          </li>
          <li class="reveal">
            <button type="button" class="poster" data-full="assets/images/posters/02.png"
              data-caption="Movie Night">
              <img src="assets/images/posters/02.png" alt="Movie Night poster" />
            </button>
            <h3>Movie Night</h3>
            <p>Saturday, February 25 &middot; 5PM &middot; PJ Hotel, Mareunnae-ro 61-5</p>
          </li>
          <li class="reveal">
            <button type="button" class="poster" data-full="assets/images/posters/03.png"
              data-caption="Beyond Small Talk">
              <img src="assets/images/posters/03.png" alt="Beyond Small Talk poster" />
            </button>
            <h3>Beyond Small Talk</h3>
            <p>January 24 &middot; 6:00PM &middot; Hongdae</p>
          </li>
          <li class="reveal">
            <button type="button" class="poster" data-full="assets/images/posters/04.png"
              data-caption="New Year Check-in">
              <img src="assets/images/posters/04.png" alt="New Year Check-in poster" />
            </button>
            <h3>New Year Check-in</h3>
            <p>Saturday, February 21 &middot; 6:30PM &middot; Hongdae</p>
          </li>
          <li class="reveal">
            <button type="button" class="poster" data-full="assets/images/posters/05.png"
              data-caption="New Year, New Me: The Path to Happiness">
              <img src="assets/images/posters/05.png" alt="New Year, New Me poster" />
            </button>
            <h3>New Year, New Me</h3>
            <p>The Path to Happiness &middot; January 18, 2025 &middot; 5PM &middot; Hongdae</p>
          </li>
        </ul>
      </div>
    </section>

    <section class="section" id="gallery">
      <div class="wrap">
        <p class="eyebrow reveal">In the room</p>
        <h2 class="reveal">Photos from our gatherings</h2>
        <ul class="gallery reveal">
          <li><img src="assets/images/gallery/01.jpg" alt="Participants gathered around tables at a Spring of Life event" loading="lazy" /></li>
          <li><img src="assets/images/gallery/02.jpg" alt="A Spring of Life evening gathering with a screen and candlelit tables" loading="lazy" /></li>
          <li><img src="assets/images/gallery/03.jpg" alt="Attendees watching a presentation at a Spring of Life gathering" loading="lazy" /></li>
          <li><img src="assets/images/gallery/04.jpg" alt="Participants talking in small groups" loading="lazy" /></li>
          <li><img src="assets/images/gallery/05.jpg" alt="A long table of participants during a Spring of Life session" loading="lazy" /></li>
        </ul>
      </div>
    </section>

    <section class="section" id="next">
      <div class="wrap">
        <div class="panel cta-band reveal">
          <h2>Want to be at the <span class="marker">next one</span>?</h2>
          <p class="lead">Our next gathering hasn&rsquo;t been announced yet. Get in touch and we&rsquo;ll
            let you know when it is.</p>
          <p><a href="contact.html" class="btn btn--primary">Get in touch</a></p>
        </div>
      </div>
    </section>
```

`</main>` 바로 앞에 라이트박스 컨테이너를 넣는다:

```html
  </main>

  <div class="lightbox" id="lightbox" hidden role="dialog" aria-modal="true" aria-label="Event poster">
    <button type="button" class="lightbox__close" id="lightboxClose" aria-label="Close">&times;</button>
    <figure class="lightbox__figure">
      <img id="lightboxImg" src="" alt="" />
      <figcaption id="lightboxCap"></figcaption>
    </figure>
  </div>
```

- [ ] **Step 2: CSS 추가**

```css
.poster-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: clamp(18px, 2.6vw, 28px);
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
.poster-grid h3 { margin: 14px 0 2px; font-size: 1.05rem; }
.poster-grid p { margin: 0; font-size: .88rem; color: var(--muted); }

.poster {
  display: block;
  width: 100%;
  padding: 0;
  border: var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--paper);
  cursor: zoom-in;
  transition: transform .25s var(--ease);
}
.poster:hover { transform: translateY(-3px); }
.poster:focus-visible { outline: 3px solid var(--navy); outline-offset: 3px; }
.poster img { width: 100%; aspect-ratio: 9 / 13; object-fit: cover; }

.gallery {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: clamp(12px, 2vw, 20px);
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.gallery img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border: var(--border);
  border-radius: var(--radius-sm);
}

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: clamp(20px, 5vw, 56px);
  background: rgba(7, 42, 66, .92);
}
.lightbox[hidden] { display: none; }
.lightbox__figure { margin: 0; display: grid; gap: 14px; justify-items: center; max-height: 100%; }
.lightbox__figure img {
  max-width: min(560px, 100%);
  max-height: 76vh;
  width: auto;
  border-radius: var(--radius-sm);
  border: 2px solid var(--paper);
}
.lightbox__figure figcaption {
  color: var(--paper);
  font-family: var(--font-head);
  font-weight: 600;
  text-align: center;
}
.lightbox__close {
  position: absolute;
  top: clamp(12px, 3vw, 24px);
  right: clamp(12px, 3vw, 24px);
  width: 48px; height: 48px;
  font-size: 1.8rem;
  line-height: 1;
  color: var(--ink);
  background: var(--paper);
  border: var(--border);
  border-radius: 50%;
  cursor: pointer;
}
body.is-locked { overflow: hidden; }
```

- [ ] **Step 3: `assets/js/script.js`에 라이트박스 모듈 추가**

`initHeaderState` 함수 **뒤**, `document.addEventListener('DOMContentLoaded', ...)` **앞**에 삽입한다.
기존 함수는 건드리지 않는다.

```javascript
  /* --- Poster lightbox --- */
  function initLightbox() {
    var box = document.getElementById('lightbox');
    var img = document.getElementById('lightboxImg');
    var cap = document.getElementById('lightboxCap');
    var closeBtn = document.getElementById('lightboxClose');
    var triggers = document.querySelectorAll('.poster');
    if (!box || !img || !cap || !closeBtn || !triggers.length) return;

    var lastFocused = null;

    function open(trigger) {
      lastFocused = trigger;
      img.src = trigger.getAttribute('data-full');
      img.alt = trigger.getAttribute('data-caption') || '';
      cap.textContent = trigger.getAttribute('data-caption') || '';
      box.hidden = false;
      document.body.classList.add('is-locked');
      closeBtn.focus();
    }

    function close() {
      box.hidden = true;
      img.src = '';
      document.body.classList.remove('is-locked');
      if (lastFocused) lastFocused.focus();
    }

    triggers.forEach(function (trigger) {
      trigger.addEventListener('click', function () { open(trigger); });
    });

    closeBtn.addEventListener('click', close);

    box.addEventListener('click', function (e) {
      if (e.target === box) close();
    });

    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') { close(); return; }
      if (e.key === 'Tab') { e.preventDefault(); closeBtn.focus(); }
    });
  }
```

`DOMContentLoaded` 핸들러에 `initLightbox();` 한 줄을 추가한다.

- [ ] **Step 4: 라이트박스 동작 검증**

```bash
python3 - <<'PY'
import http.server, socketserver, threading
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright

handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(Path.cwd()))
httpd = socketserver.TCPServer(("127.0.0.1", 8767), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://127.0.0.1:8767/events.html", wait_until="networkidle")
    assert pg.locator("#lightbox").is_hidden(), "초기에 라이트박스가 열려 있음"
    pg.locator(".poster").first.click()
    assert pg.locator("#lightbox").is_visible(), "포스터 클릭해도 안 열림"
    assert "Trivia" in pg.text_content("#lightboxCap"), "캡션이 안 들어감"
    assert pg.evaluate("getComputedStyle(document.body).overflow") == "hidden", "스크롤 잠금 안 됨"
    pg.keyboard.press("Escape")
    assert pg.locator("#lightbox").is_hidden(), "ESC로 안 닫힘"
    assert pg.evaluate("getComputedStyle(document.body).overflow") != "hidden", "스크롤 잠금 안 풀림"
    pg.locator(".poster").nth(1).click()
    pg.click("#lightbox", position={"x": 5, "y": 5})
    assert pg.locator("#lightbox").is_hidden(), "배경 클릭으로 안 닫힘"
    print("✓ 라이트박스 열기/캡션/스크롤잠금/ESC/배경클릭 정상")
    b.close()
httpd.shutdown()
PY
```

기대: `✓ 라이트박스 열기/캡션/스크롤잠금/ESC/배경클릭 정상`

- [ ] **Step 5: 전체 검사**

```bash
python3 tools/verify.py .
python3 tools/browser_check.py --shots /tmp/sl-shots
```

기대: browser_check `✓ 4개 페이지 × 3개 폭 통과`. `/tmp/sl-shots/events.png` 확인.

- [ ] **Step 6: 커밋**

```bash
git add events.html assets/css/styles.css assets/js/script.js
git commit -m "feat: Events 페이지와 포스터 라이트박스 추가

포스터 5장 아카이브, 현장 사진 갤러리, 다음 행사 안내.
라이트박스는 ESC·배경 클릭으로 닫히고 스크롤을 잠근다."
```

---

## Task 9: Stories 페이지

**Files:**
- Create: `stories.html`
- Modify: `assets/css/styles.css`

**Interfaces:**
- Consumes: `assets/images/people/01~04.jpg` (Task 1), `_archive/asset-map.md`의 인물 매핑
- Produces: `.story` 클래스

**콘텐츠:** 사용자 제공 SL Concept 텍스트의 **전문**을 쓴다. PPT의 축약본이 아니다.
원문의 `oversees`는 `overseas`의 오타이므로 바로잡는다. 그 외 표현은 손대지 않는다.

- [ ] **Step 1: 셸 준비**

```bash
cp events.html stories.html
```

`stories.html`에서 `<title>` → `Stories | Spring of Life`,
description → `Four people from Brazil, Chile, Indonesia, and Iran on what changed for them through Spring of Life.`,
canonical → `https://ondo1400-dotcom.github.io/SL/stories.html`,
`aria-current="page"`를 Stories로 옮긴다.
**`</main>` 뒤의 `<div class="lightbox">` 블록을 삭제한다** (이 페이지에는 포스터가 없다).
`<main>` 내용을 아래로 교체한다.

- [ ] **Step 2: 히어로 + 간증 4편**

```html
    <section class="hero">
      <div class="wrap">
        <div class="panel hero__panel">
          <p class="eyebrow">Stories</p>
          <h1>Testimony from our <span class="script">Seonbae (선배)</span></h1>
          <p class="lead">Four people who came to Korea, met Spring of Life, and left with something they
            didn&rsquo;t arrive with.</p>
        </div>
      </div>
    </section>

    <section class="section" id="stories">
      <div class="wrap">

        <article class="card story reveal">
          <img src="assets/images/people/01.jpg" alt="Lorena from Brazil" width="140" height="140" loading="lazy" />
          <div>
            <h2>Lorena</h2>
            <p class="story__from">Brazil</p>
            <p>I was a non-believer, and I had a lot of doubts about religion and the Bible. But through SL,
              I started to see that the Bible actually makes sense and that God has a purpose for my life.
              Now I&rsquo;m doing many activities together with other believers and helping others find
              their purpose. Looking back, I feel like coming to Korea happened for a reason. It was a good
              experience. I miss everyone.</p>
          </div>
        </article>

        <article class="card story reveal">
          <img src="assets/images/people/04.jpg" alt="Jenny from Chile" width="140" height="140" loading="lazy" />
          <div>
            <h2>Jenny</h2>
            <p class="story__from">Chile</p>
            <p>The world for me was depressing and hopeless. There were many times when I wanted to give up,
              but through SL, I learned that this world was not created according to God&rsquo;s will, and
              that we have a role in rebuilding it, starting from my inner self. I also gained the tools and
              confidence to prepare for mission work back in my country. Now, I want to give back by
              supporting SL&rsquo;s work and helping others find the same hope I found. Fighting!</p>
          </div>
        </article>

        <article class="card story reveal">
          <img src="assets/images/people/02.jpg" alt="Gracia from Indonesia" width="140" height="140" loading="lazy" />
          <div>
            <h2>Gracia</h2>
            <p class="story__from">Indonesia</p>
            <p>I used to be stressed and overwhelmed, often relying on distractions to cope. Through SL and
              guidance from my mentor, I learned that true peace comes from knowing God through the Bible.
              It wasn&rsquo;t an easy journey, but it changed me. Now, we&rsquo;ve started an organization in
              Indonesia along with others who share the same heart, and we donate to SL to help more people
              experience what we did.</p>
          </div>
        </article>

        <article class="card story reveal">
          <img src="assets/images/people/03.jpg" alt="Mahdi from Iran" width="140" height="140" loading="lazy" />
          <div>
            <h2>Mahdi</h2>
            <p class="story__from">Iran</p>
            <p>I have lived overseas as a refugee, so I often questioned God and why I had to go through so
              many hardships. I wasn&rsquo;t a Christian, but after learning God&rsquo;s Word through SL, I
              began to understand why I went through those experiences and realized how blessed I am. Now, I
              want to give back to SL and support the people in my country, just as SL supported me and
              helped change my life.</p>
          </div>
        </article>

      </div>
    </section>

    <section class="section" id="yours">
      <div class="wrap">
        <div class="panel cta-band reveal">
          <h2>Your story could be <span class="marker">next</span></h2>
          <p class="lead">Every one of these started with a single conversation.</p>
          <div class="hero__actions">
            <a href="programs.html#start" class="btn btn--primary">How to start</a>
            <a href="contact.html" class="btn">Get in touch</a>
          </div>
        </div>
      </div>
    </section>
```

**중요:** `people/01~04`가 Lorena/Gracia/Mahdi/Jenny 순이라는 전제로 위 마크업을 썼다
(Task 1 Step 5의 `_archive/asset-map.md` 참조). 매핑이 다르면 **파일이 아니라 `src` 값을 고친다.**

CSS 추가:

```css
.story {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: clamp(20px, 3vw, 34px);
  align-items: start;
  margin-bottom: clamp(18px, 2.6vw, 28px);
}
.story:last-of-type { margin-bottom: 0; }
@media (max-width: 640px) { .story { grid-template-columns: 1fr; justify-items: start; } }

.story img {
  width: 140px; height: 140px;
  border-radius: 50%;
  object-fit: cover;
  border: var(--border);
}
.story h2 { margin: 0 0 2px; font-size: clamp(1.3rem, 2.6vw, 1.7rem); }
.story__from {
  font-family: var(--font-head);
  font-weight: 600;
  font-size: .8rem;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--forest);
  background: var(--sun);
  display: inline-block;
  padding: 3px 12px;
  border-radius: 999px;
  margin-bottom: 14px;
}
.story p:last-child { margin-bottom: 0; }
```

- [ ] **Step 3: 인물 사진과 이름이 맞는지 눈으로 확인**

```bash
python3 tools/browser_check.py --shots /tmp/sl-shots
```

Read 도구로 `/tmp/sl-shots/stories.png`를 열어 **각 사진과 이름·국가가 맞는지** 확인한다.
`_archive/asset-map.md`와 대조한다. 틀리면 `src` 값을 교체하고 다시 확인한다.

- [ ] **Step 4: 정적 검사**

```bash
python3 tools/verify.py .
```

기대: `contact.html` 파일 없음 오류만 남는다.

- [ ] **Step 5: 커밋**

```bash
git add stories.html assets/css/styles.css
git commit -m "feat: Stories 페이지 추가

Lorena·Jenny·Gracia·Mahdi 4인의 간증 전문.
PPT 축약본이 아닌 원본 텍스트 사용."
```

---

## Task 10: Contact 페이지

**Files:**
- Create: `contact.html`
- Modify: `assets/css/styles.css`

**Interfaces:**
- Consumes: Task 3 셸
- Produces: `.faq` 클래스

**사실 제약:** 연락처는 확정된 것이 없다(스펙 §12). **전화번호를 넣지 않는다** — PPT의 번호는 개인 번호일 수 있다.
FAQ 답변은 원본 자료에서 도출 가능한 것만 쓴다. 가격·시간표·정원 등 근거 없는 정보를 만들지 않는다.

- [ ] **Step 1: 셸 준비**

```bash
cp stories.html contact.html
```

`<title>` → `Get in Touch | Spring of Life`,
description → `Questions about Spring of Life? Reach out and we will help you find the right place to start.`,
canonical → `https://ondo1400-dotcom.github.io/SL/contact.html`,
`aria-current="page"`를 헤더 내비에서 **제거한다** (Contact는 `.btn`이라 내비 항목이 아니다).
`<main>` 교체.

- [ ] **Step 2: 히어로 + 문의 안내 + FAQ**

```html
    <section class="hero">
      <div class="wrap">
        <div class="panel hero__panel">
          <p class="eyebrow">Contact</p>
          <h1>Get in <span class="script">touch</span></h1>
          <p class="lead">Not sure where you&rsquo;d fit? Tell us roughly where you are and we&rsquo;ll
            point you somewhere reasonable.</p>
        </div>
      </div>
    </section>

    <section class="section" id="reach">
      <div class="wrap">
        <div class="grid grid--auto">
          <div class="card reveal">
            <p class="eyebrow">Where we meet</p>
            <h3>Hongdae, Seoul</h3>
            <p>Most of our gatherings have been held in Hongdae. One-on-one sessions are arranged at a time
              and place that works for you.</p>
          </div>
          <div class="card reveal">
            <p class="eyebrow">Reach out</p>
            <h3>Contact details coming soon</h3>
            <p>We&rsquo;re finalising a single point of contact. In the meantime, if you found us through a
              campus event or a partner church, ask the person who introduced you.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="faq">
      <div class="wrap">
        <div class="panel reveal">
          <p class="eyebrow">FAQ</p>
          <h2>Questions people actually ask</h2>
          <dl class="faq">
            <dt>Do I need to be a Christian to join?</dt>
            <dd>No. Several of the people whose stories are on this site described themselves as
              non-believers when they started, and some had never opened a Bible before.</dd>

            <dt>Which denomination are you?</dt>
            <dd>None. Spring of Life is non-denominational. We cooperate with a range of international
              churches in Korea, including New Hope Church and Shining Light Church.</dd>

            <dt>How long does it take?</dt>
            <dd>Programs like Finding Inner Peace start with three sessions. After that, how far you go is
              up to you.</dd>

            <dt>Where did Spring of Life come from?</dt>
            <dd>SL has its roots in missionary work from Germany, and has since expanded to Africa, South
              America, and Asia. We have been in Korea since 2014.</dd>
          </dl>
        </div>
      </div>
    </section>
```

CSS 추가:

```css
.faq { margin: clamp(20px, 3vw, 32px) 0 0; }
.faq dt {
  font-family: var(--font-head);
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--navy);
  padding-top: clamp(18px, 2.4vw, 26px);
  border-top: 1px solid rgba(26, 26, 26, .14);
  margin-top: clamp(18px, 2.4vw, 26px);
}
.faq dt:first-child { border-top: 0; margin-top: 0; padding-top: 0; }
.faq dd { margin: 8px 0 0; color: var(--muted); }
```

- [ ] **Step 3: 전체 검사 — 이제 오류가 0건이어야 한다**

```bash
python3 tools/verify.py .
```

기대: `✓ 6개 페이지 통과 (링크 · alt · 앵커)`, exit 0.
**여기서 처음으로 완전 통과가 나와야 한다.** 남은 오류가 있으면 전부 고친다.

```bash
python3 tools/browser_check.py --shots /tmp/sl-shots
```

기대: `✓ 6개 페이지 × 3개 폭 통과`.

- [ ] **Step 4: 커밋**

```bash
git add contact.html assets/css/styles.css
git commit -m "feat: Contact 페이지 추가

위치 안내, 연락처 자리표시자, FAQ 4항목.
FAQ 답변은 원본 자료에서 도출 가능한 내용만 사용."
```

---

## Task 11: SEO 마감 · 최종 검증 · 배포

**Files:**
- Create: `README.md`, `robots.txt`, `sitemap.xml`
- Modify: 6개 HTML 전부 (OG/Twitter 메타 추가, `index.html`에 JSON-LD)

**Interfaces:**
- Consumes: 앞선 모든 Task
- Produces: 배포 가능한 완성 사이트

- [ ] **Step 1: 6개 페이지에 OG/Twitter 메타 추가**

각 HTML의 `<link rel="canonical">` 바로 뒤에 삽입한다. `PAGE`, `TITLE`, `DESC`는 페이지별 값으로 바꾼다.

```html
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://ondo1400-dotcom.github.io/SL/PAGE" />
  <meta property="og:title" content="TITLE" />
  <meta property="og:description" content="DESC" />
  <meta property="og:image" content="https://ondo1400-dotcom.github.io/SL/assets/images/logo.png" />
  <meta property="og:site_name" content="Spring of Life" />
  <meta property="og:locale" content="en_US" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="TITLE" />
  <meta name="twitter:description" content="DESC" />
  <meta name="twitter:image" content="https://ondo1400-dotcom.github.io/SL/assets/images/logo.png" />
```

| 페이지 | `PAGE` 값 |
|---|---|
| index.html | (빈 문자열 — 루트 URL) |
| about.html | `about.html` |
| programs.html | `programs.html` |
| events.html | `events.html` |
| stories.html | `stories.html` |
| contact.html | `contact.html` |

`TITLE`/`DESC`는 각 페이지의 `<title>`/`<meta name="description">`과 같은 값을 쓴다.

- [ ] **Step 2: `index.html`에만 JSON-LD 추가**

`</head>` 바로 앞:

```html
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Spring of Life",
    "alternateName": "SL",
    "url": "https://ondo1400-dotcom.github.io/SL/",
    "logo": "https://ondo1400-dotcom.github.io/SL/assets/images/logo.png",
    "description": "A non-denominational Bible institution rooted in missionary work from Germany, reaching youth and communities across Africa, South America, and Asia. In Korea since 2014.",
    "foundingLocation": { "@type": "Place", "name": "Germany" },
    "areaServed": ["Germany", "Africa", "South America", "Asia", "South Korea"],
    "address": { "@type": "PostalAddress", "addressLocality": "Seoul", "addressCountry": "KR" }
  }
  </script>
```

JSON 유효성 확인:

```bash
python3 -c "
import json, re, pathlib
html = pathlib.Path('index.html').read_text(encoding='utf-8')
block = re.search(r'<script type=\"application/ld\+json\">(.*?)</script>', html, re.S).group(1)
json.loads(block)
print('✓ JSON-LD 유효')
"
```

- [ ] **Step 3: `robots.txt`와 `sitemap.xml` 작성**

`robots.txt`:

```
User-agent: *
Allow: /

Sitemap: https://ondo1400-dotcom.github.io/SL/sitemap.xml
```

`sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://ondo1400-dotcom.github.io/SL/</loc><priority>1.0</priority></url>
  <url><loc>https://ondo1400-dotcom.github.io/SL/about.html</loc><priority>0.8</priority></url>
  <url><loc>https://ondo1400-dotcom.github.io/SL/programs.html</loc><priority>0.8</priority></url>
  <url><loc>https://ondo1400-dotcom.github.io/SL/events.html</loc><priority>0.6</priority></url>
  <url><loc>https://ondo1400-dotcom.github.io/SL/stories.html</loc><priority>0.6</priority></url>
  <url><loc>https://ondo1400-dotcom.github.io/SL/contact.html</loc><priority>0.6</priority></url>
</urlset>
```

XML 유효성 확인:

```bash
python3 -c "
import xml.dom.minidom
xml.dom.minidom.parse('sitemap.xml')
print('✓ sitemap.xml 유효')
"
```

- [ ] **Step 4: `README.md` 작성**

```markdown
# Spring of Life

> A non-denominational Bible institution rooted in missionary work from Germany.
> In Korea since 2014.

Spring of Life(SL) 소개 웹사이트. 빌드 도구 없는 정적 다중 페이지 사이트다.

## 구조

```
SL/
├── index.html        홈
├── about.html        소개 · 글로벌 확장 · Mission & Vision
├── programs.html     프로그램 5종 · How to Start
├── events.html       지난 행사 · 갤러리
├── stories.html      간증 4편
├── contact.html      문의 · FAQ
│
├── assets/
│   ├── css/styles.css   공유 스타일시트
│   ├── js/script.js     공유 스크립트
│   └── images/          로고 · 포스터 · 갤러리 · 인물
│
├── tools/
│   ├── verify.py        링크 · alt · 앵커 정적 검사
│   └── browser_check.py 반응형 · 콘솔 에러 · 스크린샷
│
└── docs/superpowers/    설계 문서 · 구현 계획
```

## 기술 스택

- HTML5 정적 다중 페이지 (6장)
- Vanilla CSS — 커스텀 프로퍼티, Grid, `clamp()`
- Vanilla JS — IntersectionObserver reveal, 모바일 내비, 라이트박스. 의존성 0개
- 폰트 — Poppins · Playfair Display · Inter (Google Fonts), Pretendard (CDN)
- 빌드 도구 없음

## 로컬 실행

```bash
python3 -m http.server 8000
# http://localhost:8000
```

## 검증

```bash
python3 tools/verify.py .                          # 링크 · alt · 앵커
python3 tools/browser_check.py --shots /tmp/shots  # 360/768/1440px · 콘솔 에러
```

## 배포

GitHub Pages — Settings → Pages → Source: `main` / `/ (root)`

## 남은 작업

- [ ] 참여 신청 링크 — `programs.html`의 `Apply now` 버튼이 `href="#"` 자리표시자
- [ ] 대표 연락처 — `contact.html`의 "Contact details coming soon" 교체
- [ ] 커스텀 도메인 — 확정 시 `CNAME` 추가 후 canonical / og:url / sitemap.xml의
      `https://ondo1400-dotcom.github.io/SL/` 를 일괄 치환
- [ ] 다음 행사 안내 — `events.html`의 `#next` 섹션

---

© 2026 Spring of Life. All rights reserved.
```

- [ ] **Step 5: 최종 전체 검증**

```bash
python3 tools/verify.py .
python3 tools/browser_check.py --shots /tmp/sl-final
```

기대: 둘 다 exit 0. `✓ 6개 페이지 통과`, `✓ 6개 페이지 × 3개 폭 통과`.

alt 커버리지를 독립적으로 재확인:

```bash
python3 -c "
import re, pathlib
tags = [t for p in pathlib.Path('.').glob('*.html')
        for t in re.findall(r'<img\b[^>]*>', p.read_text(encoding='utf-8'))]
missing = [t for t in tags if not re.search(r'\balt\s*=', t)]
print(f'img 총 {len(tags)}개, alt 누락 {len(missing)}개')
assert not missing, missing
"
```

기대: `alt 누락 0개`.

- [ ] **Step 6: 6개 페이지 스크린샷을 눈으로 확인**

Read 도구로 `/tmp/sl-final/` 의 6개 PNG를 모두 연다. 확인 항목:
- 헤더/푸터가 6페이지에서 동일하게 보인다
- 현재 페이지의 내비 링크에 밑줄 표시(`aria-current`)가 있다
- 흰 카드 + 검정 라운드 테두리가 일관되게 적용됐다
- 이미지가 깨지거나 비어 있지 않다
- 텍스트가 잘리거나 겹치지 않는다

문제가 있으면 고치고 Step 5로 돌아간다.

- [ ] **Step 7: 커밋**

```bash
git add README.md robots.txt sitemap.xml *.html
git commit -m "feat: SEO 메타·사이트맵·README 추가

6개 페이지에 OG/Twitter 카드, 홈에 Organization JSON-LD.
남은 자리표시자 4건은 README에 기록."
```

- [ ] **Step 8: GitHub 저장소 생성 및 푸시 — 사용자 확인 필요**

사용자가 `ondo1400-dotcom` 계정으로 `gh auth login`을 완료했고, 활성 계정으로 설정돼 있다.
푸시 직전에 활성 계정을 한 번 더 확인한다:

```bash
gh auth status 2>&1 | grep -A1 "ondo1400-dotcom"
```

기대: `Active account: true`. 다르면 `gh auth switch --user ondo1400-dotcom`으로 전환한다.

**LCC의 `.git/config`에 박혀 있는 토큰을 재사용하지 않는다** — 그 토큰은 폐기를 권고한 상태다.

저장소를 만들고 푸시한다:

```bash
gh repo create ondo1400-dotcom/SL --public --source=. --remote=origin --push
```

또는 저장소를 웹에서 먼저 만든 경우:

```bash
git remote add origin https://github.com/ondo1400-dotcom/SL.git
git branch -M main
git push -u origin main
```

**리모트 URL에 토큰을 넣지 않는다.** 인증은 `gh auth` 또는 git credential helper에 맡긴다.

- [ ] **Step 9: GitHub Pages 활성화 및 배포 확인**

```bash
gh api -X POST repos/ondo1400-dotcom/SL/pages \
  -f "source[branch]=main" -f "source[path]=/" 2>&1 | head -5
```

배포까지 1~2분 기다린 뒤:

```bash
curl -sI https://ondo1400-dotcom.github.io/SL/ | head -1
```

기대: `HTTP/2 200`.

라이브 사이트를 실제로 열어 확인한다:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto("https://ondo1400-dotcom.github.io/SL/", wait_until="networkidle")
    print("title:", pg.title())
    print("errors:", errors)
    pg.screenshot(path="/tmp/sl-live.png", full_page=True)
    b.close()
PY
```

Read 도구로 `/tmp/sl-live.png`를 열어 로컬과 동일하게 보이는지 확인한다.
이미지가 깨져 보이면 대소문자 구분 문제다(GitHub Pages는 Linux, Windows는 대소문자 무시).
파일명과 `src` 값의 대소문자를 대조한다.

---

## 자체 검토

**스펙 커버리지 확인:**

| 스펙 섹션 | 구현 Task |
|---|---|
| §3 결정사항 (영어 단일 / 6페이지 / PDF 추출 / CTA 자리표시자) | Global Constraints, 1, 7 |
| §4 정보구조 — 6개 페이지 · 섹션 배분 | 3, 5, 6, 7, 8, 9, 10 |
| §5.1 컬러 토큰 | 3 Step 1 |
| §5.2 시그니처 컴포넌트 (`.card` `.marker` `.chip`) | 3 Step 1 |
| §5.3 타이포그래피 | 3 Step 1, 3 Step 3(폰트 로드) |
| §5.4 레이아웃 · 브레이크포인트 | 3 Step 1~2 |
| §6 에셋 추출 · 인물 사진 파일명 규약 | 1 |
| §7 JS 4가지 | 4 (1~3), 8 (라이트박스) |
| §8 SEO · 메타데이터 | 11 Step 1~3 |
| §9 접근성 (alt · aria · reduced-motion · 포커스) | 3, 4, 8, 11 Step 5 |
| §10 배포 | 11 Step 8~9 |
| §11 검증기준 5가지 | 2 (①③), 4 (②④), 11 Step 5~6, 9 (⑤) |
| §12 열어둔 항목 | 7 (신청), 10 (연락처), 11 Step 4 (README 기록) |

누락 없음.

**타입/이름 일관성 확인:**
- `.reveal` / `.is-visible` — Task 3 CSS 정의, Task 4 JS 토글. 일치.
- `#header` / `.header--scrolled` — Task 3 정의, Task 4 참조. 일치.
- `#menuBtn` `#mobileNav` — Task 3 마크업, Task 4 JS. 일치.
- `#lightbox` `#lightboxImg` `#lightboxCap` `#lightboxClose` `.poster` `data-full` `data-caption` — Task 8 내부에서 마크업·CSS·JS가 모두 같은 이름 사용. 일치.
- `.hero__actions` — Task 3 정의, Task 5·9에서 재사용. 일치.
- `.cta-band` — Task 5 정의, Task 8·9에서 재사용. 일치.
- `.stats` `.pillar` — Task 5 정의, Task 6에서 재사용. 일치.
- `programs.html#start` — Task 5·9에서 링크, Task 7에서 `id="start"` 생성. Task 7 완료 전까지 verify가 파일 없음으로 잡지만 이는 예상된 중간 상태이며 각 Task의 기대 출력에 명시돼 있다.
- `assets/images/people/01~04.jpg` — Task 1 생성, Task 5·9 참조. Task 9 Step 2에 매핑 검증 지시 포함.

**자리표시자 점검:** `programs.html`의 `href="#"`와 `contact.html`의 연락처 문구는 스펙 §12가 명시한 의도된 자리표시자이며, README에 후속 작업으로 기록된다. 그 외 "TBD"/"나중에 구현" 류 없음.
