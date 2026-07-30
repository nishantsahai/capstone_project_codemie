import os
import subprocess
import sys
import time

import pytest
from playwright.sync_api import Page, expect


STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")


@pytest.fixture(scope="session")
def streamlit_server():
    """Start Streamlit server for UI tests."""
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "ci_cd_analyzer/ui/streamlit_app.py",
            "--server.headless=true",
            "--server.port=8501",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait for server to be ready
    deadline = time.time() + 60
    last_output = ""
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Streamlit server exited early. Output:\n{last_output}")
        try:
            line = proc.stdout.readline() if proc.stdout else ""
            if line:
                last_output += line
                if "You can now view your Streamlit app" in line or "Local URL" in line:
                    break
        except Exception:
            pass
        time.sleep(0.2)

    yield

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()


def _dismiss_cookie_banner(page: Page) -> None:
    # No-op helper; Streamlit may show banners depending on version.
    pass


def test_ui_analyze_sample_jenkins(page: Page, streamlit_server):
    page.goto(STREAMLIT_URL)
    _dismiss_cookie_banner(page)

    expect(page.get_by_text("CI/CD Pipeline Analyzer")).to_be_visible(timeout=30000)

    page.get_by_role("button", name="Analyze log").click()

    expect(page.get_by_text("Total runs")).to_be_visible()
    expect(page.get_by_text("Stage analysis")).to_be_visible()


def test_ui_empty_log_shows_error(page: Page, streamlit_server):
    page.goto(STREAMLIT_URL)
    _dismiss_cookie_banner(page)

    # Disable sample log via direct click (Streamlit checkbox overlay can intercept pointer events)
    checkbox_label = page.locator("label:has-text('Load sample log')").first
    expect(checkbox_label).to_be_visible()
    checkbox_label.click(force=True)

    # Clear text area
    textarea = page.locator("textarea").first
    textarea.fill("")

    page.get_by_role("button", name="Analyze log").click()

    expect(page.get_by_text("Add or upload a log first.")).to_be_visible()
