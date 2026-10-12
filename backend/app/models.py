from sqlmodel import Field, SQLModel


class TestResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source: str
    destination: str
    test: str
    expected: str
    observed: str = ""
    screenshot: str = ""
