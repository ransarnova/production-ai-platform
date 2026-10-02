from pathlib import Path


POLICY_FILE = Path("data/lending-policy.txt")


def load_chunks() -> list[str]:
    content = POLICY_FILE.read_text()

    chunks = [
        chunk.strip()
        for chunk in content.split("\n\n")
        if chunk.strip().startswith("POLICY-")
    ]

    return chunks


def retrieve_context(question: str) -> str:
    chunks = load_chunks()
    question_lower = question.lower()

    if "missed" in question_lower or "repayment" in question_lower:
        return chunks[0]

    if "loan" in question_lower or "approve" in question_lower:
        return chunks[1]

    if "debt-to-income" in question_lower or "50%" in question_lower:
        return chunks[2]

    return ""
