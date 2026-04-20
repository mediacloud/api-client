import datetime as dt
from typing import Any, TypeAlias, TypedDict

JSONObj: TypeAlias = dict[str, Any]
JSONList: TypeAlias = list[JSONObj]
PaginationToken: TypeAlias = str | None


class Story(TypedDict, total=False):
    id: str
    title: str
    url: str
    language: str
    media_name: str
    media_url: str
    text: str
    publish_date: dt.date | None
    indexed_date: dt.datetime | None


class StoryCount(TypedDict, total=False):
    relevant: int
    total: int


class CountOverTimePoint(TypedDict, total=False):
    date: dt.date
    count: int
    total_count: int
    ratio: float


class SourceCount(TypedDict, total=False):
    source: str
    count: int


class LanguageCount(TypedDict, total=False):
    language: str
    ratio: float
    value: int


class SourceWeekAttention(TypedDict, total=False):
    media_name: str
    week: str
    matching_stories: int
    total_stories: int
    ratio: float


class SourceIntervalAttention(TypedDict, total=False):
    media_name: str
    interval: str
    bucket: str
    matching_stories: int
    total_stories: int
    ratio: float


class Collection(TypedDict, total=False):
    id: int
    name: str
    platform: str
    notes: str
    public: bool
    featured: bool
    managed: bool
    monitored: bool


class Source(TypedDict, total=False):
    id: int
    name: str
    platform: str
    label: str
    homepage: str
    media_type: str
    pub_state: str
    pub_country: str
    primary_language: str


class Feed(TypedDict, total=False):
    id: int
    source_id: int
    url: str
    name: str
    modified_at: str


class OffsetPage(TypedDict, total=False):
    count: int
    next: str | None
    previous: str | None
    results: JSONList


class VersionInfo(TypedDict, total=False):
    GIT_REV: str
    now: float
    version: str
