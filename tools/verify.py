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
        # tools/ 디렉터리 하위의 픽스처 파일 제외 (루트를 명시적으로 지정한 경우는 제외 대상이 아님)
        if rel.parts and rel.parts[0] == "tools":
            continue
        html = page.read_text(encoding="utf-8")
        ids = set(ID_ATTR.findall(html))

        for tag in IMG_TAG.findall(html):
            if not ALT_ATTR.search(tag):
                problems.append(f"{rel}: alt 없는 img — {tag[:70]}")

        for target in LINK_ATTR.findall(html):
            target = target.strip()
            if not target or target.startswith(SKIP_PREFIX):
                continue
            if target == "#":
                continue  # 의도된 자리표시자 (스펙 §12)
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
    # tools/ 디렉터리를 제외한 페이지 개수만 집계
    all_pages = sorted(root.rglob("*.html"))
    total = sum(1 for p in all_pages if p.relative_to(root).parts and p.relative_to(root).parts[0] != "tools")
    if problems:
        print(f"\n✗ {total}개 페이지에서 {len(problems)}건 발견")
        sys.exit(1)
    print(f"✓ {total}개 페이지 통과 (링크 · alt · 앵커)")


if __name__ == "__main__":
    main()
