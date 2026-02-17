#!/usr/bin/env python3
"""Generate contributor reports from git and GitHub data."""

import json
import subprocess
import os
from collections import defaultdict
from datetime import datetime

# Main branch to analyze
BRANCH_SPEC = 'origin/main'

# Sprint-1 branches (kept for future reference)
SPRINT1_BRANCHES = [
    'origin/db-team-sprint-1',
    'origin/de-team-sprint-1',
    'origin/ml-team-sprint-1',
    'origin/ui-team-sprint-1',
]

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
    """Get commit counts and lines changed per email from main branch."""
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
    pr_data = run_cmd("gh pr list --state all --limit 500 --json number,author,state,mergedBy,assignees,reviews,createdAt,mergedAt,closedAt 2>/dev/null")
    prs = json.loads(pr_data) if pr_data else []

    # Get all issues (open and closed)
    issues_data = run_cmd("gh issue list --state all --limit 500 --json number,author,state,createdAt 2>/dev/null")
    issues = json.loads(issues_data) if issues_data else []

    # Get issue comments
    comments_data = run_cmd("gh api repos/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/comments --paginate 2>/dev/null")
    comments = json.loads(comments_data) if comments_data else []

    return prs, issues, comments

def get_timeline_data(prs, issues, comments):
    """Get daily totals for each contribution metric (excluding instructors)."""
    from collections import defaultdict

    # Excluded instructors
    excluded_emails = [
        'llibet.trautman@du.edu',
        'matthew.rutherford@du.edu',
        '38080624+mjrutherford-du@users.noreply.github.com',
    ]
    excluded_usernames = ['lilytrautman', 'mjrutherford-du']

    def is_excluded_user(login):
        return login and login.lower() in [u.lower() for u in excluded_usernames]

    timeline = defaultdict(lambda: {
        'commits': 0,
        'issues_created': 0,
        'issues_commented': 0,
        'prs_created': 0,
        'prs_merged': 0,
        'prs_reviewed': 0,
    })

    # Get commits by date from git (excluding instructors)
    commit_data = run_cmd(f"git log {BRANCH_SPEC} --no-merges --format='%as %ae'")
    for line in commit_data.split('\n'):
        if line:
            parts = line.split(' ', 1)
            if len(parts) == 2:
                date, email = parts
                if email.lower() not in [e.lower() for e in excluded_emails]:
                    timeline[date]['commits'] += 1

    # Issues created by date (excluding instructors)
    for issue in issues:
        author = issue.get('author', {}).get('login', '')
        if is_excluded_user(author):
            continue
        created_at = issue.get('createdAt', '')
        if created_at:
            date = created_at[:10]  # Extract YYYY-MM-DD
            timeline[date]['issues_created'] += 1

    # Issue comments by date (excluding instructors)
    for comment in comments:
        commenter = comment.get('user', {}).get('login', '')
        if is_excluded_user(commenter):
            continue
        created_at = comment.get('created_at', '')
        if created_at:
            date = created_at[:10]
            timeline[date]['issues_commented'] += 1

    # PRs created by date (excluding instructors)
    for pr in prs:
        author = pr.get('author', {}).get('login', '')
        if not is_excluded_user(author):
            created_at = pr.get('createdAt', '')
            if created_at:
                date = created_at[:10]
                timeline[date]['prs_created'] += 1

        # PRs merged by date (exclude if merger is instructor)
        merger = pr.get('mergedBy', {})
        if merger and not is_excluded_user(merger.get('login', '')):
            merged_at = pr.get('mergedAt', '')
            if merged_at:
                date = merged_at[:10]
                timeline[date]['prs_merged'] += 1

    # Get PR reviews with dates (excluding instructors)
    for pr in prs:
        if pr.get('reviews'):
            pr_num = pr['number']
            reviews_data = run_cmd(f"gh api repos/ComputerScienceUniversityofDenver/edge-anomly-mesh/pulls/{pr_num}/reviews 2>/dev/null")
            if reviews_data:
                reviews = json.loads(reviews_data)
                for review in reviews:
                    reviewer = review.get('user', {}).get('login', '')
                    if is_excluded_user(reviewer):
                        continue
                    submitted_at = review.get('submitted_at', '')
                    if submitted_at:
                        date = submitted_at[:10]
                        timeline[date]['prs_reviewed'] += 1

    return dict(timeline)

def get_files_changed_by_emails(emails):
    """Get list of files changed by contributor across their emails in main branch."""
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
        'Ty Esmond': ['165939755+TyEsmond@users.noreply.github.com', 'ty@the3.com'],
        'Owen Conlon': ['167807269+ohenconlon@users.noreply.github.com', 'owen.conlon@du.edu'],
        'George Rumsey': ['123426918+georgerumsey@users.noreply.github.com', 'george.rumsey@du.edu'],
        'Kailar Hayes': ['165724913+Kailar-Hayes@users.noreply.github.com', 'kailar.hayes@du.edu'],
        'Hannah Caldini': ['166074733+hcaldini@users.noreply.github.com', 'hannah.caldini@du.edu'],
        'Diego Ramirez': ['diegoiramirez42@gmail.com'],
        'Daniel Kaplan': ['daniel.kaplan32@du.edu'],
        'Tristian Bradley': ['tristian.bradley@du.edu'],
        'Truman Davis': ['truman.davis@du.edu'],
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
**Branches Analyzed:** main

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

Total non-merge commits in main branch: **{total_commits}**

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
    print("Gathering git contributor data from main branch...")
    print(f"  Branch: {BRANCH_SPEC}")
    commit_stats = get_commit_stats()

    print("Gathering GitHub PR and issue data...")
    prs, issues, comments = get_github_data()
    print(f"  Found {len(prs)} PRs, {len(issues)} issues, {len(comments)} comments")

    print("Building timeline data...")
    timeline = get_timeline_data(prs, issues, comments)
    print(f"  Found activity across {len(timeline)} days")

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
    summary = generate_summary(email_groups, gh_usernames_map, commit_stats, prs, issues, comments, timeline)
    with open(os.path.join(reports_dir, 'SUMMARY.md'), 'w') as f:
        f.write(summary)
    print("  Created: SUMMARY.md")

    print("\nDone!")

def generate_summary(email_groups, gh_usernames_map, commit_stats, prs, issues, comments, timeline):
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

        # Weighted contributions: Commits 50%, Issues 25%, PRs 25%
        issues_score = issues_created + issues_commented
        prs_score = prs_created + prs_closed + prs_reviewed + prs_merged
        contributions = (total_commits * 0.5) + (issues_score * 0.25) + (prs_score * 0.25)

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

    # Calculate team totals for all metrics
    team_stats = {}
    for r in rows:
        team = r['team']
        if team not in team_stats:
            team_stats[team] = {
                'members': 0,
                'commits': 0,
                'issues_created': 0,
                'issues_commented': 0,
                'prs_created': 0,
                'prs_reviewed': 0,
                'prs_merged': 0,
            }
        team_stats[team]['members'] += 1
        team_stats[team]['commits'] += r['commits']
        team_stats[team]['issues_created'] += r['issues_created']
        team_stats[team]['issues_commented'] += r['issues_commented']
        team_stats[team]['prs_created'] += r['prs_created']
        team_stats[team]['prs_reviewed'] += r['prs_reviewed']
        team_stats[team]['prs_merged'] += r['merge_commits']

    # Add normalized commit score to each row
    for r in rows:
        team = r['team']
        team_total = team_stats[team]['commits']
        team_size = team_stats[team]['members']
        expected_pct = 100.0 / team_size if team_size > 0 else 0
        actual_pct = (r['commits'] / team_total * 100) if team_total > 0 else 0
        r['commit_diff'] = actual_pct - expected_pct  # +/- from expected

    # Sort by contributions (descending)
    rows.sort(key=lambda x: x['contributions'], reverse=True)

    summary = f"""# Contributor Summary Report

**Repository:** edge-anomaly-mesh
**Branches:** main
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Contributions

### Team Summary

| Team | Members | Commits | Issues | Comments | PRs Created | PRs Reviewed | PRs Merged | Commits/Person |
|------|---------|---------|--------|----------|-------------|--------------|------------|----------------|
"""
    for team in sorted(team_stats.keys()):
        stats = team_stats[team]
        members = stats['members']
        commits_per = stats['commits'] / members if members > 0 else 0
        summary += f"| {team} | {members} | {stats['commits']} | {stats['issues_created']} | {stats['issues_commented']} | {stats['prs_created']} | {stats['prs_reviewed']} | {stats['prs_merged']} | {commits_per:.1f} |\n"

    summary += """
### By Individual

**Column Definitions:**
- **Contributions** — Weighted score: (Commits × 50%) + (Issues × 25%) + (PRs × 25%)
- **Commits** — Non-merge commits authored in main branch
- **Commit +/-** — Percentage points above/below expected for team (expected = 100% / team size)
- **Files** — Unique files changed
- **Issues** — GitHub issues created
- **Comments** — GitHub issue comments
- **PRs Created** — Pull requests authored
- **PRs Reviewed** — Pull requests where contributor submitted a review
- **PRs Merged** — PRs merged by contributor

| Contributor | Team | Contributions | Commits | Commit +/- | Files | Issues | Comments | PRs Created | PRs Reviewed | PRs Merged |
|-------------|------|---------------|---------|------------|-------|--------|----------|-------------|--------------|------------|
"""

    for r in rows:
        diff_str = f"{r['commit_diff']:+.0f}%" if r['commits'] > 0 else "—"
        filename = r['name'].lower().replace(' ', '_') + '.md'
        summary += f"| [{r['name']}]({filename}) | {r['team']} | {r['contributions']:.1f} | {r['commits']} | {diff_str} | {r['files_changed']} | {r['issues_created']} | {r['issues_commented']} | {r['prs_created']} | {r['prs_reviewed']} | {r['merge_commits']} |\n"

    # Totals
    total_contributions = sum(r['contributions'] for r in rows)
    total_commits = sum(r['commits'] for r in rows)
    total_merge_commits = sum(r['merge_commits'] for r in rows)
    total_files = sum(r['files_changed'] for r in rows)
    total_issues_created = sum(r['issues_created'] for r in rows)
    total_issues_commented = sum(r['issues_commented'] for r in rows)
    total_prs_created = sum(r['prs_created'] for r in rows)
    total_prs_reviewed = sum(r['prs_reviewed'] for r in rows)

    summary += f"| **TOTAL** | | **{total_contributions:.1f}** | **{total_commits}** | | **{total_files}** | **{total_issues_created}** | **{total_issues_commented}** | **{total_prs_created}** | **{total_prs_reviewed}** | **{total_merge_commits}** |\n"

    # Add timeline section
    from datetime import date as date_class, timedelta

    # Week 1 starts on January 5, 2026 (Monday)
    week1_start = date_class(2026, 1, 5)

    def get_week_number(date_str):
        """Get week number where Week 1 starts Jan 5, 2026."""
        d = date_class.fromisoformat(date_str)
        if d < week1_start:
            return 0  # Before Week 1
        days_since = (d - week1_start).days
        return (days_since // 7) + 1

    def get_week_range(week_num):
        """Get the date range string for a week number."""
        start = week1_start + timedelta(days=(week_num - 1) * 7)
        end = start + timedelta(days=6)
        return f"{start.strftime('%b %d')} - {end.strftime('%b %d')}"

    # Filter and sort dates chronologically starting from Jan 5
    filtered_dates = sorted([d for d in timeline.keys() if d >= '2026-01-05'])

    # Aggregate by week
    weekly = {}
    for date_str in filtered_dates:
        week_num = get_week_number(date_str)
        if week_num not in weekly:
            weekly[week_num] = {
                'commits': 0, 'issues_created': 0, 'issues_commented': 0,
                'prs_created': 0, 'prs_merged': 0, 'prs_reviewed': 0
            }
        day = timeline[date_str]
        for key in weekly[week_num]:
            weekly[week_num][key] += day[key]

    # By Week table
    summary += """
---

## Timeline

### By Week

| Week | Dates | Commits | Issues Created | Issues Commented | PRs Created | PRs Merged | PRs Reviewed |
|------|-------|---------|----------------|------------------|-------------|------------|--------------|
"""
    for week_num in sorted(weekly.keys()):
        w = weekly[week_num]
        date_range = get_week_range(week_num)
        summary += f"| Week {week_num} | {date_range} | {w['commits']} | {w['issues_created']} | {w['issues_commented']} | {w['prs_created']} | {w['prs_merged']} | {w['prs_reviewed']} |\n"

    # By Day table with week boundaries
    summary += """
### By Day

| Date | Day | Commits | Issues Created | Issues Commented | PRs Created | PRs Merged | PRs Reviewed |
|------|-----|---------|----------------|------------------|-------------|------------|--------------|
"""
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    current_week = None
    for date_str in filtered_dates:
        week_num = get_week_number(date_str)
        d = date_class.fromisoformat(date_str)
        day_name = day_names[d.weekday()]

        # Add week header row (centered)
        if week_num != current_week:
            date_range = get_week_range(week_num)
            summary += f"| | | | **Week {week_num}:** {date_range} | | | | |\n"
        current_week = week_num

        day = timeline[date_str]
        summary += f"| {date_str} | {day_name} | {day['commits']} | {day['issues_created']} | {day['issues_commented']} | {day['prs_created']} | {day['prs_merged']} | {day['prs_reviewed']} |\n"

    summary += """
---

*Contributions = (Commits × 50%) + (Issues Created + Issues Commented × 25%) + (PRs Created + PRs Closed + PRs Reviewed + PRs Merged × 25%)*
"""
    return summary

if __name__ == '__main__':
    main()
