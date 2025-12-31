"""Core crumb management functionality."""

import json
from pathlib import Path
from typing import Any

from knl.core.paths import KnlPaths
from knl.models.crumb import Crumb, CrumbMetadata


class CrumbManager:
    """Manager for knowledge crumbs."""

    def __init__(self, paths: KnlPaths | None = None):
        """
        Initialize crumb manager.

        Args:
            paths: KNL paths instance. If None, uses default.
        """
        self.paths = paths or KnlPaths()
        self.crumbs_dir = self._find_crumbs_directory()

    def _find_crumbs_directory(self) -> Path | None:
        """
        Find the crumbs directory.

        Checks:
        1. Repo-local: .knl/know-how/crumbs/
        2. User-local: ~/.local/knl/know-how/crumbs/

        Returns:
            Path to crumbs directory or None if not found
        """
        # Try repo-local first
        repo_local = Path.cwd() / ".knl" / "know-how" / "crumbs"
        if repo_local.exists():
            return repo_local

        # Try user-local
        user_local = Path.home() / ".local" / "knl" / "know-how" / "crumbs"
        if user_local.exists():
            return user_local

        return None

    def parse_crumb(self, file_path: Path) -> Crumb | None:
        """
        Parse a crumb file with YAML frontmatter.

        Args:
            file_path: Path to crumb markdown file

        Returns:
            Parsed Crumb or None if invalid
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Parse YAML frontmatter
            # Format: ---\nyaml content\n---\nmarkdown content
            if not content.startswith("---\n"):
                return None

            parts = content.split("---\n", 2)
            if len(parts) < 3:
                return None

            yaml_content = parts[1]
            markdown_content = parts[2]

            # Parse YAML using tomli (it can handle basic YAML)
            # For proper YAML, we should use PyYAML, but let's keep dependencies minimal
            # We'll use a simple YAML parser for now
            metadata_dict = self._parse_yaml_frontmatter(yaml_content)

            # Create metadata object
            metadata = CrumbMetadata(**metadata_dict)

            # Get relative path from crumbs directory
            if self.crumbs_dir:
                relative_path = file_path.relative_to(self.crumbs_dir)
            else:
                relative_path = file_path

            return Crumb(
                path=relative_path,
                metadata=metadata,
                content=markdown_content.strip(),
                file_path=file_path,
            )

        except Exception:
            # Skip invalid crumbs
            return None

    def _parse_yaml_frontmatter(self, yaml_content: str) -> dict[str, Any]:
        """
        Parse YAML frontmatter.

        This is a simple YAML parser for crumb frontmatter.
        For production, consider using PyYAML.

        Args:
            yaml_content: YAML content string

        Returns:
            Parsed dictionary
        """
        result: dict[str, Any] = {}
        current_key = None
        current_list: list[str] = []
        in_list = False

        for line in yaml_content.strip().split("\n"):
            line_stripped = line.rstrip()

            # Skip empty lines
            if not line_stripped:
                continue

            # List item (indented with - )
            if line.startswith("  - "):
                item = line.strip("- ").strip().strip('"')
                current_list.append(item)
                in_list = True
                continue

            # Key-value pair (not indented)
            if ":" in line_stripped and not line.startswith(" "):
                # Save previous list if any
                if current_key and in_list:
                    result[current_key] = current_list
                    current_list = []
                    in_list = False

                # Handle both ": " and ":" (for keys with empty values)
                if ": " in line_stripped:
                    key, value = line_stripped.split(": ", 1)
                else:
                    key, value = line_stripped.split(":", 1)

                current_key = key.strip()
                value = value.strip().strip('"')

                # Check if value is a JSON-style list
                if value.startswith("[") and value.endswith("]"):
                    try:
                        # Parse as JSON list
                        result[current_key] = json.loads(value)
                        # Reset list state since we're done with this key
                        in_list = False
                    except json.JSONDecodeError:
                        result[current_key] = value
                        in_list = False
                elif value == "":
                    # Start of a multi-line list
                    current_list = []
                    in_list = True
                elif value == "[]":
                    # Empty list
                    result[current_key] = []
                    in_list = False
                else:
                    # Regular value
                    result[current_key] = value
                    in_list = False

        # Save final list if any
        if current_key and in_list:
            result[current_key] = current_list

        return result

    def list_crumbs(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        difficulty: str | None = None,
    ) -> list[Crumb]:
        """
        List all crumbs with optional filtering.

        Args:
            category: Filter by category
            tags: Filter by tags (any match)
            difficulty: Filter by difficulty

        Returns:
            List of matching crumbs
        """
        if not self.crumbs_dir or not self.crumbs_dir.exists():
            return []

        crumbs = []

        # Find all .md files recursively
        for md_file in self.crumbs_dir.rglob("*.md"):
            # Skip README files
            if md_file.name.lower() == "readme.md":
                continue

            crumb = self.parse_crumb(md_file)
            if not crumb:
                continue

            # Apply filters
            if category and not crumb.matches_category(category):
                continue

            if tags and not any(crumb.matches_tag(tag) for tag in tags):
                continue

            if difficulty and not crumb.matches_difficulty(difficulty):
                continue

            crumbs.append(crumb)

        return crumbs

    def get_crumb(self, crumb_path: str) -> Crumb | None:
        """
        Get a specific crumb by path.

        Args:
            crumb_path: Relative path like "devops/github-pages-setup" or full path

        Returns:
            Crumb or None if not found
        """
        if not self.crumbs_dir:
            return None

        # Try with and without .md extension
        file_path = self.crumbs_dir / crumb_path
        if not file_path.suffix:
            file_path = file_path.with_suffix(".md")

        if not file_path.exists():
            return None

        return self.parse_crumb(file_path)

    def get_categories(self) -> dict[str, int]:
        """
        Get all categories with crumb counts.

        Returns:
            Dictionary of category name to count
        """
        crumbs = self.list_crumbs()
        categories: dict[str, int] = {}

        for crumb in crumbs:
            cat = crumb.metadata.category
            categories[cat] = categories.get(cat, 0) + 1

        return dict(sorted(categories.items()))

    def get_tags(self) -> dict[str, int]:
        """
        Get all tags with usage counts.

        Returns:
            Dictionary of tag to count
        """
        crumbs = self.list_crumbs()
        tags: dict[str, int] = {}

        for crumb in crumbs:
            for tag in crumb.metadata.tags:
                tags[tag] = tags.get(tag, 0) + 1

        return dict(sorted(tags.items()))

    def find_crumbs(
        self,
        query: str,
        in_field: str | None = None,
        case_sensitive: bool = False,
    ) -> list[Crumb]:
        """
        Find crumbs matching query.

        Args:
            query: Search query
            in_field: Search in specific field (title, description, tags, content)
            case_sensitive: Case-sensitive search

        Returns:
            List of matching crumbs
        """
        crumbs = self.list_crumbs()
        matches = []

        for crumb in crumbs:
            if in_field == "title":
                text = crumb.metadata.title
            elif in_field == "description":
                text = crumb.metadata.description
            elif in_field == "tags":
                text = " ".join(crumb.metadata.tags)
            elif in_field == "content":
                text = crumb.content
            else:
                # Search in all fields
                if crumb.matches_query(query, case_sensitive):
                    matches.append(crumb)
                continue

            # Search in specific field
            if not case_sensitive:
                text = text.lower()
                query = query.lower()

            if query in text:
                matches.append(crumb)

        return matches
