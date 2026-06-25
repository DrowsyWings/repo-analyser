from pydantic import BaseModel


class SummaryResponse(BaseModel):
    summary: str
    generated_at: str
    model: str
