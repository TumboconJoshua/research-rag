"""Semantic chunking of document text into overlapping windows."""
import re
from dataclasses import dataclass
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Section headings that typically appear in academic papers
SECTION_PATTERNS = [
    (r"(?i)^\s*abstract\s*$", "abstract"),
    (r"(?i)^\s*\d*\.?\s*introduction\s*$", "introduction"),
    (r"(?i)^\s*\d*\.?\s*(?:related work|literature review|background)\s*$", "literature_review"),
    (r"(?i)^\s*\d*\.?\s*(?:methodology|method|methods|approach)\s*$", "methodology"),
    (r"(?i)^\s*\d*\.?\s*(?:experiment|experiments|experimental|evaluation)\s*$", "experiments"),
    (r"(?i)^\s*\d*\.?\s*results?\s*$", "results"),
    (r"(?i)^\s*\d*\.?\s*discussion\s*$", "discussion"),
    (r"(?i)^\s*\d*\.?\s*conclusion\s*$", "conclusion"),
    (r"(?i)^\s*references?\s*$", "references"),
]


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    section: str
    text: str
    char_start: int
    char_end: int
    chunk_index: int


def detect_section(line: str) -> str | None:
    """Return the section label if the line matches a section heading."""
    for pattern, label in SECTION_PATTERNS:
        if re.match(pattern, line.strip()):
            return label
    return None


def chunk_document(
    document_id: str,
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    """
    Split document text into semantic chunks with section labels.

    Strategy:
    1. Split by section headings to assign labels.
    2. Within each section, create fixed-token-size chunks with overlap.
    """
    settings = get_settings()
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    # ---- Step 1: Split by sections ----
    lines = text.split("\n")
    sections: list[tuple[str, str]] = []  # (section_label, section_text)
    current_section = "body"
    current_lines: list[str] = []

    for line in lines:
        label = detect_section(line)
        if label:
            if current_lines:
                sections.append((current_section, "\n".join(current_lines)))
            current_section = label
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_section, "\n".join(current_lines)))

    # ---- Step 2: Chunk each section ----
    chunks: list[Chunk] = []
    chunk_index = 0
    global_char_pos = 0

    for section_label, section_text in sections:
        words = section_text.split()
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            char_start = global_char_pos
            char_end = char_start + len(chunk_text)

            chunks.append(
                Chunk(
                    chunk_id=f"{document_id}_chunk_{chunk_index}",
                    document_id=document_id,
                    section=section_label,
                    text=chunk_text,
                    char_start=char_start,
                    char_end=char_end,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1
            global_char_pos = char_end + 1

            if end == len(words):
                break
            start = end - chunk_overlap

    logger.info(
        "document_chunked",
        document_id=document_id,
        total_chunks=len(chunks),
        sections=[s for s, _ in sections],
    )
    return chunks
