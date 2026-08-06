from pydantic import BaseModel


class ModuleSummary(BaseModel):
    module: str
    summary: str


class OverviewResponse(BaseModel):
    overview: str
    modules: list[ModuleSummary]
