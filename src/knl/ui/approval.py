"""Interactive approval UI for documentation updates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

from ..models.docs import DocUpdate, DocUpdateProposal


class EnrichedDocUpdate(BaseModel):
    """
    DocUpdate enriched with UI-friendly fields.

    This wraps DocUpdate and adds fields needed by the approval UI.
    """

    # Original update
    original: DocUpdate

    # Enriched fields for UI
    file_path: Path
    gap_description: str | None = None

    # Map model fields to UI-friendly names
    @property
    def type(self) -> str:
        return self.original.type.value

    @property
    def old_text(self) -> str | None:
        return self.original.old

    @property
    def new_text(self) -> str:
        return self.original.new

    @property
    def reason(self) -> str:
        return self.original.reason

    @property
    def priority(self) -> str:
        return self.original.severity.value

    @property
    def line_start(self) -> int | None:
        return self.original.line_number

    @property
    def line_end(self) -> int | None:
        # Estimate end line based on content
        if self.original.old and self.original.line_number:
            return self.original.line_number + len(self.original.old.splitlines()) - 1
        return self.original.line_number


class ApprovalResult(Enum):
    """Result of approval session."""

    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    SKIPPED = "skipped"
    QUIT = "quit"


@dataclass
class UpdateReview:
    """Review decision for a single update."""

    update: EnrichedDocUpdate
    action: ApprovalResult
    edited_content: str | None = None  # For EDITED action


class ApprovalUI:
    """
    Interactive UI for reviewing and approving documentation updates.

    Presents each update with a diff, allows user to accept, reject, edit,
    skip, or quit the review process.
    """

    def __init__(self, console: Console | None = None) -> None:
        """
        Initialize approval UI.

        Args:
            console: Rich console instance (creates new one if not provided)
        """
        self.console = console or Console()
        self.reviews: list[UpdateReview] = []
        self.current_index = 0

    def review_proposal(
        self,
        proposal: DocUpdateProposal,
        auto_approve: bool = False,
    ) -> list[UpdateReview]:
        """
        Review a documentation update proposal.

        Args:
            proposal: Proposal to review
            auto_approve: If True, automatically approve all updates

        Returns:
            List of review decisions
        """
        if auto_approve:
            return self._auto_approve_all(proposal)

        # Show initial summary
        self._show_summary(proposal)

        # Wait for user to start
        if not self._confirm_start():
            return []

        # Review each update
        all_updates = self._flatten_updates(proposal)
        self.reviews = []
        self.current_index = 0

        while self.current_index < len(all_updates):
            update = all_updates[self.current_index]
            action = self._review_update(update, self.current_index + 1, len(all_updates))

            if action == ApprovalResult.QUIT:
                # User quit - return reviews so far
                break
            elif action == ApprovalResult.SKIPPED:
                # Skip for now - don't add to reviews
                self.current_index += 1
            else:
                # Accept, reject, or edit - record decision
                self.reviews.append(
                    UpdateReview(
                        update=update,
                        action=action,
                        edited_content=None,  # TODO: Capture edited content
                    )
                )
                self.current_index += 1

        # Show completion summary
        self._show_completion_summary()

        return self.reviews

    def _flatten_updates(self, proposal: DocUpdateProposal) -> list[EnrichedDocUpdate]:
        """
        Flatten all updates from proposal into enriched list.

        Args:
            proposal: Proposal containing file updates

        Returns:
            List of enriched doc updates with file context
        """
        enriched_updates = []
        for file_update in proposal.files:
            for update in file_update.updates:
                # Find matching gap description if available
                gap_desc = None
                for gap in proposal.gaps:
                    if file_update.path in gap.affected_files:
                        gap_desc = gap.description
                        break

                # Create enriched update
                enriched = EnrichedDocUpdate(
                    original=update,
                    file_path=file_update.path,
                    gap_description=gap_desc,
                )
                enriched_updates.append(enriched)
        return enriched_updates

    def _auto_approve_all(self, proposal: DocUpdateProposal) -> list[UpdateReview]:
        """
        Auto-approve all updates without user interaction.

        Args:
            proposal: Proposal to approve

        Returns:
            List of approved reviews
        """
        updates = self._flatten_updates(proposal)
        self.console.print("[dim]Auto-approving all updates...[/dim]")

        reviews = [
            UpdateReview(update=update, action=ApprovalResult.APPROVED)
            for update in updates
        ]

        self.console.print(f"[green]✓[/green] Auto-approved {len(reviews)} updates\n")
        return reviews

    def _show_summary(self, proposal: DocUpdateProposal) -> None:
        """
        Show initial summary of the proposal.

        Args:
            proposal: Proposal to summarize
        """
        self.console.print()
        self.console.print(
            Panel(
                f"[bold]KNL Documentation Update Approval[/bold]\n"
                f"Task: {proposal.task_id} - {proposal.task_title}",
                border_style="cyan",
            )
        )

        # Count updates by priority
        all_updates = self._flatten_updates(proposal)
        critical = sum(1 for u in all_updates if u.priority == "critical")
        high = sum(1 for u in all_updates if u.priority == "high")
        medium = sum(1 for u in all_updates if u.priority == "medium")
        low = sum(1 for u in all_updates if u.priority == "low")

        self.console.print("\n[bold]Analysis Summary:[/bold]")
        self.console.print(f"  Scope: {proposal.scope}")
        self.console.print(f"  Gaps found: {len(proposal.gaps)} ({critical} critical, {high} high, {medium} medium, {low} low)")
        self.console.print(f"  Files to update: {len(proposal.files)}")
        self.console.print(f"  Total updates: {len(all_updates)}")
        self.console.print(f"  Confidence: {int(proposal.confidence * 100)}%\n")

        # List files
        self.console.print("[bold]Files to update:[/bold]")
        for i, file_update in enumerate(proposal.files, 1):
            file_critical = sum(1 for u in file_update.updates if u.priority == "critical")
            file_high = sum(1 for u in file_update.updates if u.priority == "high")
            file_medium = sum(1 for u in file_update.updates if u.priority == "medium")

            priority_str = []
            if file_critical:
                priority_str.append(f"[red]{file_critical} critical[/red]")
            if file_high:
                priority_str.append(f"[yellow]{file_high} high[/yellow]")
            if file_medium:
                priority_str.append(f"[blue]{file_medium} medium[/blue]")

            priority_display = ", ".join(priority_str) if priority_str else "[dim]low[/dim]"

            self.console.print(
                f"  {i}. [cyan]{file_update.path}[/cyan] "
                f"({len(file_update.updates)} updates: {priority_display})"
            )

        self.console.print()

    def _confirm_start(self) -> bool:
        """
        Ask user to confirm starting the review.

        Returns:
            True if user wants to start, False otherwise
        """
        response = Prompt.ask(
            "Press [green]Enter[/green] to start review, [red]Q[/red] to quit",
            default="",
            show_default=False,
        )
        return response.upper() != "Q"

    def _review_update(self, update: EnrichedDocUpdate, number: int, total: int) -> ApprovalResult:
        """
        Review a single update.

        Args:
            update: Update to review
            number: Update number (1-indexed)
            total: Total number of updates

        Returns:
            Approval action taken
        """
        # Clear screen and show update
        self.console.print("\n" * 2)

        # Priority color
        priority_colors = {
            "critical": "red",
            "high": "yellow",
            "medium": "blue",
            "low": "dim",
        }
        priority_color = priority_colors.get(update.priority, "dim")

        # Header
        self.console.print(
            Panel(
                f"Update {number}/{total} │ [cyan]{update.file_path}[/cyan] │ "
                f"Priority: [{priority_color}]{update.priority.upper()}[/{priority_color}]",
                border_style="cyan",
            )
        )

        # Show reason and gap
        self.console.print(f"\n[bold]Reason:[/bold] {update.reason}")
        if update.gap_description:
            self.console.print(f"[bold]Gap:[/bold] {update.gap_description}\n")

        # Show current text if available
        if update.old_text:
            self.console.print(f"[bold]Current text (lines {update.line_start}-{update.line_end}):[/bold]")
            current_syntax = Syntax(
                update.old_text,
                "markdown",
                theme="monokai",
                line_numbers=True,
                start_line=update.line_start or 1,
            )
            self.console.print(Panel(current_syntax, border_style="dim"))

        # Show proposed change
        self.console.print("\n[bold]Proposed change:[/bold]")
        proposed_syntax = Syntax(
            update.new_text,
            "markdown",
            theme="monokai",
            line_numbers=True,
            start_line=update.line_start or 1,
        )
        self.console.print(Panel(proposed_syntax, border_style="green"))

        # Show diff if we have both old and new
        if update.old_text:
            self._show_diff(update)

        # Get user action
        return self._get_user_action()

    def _show_diff(self, update: EnrichedDocUpdate) -> None:
        """
        Show a diff between old and new text.

        Args:
            update: Update with old and new text
        """
        if not update.old_text:
            return

        self.console.print("\n[bold]Diff:[/bold]")

        # Simple line-by-line diff
        old_lines = update.old_text.splitlines()
        new_lines = update.new_text.splitlines()

        # Find common prefix/suffix to minimize diff
        start_line = update.line_start or 1

        # Show diff
        diff_lines = []
        for i, (old, new) in enumerate(zip(old_lines, new_lines, strict=False), start=start_line):
            if old != new:
                diff_lines.append(f"  {i:3d} │ [red]-{old}[/red]")
                diff_lines.append(f"  {i:3d} │ [green]+{new}[/green]")
            else:
                diff_lines.append(f"  {i:3d} │  {old}")

        # Handle length differences
        if len(old_lines) > len(new_lines):
            for i, line in enumerate(old_lines[len(new_lines):], start=start_line + len(new_lines)):
                diff_lines.append(f"  {i:3d} │ [red]-{line}[/red]")
        elif len(new_lines) > len(old_lines):
            for i, line in enumerate(new_lines[len(old_lines):], start=start_line + len(old_lines)):
                diff_lines.append(f"  {i:3d} │ [green]+{line}[/green]")

        for line in diff_lines[:20]:  # Limit to 20 lines
            self.console.print(line)

        if len(diff_lines) > 20:
            self.console.print(f"  [dim]... {len(diff_lines) - 20} more lines[/dim]")

        self.console.print()

    def _get_user_action(self) -> ApprovalResult:
        """
        Get user's action for current update.

        Returns:
            User's chosen action
        """
        self.console.print("[bold]Actions:[/bold]")
        self.console.print("  [green][A][/green] Accept    ", end="")
        self.console.print("[red][R][/red] Reject    ", end="")
        self.console.print("[cyan][E][/cyan] Edit    ", end="")
        self.console.print("[yellow][S][/yellow] Skip    ", end="")
        self.console.print("[dim][Q][/dim] Quit")

        while True:
            choice = Prompt.ask(
                "\nChoice",
                choices=["a", "r", "e", "s", "q", "A", "R", "E", "S", "Q"],
                show_choices=False,
            ).upper()

            if choice == "A":
                self.console.print("[green]✓ Accepted[/green]")
                return ApprovalResult.APPROVED
            elif choice == "R":
                self.console.print("[red]✗ Rejected[/red]")
                return ApprovalResult.REJECTED
            elif choice == "E":
                self.console.print("[yellow]Note:[/yellow] Edit mode not yet implemented")
                # TODO: Implement edit mode
                continue
            elif choice == "S":
                self.console.print("[dim]⊘ Skipped[/dim]")
                return ApprovalResult.SKIPPED
            elif choice == "Q":
                confirm = Prompt.ask(
                    "[yellow]Quit review?[/yellow] Progress will be saved",
                    choices=["y", "n", "Y", "N"],
                    default="n",
                )
                if confirm.upper() == "Y":
                    return ApprovalResult.QUIT
                continue

    def _show_completion_summary(self) -> None:
        """Show summary after review is complete."""
        self.console.print("\n" * 2)
        self.console.print(Panel("[bold]Documentation Update Complete[/bold]", border_style="green"))

        # Count actions
        accepted = sum(1 for r in self.reviews if r.action == ApprovalResult.APPROVED)
        rejected = sum(1 for r in self.reviews if r.action == ApprovalResult.REJECTED)
        edited = sum(1 for r in self.reviews if r.action == ApprovalResult.EDITED)

        self.console.print("\n[bold]Review Summary:[/bold]")
        self.console.print(f"  Reviewed: {len(self.reviews)} updates")
        self.console.print(f"  [green]Accepted: {accepted}[/green]")
        if edited:
            self.console.print(f"  [cyan]Edited: {edited}[/cyan]")
        if rejected:
            self.console.print(f"  [red]Rejected: {rejected}[/red]")

        # Group by file
        files_modified = {}
        for review in self.reviews:
            if review.action in (ApprovalResult.APPROVED, ApprovalResult.EDITED):
                path = review.update.file_path
                files_modified[path] = files_modified.get(path, 0) + 1

        if files_modified:
            self.console.print("\n[bold]Changes Applied:[/bold]")
            for path, count in files_modified.items():
                self.console.print(f"  [green]✓[/green] [cyan]{path}[/cyan] ({count} updates)")

        # Skipped (rejected)
        if rejected:
            self.console.print("\n[bold]Skipped:[/bold]")
            for review in self.reviews:
                if review.action == ApprovalResult.REJECTED:
                    self.console.print(
                        f"  [red]✗[/red] {review.update.file_path}:{review.update.line_start} "
                        f"- {review.update.reason}"
                    )

        # Next steps
        self.console.print("\n[bold]Next Steps:[/bold]")
        if accepted or edited:
            self.console.print("  • Run [cyan]knl docs check[/cyan] to verify all docs are in sync")
            self.console.print("  • Review and commit the changes")
            self.console.print("  • Consider running [cyan]knl docs sync[/cyan] for CLI reference")
        else:
            self.console.print("  • No changes were applied")

        self.console.print()

    def get_approved_updates(self) -> list[EnrichedDocUpdate]:
        """
        Get list of approved updates.

        Returns:
            List of approved doc updates
        """
        return [
            review.update
            for review in self.reviews
            if review.action in (ApprovalResult.APPROVED, ApprovalResult.EDITED)
        ]

    def apply_updates(self, repo_root: Path | None = None) -> dict[str, int]:
        """
        Apply approved updates to files.

        Args:
            repo_root: Repository root directory (defaults to current dir)

        Returns:
            Dictionary mapping file path to number of updates applied
        """
        repo_root = repo_root or Path.cwd()
        updates_by_file: dict[str, list[EnrichedDocUpdate]] = {}

        # Group updates by file
        for review in self.reviews:
            if review.action not in (ApprovalResult.APPROVED, ApprovalResult.EDITED):
                continue

            path = str(review.update.file_path)
            if path not in updates_by_file:
                updates_by_file[path] = []
            updates_by_file[path].append(review.update)

        # Apply updates to each file
        results = {}
        for path, updates in updates_by_file.items():
            file_path = repo_root / path
            try:
                count = self._apply_file_updates(file_path, updates)
                results[path] = count
                self.console.print(f"[green]✓[/green] Updated {path} ({count} changes)")
            except Exception as e:
                self.console.print(f"[red]Error:[/red] Failed to update {path}: {e}")
                results[path] = 0

        return results

    def _apply_file_updates(self, file_path: Path, updates: list[EnrichedDocUpdate]) -> int:
        """
        Apply updates to a single file.

        Args:
            file_path: Path to file
            updates: List of enriched updates to apply

        Returns:
            Number of updates applied
        """
        # Sort updates by line number (descending) to avoid offset issues
        sorted_updates = sorted(
            updates,
            key=lambda u: u.line_start or 0,
            reverse=True,
        )

        # Read file
        if file_path.exists():
            lines = file_path.read_text().splitlines(keepends=True)
        else:
            lines = []

        # Apply each update
        count = 0
        for update in sorted_updates:
            if update.type == "replace" and update.line_start and update.line_end:
                # Replace lines
                start = update.line_start - 1  # Convert to 0-indexed
                end = update.line_end

                new_lines = update.new_text.splitlines(keepends=True)
                lines[start:end] = new_lines
                count += 1

            elif update.type == "insert" and update.line_start:
                # Insert lines
                start = update.line_start - 1
                new_lines = update.new_text.splitlines(keepends=True)
                lines[start:start] = new_lines
                count += 1

            elif update.type == "append":
                # Append to end
                new_lines = update.new_text.splitlines(keepends=True)
                lines.extend(new_lines)
                count += 1

        # Write file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("".join(lines))

        return count
