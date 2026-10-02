import json
from pathlib import Path

from app.rag import ask_knowledge_base, retrieve_context


CASES_FILE = Path("evals/cases.json")

ABSTENTION_TEXT = (
    "I don't know based on the available policy information."
)


def evaluate_retrieval(
    retrieved_text: str,
    expected_policy: str | None,
) -> bool:
    # For unsupported questions, there is no expected policy.
    #
    # Note: this does NOT prove retrieval correctly rejected the
    # question. Our current tiny KB contains all policies in one
    # chunk, so negative retrieval evaluation isn't meaningful yet.
    if expected_policy is None:
        return True

    return expected_policy.lower() in retrieved_text.lower()


def evaluate_generation(
    answer: str,
    expected_keywords: list[str],
    should_abstain: bool,
) -> bool:
    if should_abstain:
        return answer.strip() == ABSTENTION_TEXT

    answer_lower = answer.lower()

    return all(
        keyword.lower() in answer_lower
        for keyword in expected_keywords
    )


def main():
    cases = json.loads(CASES_FILE.read_text())

    retrieval_passed = 0
    generation_passed = 0
    overall_passed = 0

    for case in cases:
        # -------------------------
        # 1. Evaluate retrieval
        # -------------------------

        retrieved_chunks = retrieve_context(
            case["question"]
        )

        retrieved_text = " ".join(retrieved_chunks)

        retrieval_success = evaluate_retrieval(
            retrieved_text=retrieved_text,
            expected_policy=case["expected_policy"],
        )

        # -------------------------
        # 2. Evaluate generation
        # -------------------------

        response = ask_knowledge_base(
            case["question"]
        )

        generation_success = evaluate_generation(
            answer=response.answer,
            expected_keywords=case["expected_keywords"],
            should_abstain=case["should_abstain"],
        )

        # -------------------------
        # 3. Record results
        # -------------------------

        if retrieval_success:
            retrieval_passed += 1

        if generation_success:
            generation_passed += 1

        if retrieval_success and generation_success:
            overall_passed += 1

        retrieval_status = (
            "PASS" if retrieval_success else "FAIL"
        )

        generation_status = (
            "PASS" if generation_success else "FAIL"
        )

        print()
        print(f"[{case['id']}]")
        print(f"Retrieval:  {retrieval_status}")
        print(f"Generation: {generation_status}")
        print(f"Question:   {case['question']}")
        print(f"Answer:     {response.answer}")

    # -------------------------
    # Summary
    # -------------------------

    total = len(cases)

    print()
    print("--------------------------------")
    print(
        f"Retrieval:  "
        f"{retrieval_passed}/{total} "
        f"({retrieval_passed / total * 100:.1f}%)"
    )
    print(
        f"Generation: "
        f"{generation_passed}/{total} "
        f"({generation_passed / total * 100:.1f}%)"
    )
    print(
        f"Overall:    "
        f"{overall_passed}/{total} "
        f"({overall_passed / total * 100:.1f}%)"
    )
    print("--------------------------------")


if __name__ == "__main__":
    main()
