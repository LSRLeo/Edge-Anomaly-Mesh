# Reports Directory

This directory contains contributor reports for the edge-anomaly-mesh repository.

## Contents

- `SUMMARY.md` - Overview table of all contributors with aggregated stats
- `generate_reports.py` - Python script to regenerate all reports
- `{contributor_name}.md` - Individual reports for each contributor (13 total)

## Regenerating Reports

Run the script from the repository root:

```bash
python reports/generate_reports.py
```

## Scope

Reports are scoped to the **sprint-1 branches only**:
- `origin/db-team-sprint-1`
- `origin/de-team-sprint-1`
- `origin/ml-team-sprint-1`
- `origin/ui-team-sprint-1`

## Data Sources

**Git (local repository):**
- Commits (non-merge) per author
- Merge commits per author
- Lines added/deleted per author
- Files changed per author

**GitHub API (via `gh` CLI):**
- Issues created, commented
- PRs created, assigned, reviewed, merged

## Contributions Formula

```
Contributions = Commits + Issues Created + PRs Created + PRs Closed + PRs Reviewed
```

Note: Merge commits are tracked separately and not included in the contributions score.

## Summary Table Columns

| Column | Description |
|--------|-------------|
| Contributions | Aggregate score (see formula above) |
| Commits | Non-merge commits in sprint-1 branches |
| Merges | Merge commits (not in contributions) |
| Files | Unique files changed |
| Issues Created | GitHub issues opened |
| PRs Created | Pull requests authored |
| PRs Closed | PRs authored that are merged/closed |
| PRs Reviewed | PRs where user submitted a review |

## Individual Report Sections

- Summary table with all metrics
- Issues (created, commented)
- Pull Requests (created, assigned, reviewed, merged)
- Commits with lines added/deleted
- Files changed (full list)

## Contributor Mappings

The script consolidates contributors who use multiple identities:

**Email consolidation:** Contributors using multiple emails (e.g., personal + GitHub noreply) are merged into single reports. See `consolidate_contributors()` in the script.

**GitHub username aliases:**
- `TyEsmond` and `Troo4` are consolidated as Ty Esmond

**Excluded contributors:**
- Lily Trautman (instructor)
- Matt Rutherford (instructor)

## Modifying the Script

Key functions in `generate_reports.py`:

| Function | Purpose |
|----------|---------|
| `consolidate_contributors()` | Email-to-name mappings |
| `get_github_usernames()` | GitHub username aliases |
| `SPRINT1_BRANCHES` | Branches to analyze (top of file) |
