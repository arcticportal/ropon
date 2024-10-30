from datetime import datetime
from typing import Optional
from ninja import Schema
from pydantic import UUID4


class HomePageSchema(Schema):
    id: int
    path: str
    depth: int
    numchild: int
    translation_key: UUID4
    live: bool
    has_unpublished_changes: bool
    first_published_at: Optional[datetime]
    last_published_at: Optional[datetime]
    go_live_at: Optional[datetime]
    expire_at: Optional[datetime]
    expired: bool
    locked: bool
    locked_at: Optional[datetime]
    title: str
    draft_title: str
    slug: str
    url_path: str
    seo_title: str
    show_in_menus: bool
    search_description: str
    latest_revision_created_at: Optional[datetime]
