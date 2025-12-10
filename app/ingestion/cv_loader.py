from pathlib import Path
import pdfplumber


def load_cv_text(cv_path: str | Path) -> str:
    cv_path = Path(cv_path)
    if not cv_path.exists():
        raise FileNotFoundError(f"CV not found at {cv_path}")

    texts = []
    with pdfplumber.open(cv_path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    full_text = "\n".join(texts)
    return full_text