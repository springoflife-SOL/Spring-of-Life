# Spring of Life (SL) 웹사이트 — 설계 문서

작성일: 2026-08-15
상태: 승인됨 (구현 계획 작성 대기)

---

## 1. 개요

Spring of Life(이하 SL)는 독일 선교 사역에 뿌리를 둔 초교파 성경 기관이다. 2014년부터
한국 대학가에서 청년 대상 성경 읽기 활동을 시작했고, 현재는 국내 국제 교회들과 협력하고 있다.

이 프로젝트는 SL을 소개하는 **정적 다중 페이지 웹사이트**를 만든다. 기존 `Desktop/LCC`
프로젝트와 동일한 구조 규약(빌드 도구 없음, 공유 CSS/JS 각 1개, GitHub Pages 배포)을 따르되,
디자인은 SL 브랜드 자료(Canva PPT 8장)를 따른다.

### 콘텐츠 원본

| 원본 | 위치 | 용도 |
|---|---|---|
| SL Concept 텍스트 | 사용자 제공 (대화) | 간증 전문, 프로그램 목록, 미션/비전 |
| Canva PPT (8쪽 PDF) | `Blue and White Minimalist Company Introduction Business Presentation.pdf` | 디자인 톤, 로고, 포스터·사진 에셋 |

두 원본이 충돌할 때(예: 간증문 길이)는 **사용자 제공 텍스트를 정본으로** 삼는다.
PPT의 간증문은 지면에 맞춰 축약된 판본이다.

---

## 2. 목표와 비목표

### 목표

- SL이 누구이고 무엇을 하는지 처음 방문자가 1분 안에 파악할 수 있게 한다.
- 프로그램 5종과 참여 방법을 명확히 제시한다.
- 실제 참여자 간증으로 신뢰를 확보한다.
- 지난 행사 기록으로 활동의 실재성을 보여준다.

### 비목표 (YAGNI)

- 회원가입·로그인·마이페이지 없음
- CMS·관리자 화면 없음 (콘텐츠 수정은 HTML 직접 편집)
- 다국어 토글 없음 (영어 단일)
- 온라인 신청 폼 제출 처리 없음 (CTA는 자리표시자)
- 빌드 도구·번들러·프레임워크 없음
- 다크 모드 없음

---

## 3. 결정 사항

브레인스토밍에서 확정한 4가지:

1. **언어**: 영어 단일. PPT와 간증문 원문이 모두 영어이고, 실제 대상이 한국 내 국제 청년이다.
   한글은 고유명사 병기(예: `Seonbae (선배)`)에만 예외적으로 쓴다.
2. **범위**: 멀티페이지 6장. 개별 아티클 페이지는 만들지 않는다.
3. **에셋**: PDF 내장 비트맵을 추출해 사용한다.
4. **신청 CTA**: 버튼과 안내 문구는 만들되 `href="#"` 자리표시자로 둔다.

---

## 4. 정보 구조

```
SL/
├── index.html        홈 (랜딩)
├── about.html        Who We Are · 글로벌 확장 · Since 2014 · Mission & Vision
├── programs.html     프로그램 5종 · How to Start
├── events.html       지난 행사 포스터 아카이브 + 현장 갤러리
├── stories.html      간증 4인 전문
├── contact.html      문의 · FAQ
│
├── assets/
│   ├── css/styles.css        공유 스타일시트 (단일 파일)
│   ├── js/script.js          공유 스크립트 (단일 파일)
│   └── images/
│       ├── logo.png          SL 물방울 로고 (투명 배경)
│       ├── posters/01~05.png 행사 포스터
│       ├── gallery/01~05.jpg 행사 현장 사진
│       ├── people/01~04.jpg  간증자 프로필
│       └── start/            신청서·스탬프카드 이미지
│
├── _archive/         원본 PDF · 추출 스크립트 (git 미추적)
├── docs/superpowers/specs/   설계 문서
├── .gitignore
├── README.md
├── robots.txt
└── sitemap.xml
```

### 페이지별 섹션

**index.html**
1. Hero — 로고 + "Get to Know Spring of Life" + 한 줄 소개 + CTA 2개(Programs / About)
2. Who We Are — 3문장 요약 + 통계 스트립(Since 2014 · 3 continents · 5 programs)
3. Four Pillars — 4장 카드 (Personal Growth / Putting the Word into Practice /
   Creating Global Positive Influence / Partners)
4. Programs preview — 5종 리스트 + programs.html 링크
5. Stories preview — 간증 2개 발췌 + stories.html 링크
6. Events strip — 포스터 5장 가로 스트립 + events.html 링크
7. CTA 밴드 — "How to Start" 유도

**about.html**
1. Who is Spring of Life? — 독일 뿌리
2. Global Expansion — 독일 → 남미 · 아프리카 · 아시아.
   세계지도 이미지나 SVG 지도는 만들지 않는다. 출발점(Germany) 블록 + 도착 지역 3장 카드의
   CSS 레이아웃으로 표현한다. 지도 제작은 범위 밖이며, 추후 이미지 확보 시 교체 가능한 구조로 둔다.
3. Since 2014 in Korea — 캠퍼스 시작, 국제 교회 협력 (New Hope Church, Shining Light Church)
4. Mission & Vision — 두 문단
5. Four Pillars 상세
6. Partners

**programs.html**
1. 프로그램 5종 카드 — 아이콘 · 이름 · 설명 · 형식(1:1 / 그룹) 표기
   - Bible Deep Dive — explore the Bible, 1 on 1
   - Faith & You — discover yourself through faith
   - Word & Reflect — building bible reflection habit
   - Bible Mentoring — grow through biblical guidance
   - Finding Inner Peace — discover roots of true peace
2. How to Start — 3스텝 (Reach out → Meet a mentor → Grow together)
3. 신청 CTA (자리표시자)

**events.html**
1. Poster archive — 포스터 5장 그리드, 클릭 시 라이트박스
   (Trivia Night, Movie Night, Beyond Small Talk, New Year Check-in, New Year New Me)
2. Gallery — 현장 사진 5장
3. 다음 행사 안내 자리표시자

**stories.html**
1. 간증 4인 전문 (Lorena/Brazil, Jenny/Chile, Gracia/Indonesia, Mahdi/Iran)
   - 원형 프로필 사진 · 이름 · 국가 · 전문 인용
2. CTA — "Your story could be next"

**contact.html**
1. 문의 안내 (연락 수단 자리표시자)
2. FAQ 4~5개
3. 위치 안내 (Hongdae, Seoul)

---

## 5. 디자인 시스템

### 5.1 컬러 토큰

PPT에서 추출한 팔레트. `:root` 커스텀 프로퍼티로 정의한다.

| 토큰 | 값 | 용도 |
|---|---|---|
| `--navy` | `#0B3C5D` | 헤드라인, 다크 섹션 배경 |
| `--navy-deep` | `#072A42` | 다크 섹션 그라데이션 끝 |
| `--teal` | `#7FCFD4` | 아이콘 칩, 액센트 |
| `--teal-soft` | `#BEE7E9` | 연한 배경 |
| `--forest` | `#1F4B3F` | 소제목 |
| `--sun` | `#FBF3A8` | 하이라이터 마커, 강조 배경 |
| `--lavender` | `#E8EDFB` | 페이지 바탕 |
| `--paper` | `#FFFFFF` | 카드 표면 |
| `--ink` | `#1A1A1A` | 본문, 카드 테두리 |
| `--muted` | `#5C6470` | 보조 텍스트 |

대비 검증(계산값): `--ink` on `--paper` = 17.4:1, `--navy` on `--paper` = 11.5:1,
`--ink` on `--sun` = 15.3:1 — 모두 WCAG AA 통과.
`--teal` 위 흰 텍스트는 1.8:1로 미달이므로 금지하고, `--teal` 배경에는 `--ink`(9.8:1)만 얹는다.

### 5.2 시그니처 컴포넌트

PPT 전 페이지에 반복되는 **"흰 카드 + 굵은 검정 라운드 테두리"** 를 사이트의 핵심 시각 언어로
가져온다.

```css
.card-outline {
  background: var(--paper);
  border: 2.5px solid var(--ink);
  border-radius: 22px;
}
```

부수 컴포넌트:
- `.marker` — `--sun` 배경의 하이라이터 효과 (제목 강조). PPT의 노란 형광펜 스타일.
- `.chip-icon` — 원형 `--teal-soft` 배경 + 아이콘. 4 Pillars와 프로그램 목록에 사용.
- `.stat` — 숫자 + 라벨 조합.

### 5.3 타이포그래피

| 역할 | 서체 | 스타일 |
|---|---|---|
| 헤드라인 | Poppins 800 | 대문자, `letter-spacing: .02em` |
| 디스플레이 | Playfair Display Italic | "Spring of Life" 로고타입 표현 |
| 본문 | Inter 400/500 | `line-height: 1.7` |
| 한글 fallback | Pretendard | 고유명사 병기용 |

Google Fonts + Pretendard CDN으로 로드한다 (LCC와 동일 방식).
크기는 `clamp()` 기반 유동 스케일.

### 5.4 레이아웃

- 최대 폭 `--max: 1200px`, 거터 `clamp(20px, 5vw, 40px)`
- 그리드는 CSS Grid. 4 Pillars는 `repeat(auto-fit, minmax(260px, 1fr))`
- 브레이크포인트 2개: `768px`(태블릿), `520px`(모바일)
- 섹션 수직 여백 `clamp(64px, 10vw, 120px)`

---

## 6. 에셋 추출

`pdfimages`로 PDF 내장 비트맵을 추출한다. 페이지 렌더링(스크린샷)이 아니라 원본
비트맵을 뽑기 때문에 배경·텍스트가 섞이지 않는다.

| 대상 | PDF 위치 | 원본 크기 | 처리 |
|---|---|---|---|
| 로고 | p1, image #4 + smask #5 | 432×432 | 알파 마스크 합성 → 투명 PNG |
| 포스터 5장 | p5, image #16~20 | ~453×640 | JPG 그대로 |
| 현장 사진 5장 | p5, image #21~25 | ~512×384 | JPG 변환 |
| 인물 사진 4장 | p6, image #28~31 | ~448×640 | 정사각 크롭 → 원형 마스크는 CSS |
| 신청서·스탬프카드 | p8, image #34, #37 | ~558×392 | JPG 그대로 |

**제약**: 최대 640px급이므로 히어로 배경 등 대형 이미지로는 쓰지 않는다.
카드 썸네일·갤러리·원형 프로필 용도로만 사용한다.

추출 스크립트는 `_archive/extract_assets.sh`에 남기되 git에는 올리지 않는다(일회용).

**인물 사진 주의**: 실존 인물의 얼굴 사진이다. SL이 자체 홍보 자료(PPT)에 이미 사용한
사진이므로 웹사이트 전재는 같은 목적 범위로 본다. 다만 파일명에 개인 식별 정보를 넣지 않고
`people/01.jpg` 형태로만 저장한다.

---

## 7. JavaScript

`assets/js/script.js` 단일 파일. 다음 4가지만 구현한다.

1. **Reveal 애니메이션** — `IntersectionObserver`로 `.reveal` 요소에 `.is-visible` 부여.
   `prefers-reduced-motion: reduce`면 즉시 표시하고 관찰하지 않는다.
2. **모바일 내비 토글** — 햄버거 버튼 ↔ `.mobile-nav`, `aria-expanded` 동기화.
3. **헤더 스크롤 상태** — 스크롤 시 `.header--scrolled` 클래스 (배경 불투명 전환).
4. **포스터 라이트박스** (events.html 전용) — 포스터 클릭 시 확대. ESC·배경 클릭으로 닫기,
   포커스 트랩, 열려 있을 때 body 스크롤 잠금.

의존성 없음. 전역 오염 방지를 위해 즉시실행 함수로 감싼다.

---

## 8. SEO · 메타데이터

각 페이지에 다음을 포함한다 (LCC 패턴 따름):

- `<title>`, `<meta name="description">` — 페이지별 고유
- Open Graph 5종 (`og:type`, `og:url`, `og:title`, `og:description`, `og:image`)
- Twitter Card `summary`
- `<link rel="canonical">`
- `index.html`에만 JSON-LD `Organization` 스키마
- `robots.txt` — 전체 허용 + sitemap 참조
- `sitemap.xml` — 6개 페이지

도메인이 미정이므로 canonical/og:url은 `https://springoflife.example/` 를
플레이스홀더로 두고, README에 "도메인 확정 시 일괄 치환" 항목을 명시한다.
페이지 간 링크는 모두 상대 경로로 작성해 도메인과 무관하게 동작하게 한다.

---

## 9. 접근성

- 시맨틱 마크업: `<header> <nav> <main> <section> <footer>`
- 모든 `<img>`에 의미 있는 `alt` (장식용은 `alt=""`)
- 키보드 내비게이션: 포커스 링 유지, 라이트박스 포커스 트랩
- `aria-label` — 로고 링크, 햄버거 버튼, 라이트박스 닫기
- `prefers-reduced-motion` 존중
- 본문 텍스트 대비 AA 이상

---

## 10. 배포

- `git init` 후 GitHub 저장소에 푸시
- Settings → Pages → `main` / `/ (root)`
- 커스텀 도메인 확정 시 `CNAME` 파일 추가
- 로컬 확인: `python3 -m http.server 8000`

---

## 11. 검증 기준

구현 완료 판정은 다음을 **실제로 실행해 확인**한 뒤에만 내린다.

1. **링크 무결성** — 6개 페이지의 모든 내부 링크·이미지 경로가 실재하는 파일을 가리킨다.
   깨진 링크 0개. (스크립트로 href/src 수집 후 파일 존재 검사)
2. **반응형** — 360px / 768px / 1440px 세 폭에서 가로 스크롤이 발생하지 않는다.
   (`document.documentElement.scrollWidth <= innerWidth`)
3. **alt 커버리지** — `alt` 속성이 없는 `<img>` 0개.
4. **콘솔 청결** — 6개 페이지 로드 시 JS 에러 0개.
5. **시각 확인** — 로컬 서버 구동 후 각 페이지 스크린샷을 찍어 육안 확인.

---

## 12. 열어둔 항목

| 항목 | 현재 처리 | 확정 시 할 일 |
|---|---|---|
| 도메인 | 플레이스홀더 URL | canonical/og:url 치환 + CNAME 추가 |
| 신청 링크 | `href="#"` | 구글폼/카톡 URL 삽입 |
| 연락처 | 자리표시자 | PPT의 전화번호는 개인 번호일 수 있어 넣지 않음. 대표 이메일 확보 시 삽입 |
| 다음 행사 | 자리표시자 섹션 | 일정 확정 시 내용 채움 |
