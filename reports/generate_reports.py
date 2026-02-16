#!/usr/bin/env python3
"""Generate contributor reports from git and GitHub data."""

import json
import subprocess
import os
from collections import defaultdict
from datetime import datetime

# Sprint-1 branches to analyze
SPRINT1_BRANCHES = [
    'origin/db-team-sprint-1',
    'origin/de-team-sprint-1',
    'origin/ml-team-sprint-1',
    'origin/ui-team-sprint-1',
]
BRANCH_SPEC = ' '.join(SPRINT1_BRANCHES)

# Team assignments (contributor name -> team name)
TEAMS = {
    'Sean Osman': 'DE',
    'Aldo Rios': 'DE',
    'Leo Liu': 'DE',
    'Ty Esmond': 'UI',
    'Owen Conlon': 'UI',
    'George Rumsey': 'UI',
    'Kailar Hayes': 'DB',
    'Hannah Caldini': 'DB',
    'Diego Ramirez': 'DB',
    'Daniel Kaplan': 'ML',
    'Tristian Bradley': 'ML',
    'Truman Davis': 'ML',
    'Alyssa Bulai': 'ML',
}

def run_cmd(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_commit_stats():
    """Get commit counts and lines changed per email from sprint-1 branches."""
    stats = {}
    emails = run_cmd(f"git log {BRANCH_SPEC} --format='%ae' | sort | uniq").split('\n')

    for email in emails:
        if not email:
            continue
        # Commit count (non-merge)
        count = run_cmd(f"git log {BRANCH_SPEC} --author='{email}' --no-merges --oneline | wc -l")
        # Merge commit count
        merge_count = run_cmd(f"git log {BRANCH_SPEC} --author='{email}' --merges --oneline | wc -l")
        # Lines changed
        numstat = run_cmd(f"git log {BRANCH_SPEC} --author='{email}' --no-merges --numstat --pretty='' | awk '{{add+=$1; del+=$2}} END {{printf \"%d %d\", add, del}}'")
        parts = numstat.split()
        added = int(parts[0]) if parts else 0
        deleted = int(parts[1]) if len(parts) > 1 else 0
        stats[email] = {
            'commits': int(count) if count else 0,
            'merge_commits': int(merge_count) if merge_count else 0,
            'lines_added': added,
            'lines_deleted': deleted
        }
    return stats

def get_github_data():
    """Get PR and issue data from GitHub."""
    pr_data = run_cmd("gh pr list --state all --limit 500 --json number,author,state,mergedBy,assignees,reviews 2>/dev/null")
    prs = json.loads(pr_data) if pr_data else []

    # Get all issues (open and closed)
    issues_data = run_cmd("gh issue list --state all --limit 500 --json number,author,state 2>/dev/null")
    issues = json.loads(issues_data) if issues_data else []

    # Get issue comments
    comments_data = run_cmd("gh api repos/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/comments --paginate 2>/dev/null")
    comments = json.loads(comments_data) if comments_data else []

    return prs, issues, comments

def get_files_changed_by_emails(emails):
    """Get list of files changed by contributor across their emails in sprint-1 branches."""
    files = set()
    for email in emails:
        output = run_cmd(f"git log {BRANCH_SPEC} --author='{email}' --no-merges --name-only --pretty=format: | sort | uniq")
        for line in output.split('\n'):
            line = line.strip()
            if line:
                files.add(line)
    return sorted(files)

def consolidate_contributors():
    """Consolidate contributors with multiple emails."""
    # Map multiple emails to canonical contributor
    # Excludes: Lily Trautman, Matt Rutherford
    email_groups = {
        'Sean Osman': ['96084662+Sean-Osman@users.noreply.github.com'],
        'Aldo Rios': ['124832719+arios123@users.noreply.github.com', 'aldorios369@gmail.com'],
        'Leo Liu': ['shirui.liu@du.edu', 'leoliu20041217@gmail.com'],
        'Ty Esmond': ['165939755+TyEsmond@users.noreply.github.com'],
        'Owen Conlon': ['167807269+ohenconlon@users.noreply.github.com', 'owen.conlon@du.edu'],
        'George Rumsey': ['123426918+georgerumsey@users.noreply.github.com', 'george.rumsey@du.edu'],
        'Kailar Hayes': ['165724913+Kailar-Hayes@users.noreply.github.com', 'kailar.hayes@du.edu'],
        'Hannah Caldini': ['166074733+hcaldini@users.noreply.github.com', 'hannah.caldini@du.edu'],
        'Diego Ramirez': ['diegoiramirez42@gmail.com'],
        'Daniel Kaplan': ['daniel.kaplan32@du.edu'],
        'Tristian Bradley': ['tristian.bradley@du.edu'],
        'Truman Davis': ['truman.davis@du.edu', 'ty@the3.com'],
        'Alyssa Bulai': ['alyssabulai@outlook.com'],
    }
    return email_groups

def get_github_usernames():
    """Get mapping of contributor names to GitHub usernames."""
    # Includes Troo4 as alias for TyEsmond
    return {
        'Sean Osman': ['Sean-Osman'],
        'Aldo Rios': ['arios123'],
        'Leo Liu': ['LSRLeo'],
        'Ty Esmond': ['TyEsmond', 'Troo4'],
        'Owen Conlon': ['ohenconlon'],
        'George Rumsey': ['georgerumsey'],
        'Kailar Hayes': ['Kailar-Hayes'],
        'Hannah Caldini': ['hcaldini'],
        'Diego Ramirez': ['Diego-Ramirez64'],
        'Daniel Kaplan': ['danielkaplan32'],
        'Tristian Bradley': ['TBradley06'],
        'Truman Davis': ['TrumanAD'],
        'Alyssa Bulai': ['alyssabulai'],
    }

def get_issue_stats(gh_usernames, issues, comments):
    """Get issue stats for a list of GitHub usernames."""
    usernames_lower = [u.lower() for u in gh_usernames]

    issues_created = []
    issues_commented = []

    for issue in issues:
        issue_num = issue.get('number')
        # gh issue list uses 'author' -> 'login'
        author = issue.get('author', {}).get('login', '').lower()

        if author in usernames_lower:
            issues_created.append(issue_num)

    # Count comments
    commented_issues = set()
    for comment in comments:
        commenter = comment.get('user', {}).get('login', '').lower()
        issue_url = comment.get('issue_url', '')
        if commenter in usernames_lower and issue_url:
            # Extract issue number from URL
            issue_num = int(issue_url.split('/')[-1])
            commented_issues.add(issue_num)

    issues_commented = sorted(commented_issues)

    return issues_created, issues_commented

def generate_report(name, gh_usernames, emails, commit_stats, prs, issues, comments):
    """Generate a markdown report for a contributor."""
    # Aggregate commit stats across all emails
    total_commits = 0
    total_added = 0
    total_deleted = 0
    for email in emails:
        if email in commit_stats:
            total_commits += commit_stats[email]['commits']
            total_added += commit_stats[email]['lines_added']
            total_deleted += commit_stats[email]['lines_deleted']

    # PR stats
    prs_created = []
    prs_assigned = []
    prs_reviewed = []
    prs_merged = []

    usernames_lower = [u.lower() for u in gh_usernames]

    for pr in prs:
        pr_num = pr['number']

        # Created
        if pr.get('author', {}).get('login', '').lower() in usernames_lower:
            prs_created.append(pr_num)

        # Assigned
        for assignee in pr.get('assignees', []):
            if assignee.get('login', '').lower() in usernames_lower:
                prs_assigned.append(pr_num)
                break

        # Reviewed
        for review in pr.get('reviews', []):
            if review.get('author', {}).get('login', '').lower() in usernames_lower:
                prs_reviewed.append(pr_num)
                break

        # Merged by
        if pr.get('mergedBy', {}) and pr['mergedBy'].get('login', '').lower() in usernames_lower:
            prs_merged.append(pr_num)

    # Issue stats
    issues_created, issues_commented = get_issue_stats(gh_usernames, issues, comments)

    # Get files changed
    files_changed = get_files_changed_by_emails(emails)
    files_list = '\n'.join([f'- `{f}`' for f in files_changed]) if files_changed else 'None'

    # Generate report content
    report = f"""# Contributor Report: {name}

**GitHub Username(s):** {', '.join(gh_usernames)}
**Email(s):** {', '.join(emails)}
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Branches Analyzed:** sprint-1 branches (db-team, de-team, ml-team, ui-team)

---

## Summary

| Metric | Count |
|--------|-------|
| Total Commits | {total_commits} |
| Lines Added | {total_added:,} |
| Lines Deleted | {total_deleted:,} |
| Net Lines Changed | {total_added - total_deleted:+,} |
| PRs Created | {len(prs_created)} |
| PRs Assigned | {len(prs_assigned)} |
| PRs Reviewed | {len(prs_reviewed)} |
| PRs Merged (as merger) | {len(prs_merged)} |
| Issues Created | {len(issues_created)} |
| Issues Commented | {len(issues_commented)} |
| Files Changed | {len(files_changed)} |

---

## Issues

### Created ({len(issues_created)})
{', '.join([f'#{n}' for n in sorted(issues_created)]) if issues_created else 'None'}

### Commented ({len(issues_commented)})
{', '.join([f'#{n}' for n in sorted(issues_commented)]) if issues_commented else 'None'}

---

## Pull Requests

### Created ({len(prs_created)})
{', '.join([f'#{n}' for n in sorted(prs_created)]) if prs_created else 'None'}

### Assigned ({len(prs_assigned)})
{', '.join([f'#{n}' for n in sorted(prs_assigned)]) if prs_assigned else 'None'}

### Reviewed ({len(prs_reviewed)})
{', '.join([f'#{n}' for n in sorted(prs_reviewed)]) if prs_reviewed else 'None'}

### Merged (as merger) ({len(prs_merged)})
{', '.join([f'#{n}' for n in sorted(prs_merged)]) if prs_merged else 'None'}

---

## Commits

Total non-merge commits in sprint-1 branches: **{total_commits}**

### Code Changes
- **Lines Added:** {total_added:,}
- **Lines Deleted:** {total_deleted:,}
- **Net Change:** {total_added - total_deleted:+,}

---

## Files Changed ({len(files_changed)})

{files_list}
"""
    return report

def main():
    print("Gathering git contributor data from sprint-1 branches...")
    print(f"  Branches: {', '.join(SPRINT1_BRANCHES)}")
    commit_stats = get_commit_stats()

    print("Gathering GitHub PR and issue data...")
    prs, issues, comments = get_github_data()
    print(f"  Found {len(prs)} PRs, {len(issues)} issues, {len(comments)} comments")

    print("Mapping contributors...")
    email_groups = consolidate_contributors()
    gh_usernames_map = get_github_usernames()

    # Generate reports
    reports_dir = os.path.dirname(os.path.abspath(__file__))

    print("\nGenerating reports...")
    for name, emails in email_groups.items():
        gh_usernames = gh_usernames_map.get(name, [])
        report = generate_report(name, gh_usernames, emails, commit_stats, prs, issues, comments)

        # Create filename from name
        filename = name.lower().replace(' ', '_') + '.md'
        filepath = os.path.join(reports_dir, filename)

        with open(filepath, 'w') as f:
            f.write(report)
        print(f"  Created: {filename}")

    # Generate summary report
    print("\nGenerating summary report...")
    summary = generate_summary(email_groups, gh_usernames_map, commit_stats, prs, issues, comments)
    with open(os.path.join(reports_dir, 'SUMMARY.md'), 'w') as f:
        f.write(summary)
    print("  Created: SUMMARY.md")

    print("\nDone!")

def generate_summary(email_groups, gh_usernames_map, commit_stats, prs, issues, comments):
    """Generate a summary report of all contributors."""
    rows = []

    for name, emails in sorted(email_groups.items()):
        gh_usernames = gh_usernames_map.get(name, [])
        usernames_lower = [u.lower() for u in gh_usernames]

        # Aggregate stats
        total_commits = sum(commit_stats.get(e, {}).get('commits', 0) for e in emails)
        total_merge_commits = sum(commit_stats.get(e, {}).get('merge_commits', 0) for e in emails)

        # Files changed
        files_changed = len(get_files_changed_by_emails(emails))

        # PR stats
        prs_created = sum(1 for pr in prs if pr.get('author', {}).get('login', '').lower() in usernames_lower)
        prs_closed = sum(1 for pr in prs if pr.get('author', {}).get('login', '').lower() in usernames_lower and pr.get('state') in ('MERGED', 'CLOSED'))
        prs_reviewed = sum(1 for pr in prs if any(r.get('author', {}).get('login', '').lower() in usernames_lower for r in pr.get('reviews', [])))
        prs_merged = sum(1 for pr in prs if pr.get('mergedBy', {}) and pr['mergedBy'].get('login', '').lower() in usernames_lower)

        # Issue stats
        issues_created_list, issues_commented_list = get_issue_stats(gh_usernames, issues, comments)
        issues_created = len(issues_created_list)
        issues_commented = len(issues_commented_list)

        # Contributions = commits + issues created + PRs created + PRs closed + PRs reviewed
        contributions = total_commits + issues_created + prs_created + prs_closed + prs_reviewed

        # Team assignment
        team = TEAMS.get(name, '?')

        rows.append({
            'name': name,
            'team': team,
            'gh': gh_usernames[0] if gh_usernames else '',
            'commits': total_commits,
            'merge_commits': total_merge_commits,
            'files_changed': files_changed,
            'issues_created': issues_created,
            'issues_commented': issues_commented,
            'prs_created': prs_created,
            'prs_closed': prs_closed,
            'prs_reviewed': prs_reviewed,
            'prs_merged': prs_merged,
            'contributions': contributions,
        })

    # Calculate team totals and normalized commits
    team_stats = {}
    for r in rows:
        team = r['team']
        if team not in team_stats:
            team_stats[team] = {'total_commits': 0, 'members': 0}
        team_stats[team]['total_commits'] += r['commits']
        team_stats[team]['members'] += 1

    # Add normalized commit score to each row
    for r in rows:
        team = r['team']
        team_total = team_stats[team]['total_commits']
        team_size = team_stats[team]['members']
        expected_pct = 100.0 / team_size if team_size > 0 else 0
        actual_pct = (r['commits'] / team_total * 100) if team_total > 0 else 0
        r['commit_diff'] = actual_pct - expected_pct  # +/- from expected

    # Sort by contributions (descending)
    rows.sort(key=lambda x: x['contributions'], reverse=True)

    summary = f"""# Contributor Summary Report

**Repository:** edge-anomaly-mesh
**Branches:** sprint-1 (db-team, de-team, ml-team, ui-team)
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Overview

**Column Definitions:**
- **Contributions** — Aggregate score: Commits + Issues + PRs Created + PRs Closed + PRs Reviewed
- **Commits** — Non-merge commits authored in sprint-1 branches
- **Commit +/-** — Percentage points above/below expected for team (expected = 100% / team size)
- **Merges** — Merge commits (PRs merged into sprint branch)
- **Files** — Unique files changed
- **Issues** — GitHub issues created
- **PRs Created** — Pull requests authored
- **PRs Reviewed** — Pull requests where contributor submitted a review

| Contributor | Team | Contributions | Commits | Commit +/- | Merges | Files | Issues | PRs Created | PRs Reviewed |
|-------------|------|---------------|---------|------------|--------|-------|--------|-------------|--------------|
"""

    for r in rows:
        diff_str = f"{r['commit_diff']:+.0f}%" if r['commits'] > 0 else "—"
        filename = r['name'].lower().replace(' ', '_') + '.md'
        summary += f"| [{r['name']}]({filename}) | {r['team']} | {r['contributions']} | {r['commits']} | {diff_str} | {r['merge_commits']} | {r['files_changed']} | {r['issues_created']} | {r['prs_created']} | {r['prs_reviewed']} |\n"

    # Totals
    total_contributions = sum(r['contributions'] for r in rows)
    total_commits = sum(r['commits'] for r in rows)
    total_merge_commits = sum(r['merge_commits'] for r in rows)
    total_files = sum(r['files_changed'] for r in rows)
    total_issues_created = sum(r['issues_created'] for r in rows)
    total_prs_created = sum(r['prs_created'] for r in rows)
    total_prs_reviewed = sum(r['prs_reviewed'] for r in rows)

    summary += f"| **TOTAL** | | **{total_contributions}** | **{total_commits}** | | **{total_merge_commits}** | **{total_files}** | **{total_issues_created}** | **{total_prs_created}** | **{total_prs_reviewed}** |\n"

    # Add team summary
    summary += """
---

## Team Summary

| Team | Members | Total Commits | Expected/Person |
|------|---------|---------------|-----------------|
"""
    for team in sorted(team_stats.keys()):
        stats = team_stats[team]
        expected = stats['total_commits'] / stats['members'] if stats['members'] > 0 else 0
        summary += f"| {team} | {stats['members']} | {stats['total_commits']} | {expected:.1f} |\n"

    summary += """
---

*Contributions = Commits + Issues Created + PRs Created + PRs Closed + PRs Reviewed*
"""
    return summary

if __name__ == '__main__':
    main()
