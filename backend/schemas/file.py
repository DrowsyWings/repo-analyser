from pydantic import BaseModel


class FileResponse(BaseModel):
    name: str
    path: str
    extension: str
    loc: int
    imports: list[str]
    imported_by: list[str]
    content: str
