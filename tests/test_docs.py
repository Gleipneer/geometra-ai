"""Tests for documentation structure and content."""

import os
import re
from pathlib import Path

# Sökvägar
DOCS_PATH = Path("meta_docs")
REQUIRED_DOCS = [
    "00_START_HÄR.md",
    "01_SYSTEMÖVERSIKT.md",
    "02_INITIERA_PROJEKT.md",
    "03_KONFIGURERA_MINNE.md",
    "04_BYGG_API.md",
    "05_PROMPT_LOGIK.md",
    "06_FALLBACK_LOGIK.md",
    "07_SYSTEMCHECK.md",
    "08_TESTNING.md",
    "09_CICD_PIPELINE.md",
    "10_DEPLOY_RAILWAY.md",
    "99_REFERENSER.md"
]

def read_md(filename: str) -> str:
    """Läs innehållet i en markdown-fil."""
    filepath = DOCS_PATH / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Dokumentationsfilen {filename} hittades inte")
    return filepath.read_text(encoding="utf-8")

def test_required_docs_exist():
    """Testa att alla obligatoriska dokumentationsfiler finns."""
    for doc in REQUIRED_DOCS:
        assert (DOCS_PATH / doc).exists(), f"Dokumentationsfilen {doc} saknas"

def test_00_start_har():
    """Testa innehållet i 00_START_HÄR.md."""
    content = read_md("00_START_HÄR.md")
    assert content.strip() != ""
    assert re.search(r"Node\.js-version", content)
    assert re.search(r"Python-version", content)
    assert re.search(r"pnpm-version", content)
    assert re.search(r"Docker-version", content)

def test_01_systemoversikt():
    """Testa innehållet i 01_SYSTEMÖVERSIKT.md."""
    content = read_md("01_SYSTEMÖVERSIKT.md")
    assert "systemarkitektur" in content.lower()
    assert "komponenter" in content.lower()
    assert "dataflöde" in content.lower()
    assert "validering" in content.lower()

def test_02_initiera_projekt():
    """Testa innehållet i 02_INITIERA_PROJEKT.md."""
    content = read_md("02_INITIERA_PROJEKT.md")
    assert "projektstruktur" in content.lower()
    assert "git" in content.lower()
    assert "konfiguration" in content.lower()

def test_03_konfigurera_minne():
    """Testa innehållet i 03_KONFIGURERA_MINNE.md."""
    content = read_md("03_KONFIGURERA_MINNE.md")
    assert "chromadb" in content.lower()
    assert "redis" in content.lower()
    assert "minneskomponenter" in content.lower()
    assert "installation" in content.lower()

def test_04_bygg_api():
    """Testa innehållet i 04_BYGG_API.md."""
    content = read_md("04_BYGG_API.md")
    assert "api" in content.lower()
    assert "endpoints" in content.lower()
    assert "fastapi" in content.lower()

def test_05_prompt_logik():
    """Testa innehållet i 05_PROMPT_LOGIK.md."""
    content = read_md("05_PROMPT_LOGIK.md")
    assert "prompt" in content.lower()
    assert "mallar" in content.lower()
    assert "variabler" in content.lower()

def test_06_fallback_logik():
    """Testa innehållet i 06_FALLBACK_LOGIK.md."""
    content = read_md("06_FALLBACK_LOGIK.md")
    assert "fallback" in content.lower()
    assert "felhantering" in content.lower()
    assert "återhämtning" in content.lower()

def test_07_systemcheck():
    """Testa innehållet i 07_SYSTEMCHECK.md."""
    content = read_md("07_SYSTEMCHECK.md")
    assert "system_check.sh" in content.lower()
    assert "validering" in content.lower()
    assert "hälsokontroll" in content.lower()

def test_08_testning():
    """Testa innehållet i 08_TESTNING.md."""
    content = read_md("08_TESTNING.md")
    assert "teststrategi" in content.lower()
    assert "enhetstester" in content.lower()
    assert "integrationstester" in content.lower()
    assert "e2e-tester" in content.lower()

def test_09_cicd_pipeline():
    """Testa innehållet i 09_CICD_PIPELINE.md."""
    content = read_md("09_CICD_PIPELINE.md")
    assert "github actions" in content.lower() or "ci/cd" in content.lower()
    assert "pipeline" in content.lower()
    assert "deployment" in content.lower()

def test_10_deploy_railway():
    """Testa innehållet i 10_DEPLOY_RAILWAY.md."""
    content = read_md("10_DEPLOY_RAILWAY.md")
    assert "railway" in content.lower()
    assert "deployment" in content.lower()
    assert "miljö" in content.lower()

def test_99_referenser():
    """Testa innehållet i 99_REFERENSER.md."""
    content = read_md("99_REFERENSER.md")
    assert "referens" in content.lower()
    assert "dokumentation" in content.lower()
    assert "länkar" in content.lower()

def test_code_blocks():
    """Testa att kodexempel i dokumentationen är giltiga."""
    for doc in REQUIRED_DOCS:
        content = read_md(doc)
        code_blocks = re.findall(r"```(?:python|bash|json|yaml)\n(.*?)```", content, re.DOTALL)
        for block in code_blocks:
            # Här kan vi lägga till mer avancerad validering av kodexempel
            assert block.strip() != "", f"Tomt kodexempel hittades i {doc}" 