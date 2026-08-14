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
- [ ] 커스텀 도메인 — 확정 시 `CNAME` 추가 후 canonical / og:url / sitemap.xml의 `https://ondo1400-dotcom.github.io/SL/` 를 일괄 치환
- [ ] 다음 행사 안내 — `events.html`의 `#next` 섹션

---

© 2026 Spring of Life. All rights reserved.
