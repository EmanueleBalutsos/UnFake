from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True) # make it immutable after creation
class Article:
    title: str
    source: str
    query_origin: str # which query retrieved this
    published_at: datetime | None = None
    url: str = ""
    description: str | None = None
    content: str | None = None

    def __str__(self):
        return f"{self.title}, source='{self.source}', query_origin='{self.query_origin}' - URL : {self.url}"
    
    def __repr__(self):
        return self.__str__()


