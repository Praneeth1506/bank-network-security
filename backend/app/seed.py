"""Load the default test table into the tracker without creating duplicates.

Usage (from backend/): python -m app.seed
"""
from sqlmodel import Session, SQLModel, select

from .models import TestResult
from .test_cases import TEST_CASES


def seed(session: Session) -> int:
    """Insert TEST_CASES rows missing by (source, destination, test); return how many."""
    existing = set(session.exec(
        select(TestResult.source, TestResult.destination, TestResult.test)).all())
    inserted = 0
    for case in TEST_CASES:
        if (case["source"], case["destination"], case["test"]) not in existing:
            session.add(TestResult(**case))
            inserted += 1
    session.commit()
    return inserted


def main() -> None:
    from .main import engine

    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        print(f"added {seed(s)} test rows")


if __name__ == "__main__":
    main()
