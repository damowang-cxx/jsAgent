from pathlib import Path

import pytest

from har_agent.models.har import HarDocument
from har_agent.parsers.har_loader import HarLoaderError, load_har_document


FIXTURES = Path(__file__).parent / "fixtures"


def test_load_har_document_success() -> None:
    document = load_har_document(FIXTURES / "basic.har")
    assert isinstance(document, HarDocument)
    assert len(document.log.entries) == 4


def test_load_har_document_invalid_json(tmp_path: Path) -> None:
    broken = tmp_path / "broken.har"
    broken.write_text("{", encoding="utf-8")

    with pytest.raises(HarLoaderError):
        load_har_document(broken)
