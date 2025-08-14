from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json

class RssFeedConfigBase(BaseModel):
    name: str
    qbitname: Optional[str] = None
    enable: bool = True
    rssUrl: str
    filters: str = Field(default="[]", description="JSON string of filters") # Changed to str
    site: str
    qbCategory: Optional[str] = None
    getDetail: Optional[bool] = False
    optpick: Optional[str] = None
    tag: Optional[str] = None
    action: str = "download"
    interval: int = 600

    # Custom validator to ensure filters is a valid JSON string
    def set_filters(self, value: List[str]):
        self.filters = json.dumps(value)

    def get_filters(self) -> List[str]:
        return json.loads(self.filters)


class RssFeedConfigCreate(RssFeedConfigBase):
    pass

class RssFeedConfig(RssFeedConfigBase):
    id: int

    class Config:
        orm_mode = True

class RSSHistoryBase(BaseModel):
    site: str
    title: str
    subtitle: Optional[str] = None
    tid: Optional[int] = None
    size: Optional[int] = None
    info_link: Optional[str] = None
    download_link: Optional[str] = None
    accept: Optional[int] = 0 # Corresponds to AcceptStatus enum value
    reason: Optional[str] = None
    rssname: Optional[str] = None
    rsstags: Optional[str] = None
    pubdate: Optional[datetime] = None

class RSSHistoryCreate(RSSHistoryBase):
    pass

class RSSHistory(RSSHistoryBase):
    id: int
    added_on: datetime

    class Config:
        orm_mode = True
