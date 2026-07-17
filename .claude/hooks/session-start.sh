#!/bin/bash
# SessionStart hook: install the runtime dependencies that hcux-report-format's
# render.py needs (Python Playwright matched to the pre-installed Chromium, and
# the Noto Sans CJK JP font for Japanese text). Idempotent and non-interactive.
set -euo pipefail

# Only run in Claude Code on the web (remote container). Locally, do nothing.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Python Playwright must match the browser build pre-installed at
# $PLAYWRIGHT_BROWSERS_PATH (Chromium rev 1194 == Playwright 1.56.x). Pin 1.56.0
# so we reuse that browser instead of triggering a fresh download.
PW_VERSION="1.56.0"
if ! python3 -c "import playwright, importlib.metadata as m, sys; sys.exit(0 if m.version('playwright')=='${PW_VERSION}' else 1)" 2>/dev/null; then
  pip3 install --quiet "playwright==${PW_VERSION}"
fi

# Noto Sans CJK JP: required so Japanese renders instead of tofu boxes.
if ! fc-list 2>/dev/null | grep -qi "Noto Sans CJK JP"; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get install -y --no-install-recommends fonts-noto-cjk >/dev/null 2>&1 || true
fi

echo "session-start: hcux-report-format render deps ready"
