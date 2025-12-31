"""Crumb models for knowledge crumbs."""

from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field


class CrumbMetadata(BaseModel):
    """Metadata for a knowledge crumb."""

    title: str = Field(..., description="Crumb title")
    description: str = Field(..., description="One-line summary")
    category: str = Field(..., description="Crumb category")
    tags: list[str] = Field(default_factory=list, description="Searchable tags")
    difficulty: str = Field(
        ..., description="Target audience level", pattern="^(beginner|intermediate|advanced)$"
    )
    created: date = Field(..., description="Creation date")
    updated: date = Field(..., description="Last update date")
    author: str = Field(..., description="Original author")
    related: list[str] = Field(default_factory=list, description="Related crumbs")
    prerequisites: list[str] = Field(default_factory=list, description="Prerequisites")
    applies_to: list[str] = Field(default_factory=list, description="Technologies/scenarios")


class Crumb(BaseModel):
    """A knowledge crumb with metadata and content."""

    path: Path = Field(..., description="Relative path from crumbs directory")
    metadata: CrumbMetadata = Field(..., description="Crumb metadata")
    content: str = Field(..., description="Markdown content (without frontmatter)")
    file_path: Path = Field(..., description="Absolute path to crumb file")

    @property
    def slug(self) -> str:
        """Get crumb slug (path without .md extension)."""
        return str(self.path.with_suffix(""))

    @property
    def category_path(self) -> str:
        """Get category/filename format."""
        return str(self.path)

    def matches_category(self, category: str) -> bool:
        """Check if crumb matches category."""
        return self.metadata.category.lower() == category.lower()

    def matches_tag(self, tag: str) -> bool:
        """Check if crumb has tag."""
        return tag.lower() in [t.lower() for t in self.metadata.tags]

    def matches_difficulty(self, difficulty: str) -> bool:
        """Check if crumb matches difficulty."""
        return self.metadata.difficulty.lower() == difficulty.lower()

    def matches_query(self, query: str, case_sensitive: bool = False) -> bool:
        """Check if crumb matches search query in content or metadata."""
        if not case_sensitive:
            query = query.lower()
            search_in = [
                self.metadata.title.lower(),
                self.metadata.description.lower(),
                self.content.lower(),
                *[t.lower() for t in self.metadata.tags],
            ]
        else:
            search_in = [
                self.metadata.title,
                self.metadata.description,
                self.content,
                *self.metadata.tags,
            ]

        return any(query in text for text in search_in)
