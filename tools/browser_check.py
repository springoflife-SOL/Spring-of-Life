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
    # 반복 실행 시 직전 소켓의 TIME_WAIT로 죽지 않도록
    socketserver.TCPServer.allow_reuse_address = True
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
                errors: list[tuple[str, str]] = []  # (message, source_url)
                external_notes: list[str] = []

                def on_console(msg):
                    if msg.type == "error":
                        location_url = msg.location.get("url", "") if msg.location else ""
                        if f"127.0.0.1:{PORT}" in location_url or not location_url:
                            # 로컬 서버 에러 또는 출처 불명: 실패 처리
                            errors.append((msg.text, location_url))
                        else:
                            # 외부 리소스 에러: 참고용만 기록
                            external_notes.append(
                                f"참고: 외부 리소스 로드 실패 — {msg.text} (출처: {location_url})")

                def on_page_error(err):
                    # JS 예외는 출처 무관 실패 처리
                    errors.append((f"JS 예외: {str(err)}", ""))

                page.on("console", on_console)
                page.on("pageerror", on_page_error)

                for name in pages:
                    del errors[:]
                    del external_notes[:]
                    page.goto(f"http://127.0.0.1:{PORT}/{name}",
                              wait_until="networkidle")
                    page.wait_for_timeout(400)

                    scroll_w = page.evaluate("document.documentElement.scrollWidth")
                    inner_w = page.evaluate("window.innerWidth")
                    if scroll_w > inner_w + 1:
                        problems.append(
                            f"{name} @{width}px: 가로 오버플로 "
                            f"scrollWidth={scroll_w} > innerWidth={inner_w}")
                    for msg, url in errors:
                        msg_with_url = f"{msg} (출처: {url})" if url else msg
                        problems.append(f"{name} @{width}px: 콘솔 에러 — {msg_with_url}")
                    for note in external_notes:
                        print(note)

                    if shots and width == 1440:
                        # 모든 reveal 요소 발동: 끝까지 스크롤
                        scroll_height = page.evaluate(
                            "document.documentElement.scrollHeight")
                        step = 300
                        for y in range(step, scroll_height, step):
                            page.evaluate(f"window.scrollTo(0, {y})")
                            page.wait_for_timeout(100)
                        page.evaluate(f"window.scrollTo(0, {scroll_height})")
                        # CSS 트랜지션(0.7s) 완료 대기
                        page.wait_for_timeout(800)
                        # 맨 위로 복귀
                        page.evaluate("window.scrollTo(0, 0)")
                        page.wait_for_timeout(100)
                        page.screenshot(path=str(shots / f"{Path(name).stem}.png"),
                                        full_page=True)
                page.close()
            browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()

    for problem in problems:
        print(problem)
    if problems:
        print(f"\n✗ {len(problems)}건 발견")
        raise SystemExit(1)
    print(f"✓ {len(pages)}개 페이지 × {len(WIDTHS)}개 폭 통과")


if __name__ == "__main__":
    main()
