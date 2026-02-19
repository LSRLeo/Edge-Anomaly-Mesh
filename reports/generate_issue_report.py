#!/usr/bin/env python3
"""Generate issue report grouped by team labels and assignees."""

import json
import subprocess
from collections import defaultdict
from datetime import datetime

# Team labels to group by
TEAM_LABELS = ['ML TEAM', 'DB TEAM', 'DE TEAM', 'UI TEAM']

# GitHub username to student name mapping
GITHUB_TO_NAME = {
    'sean-osman': 'Sean Osman',
    'arios123': 'Aldo Rios',
    'lsrleo': 'Leo Liu',
    'tyesmond': 'Ty Esmond',
    'troo4': 'Ty Esmond',
    'ohenconlon': 'Owen Conlon',
    'georgerumsey': 'George Rumsey',
    'kailar-hayes': 'Kailar Hayes',
    'hcaldini': 'Hannah Caldini',
    'diego-ramirez64': 'Diego Ramirez',
    'danielkaplan32': 'Daniel Kaplan',
    'tbradley06': 'Tristian Bradley',
    'trumanad': 'Truman Davis',
    'alyssabulai': 'Alyssa Bulai',
}

# Team membership (team label -> list of GitHub usernames)
TEAM_MEMBERS = {
    'ML TEAM': ['danielkaplan32', 'TBradley06', 'TrumanAD', 'alyssabulai'],
    'DB TEAM': ['Kailar-Hayes', 'hcaldini', 'Diego-Ramirez64'],
    'DE TEAM': ['Sean-Osman', 'arios123', 'LSRLeo'],
    'UI TEAM': ['TyEsmond', 'ohenconlon', 'georgerumsey'],
}

# Excluded users (instructors)
EXCLUDED_USERS = ['lilytrautman', 'mjrutherford-du']


def run_cmd(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_issues():
    """Fetch all issues from GitHub."""
    issues_data = run_cmd(
        "gh issue list --state all --limit 500 "
        "--json number,title,state,labels,assignees,milestone,author,createdAt,closedAt "
        "2>/dev/null"
    )
    return json.loads(issues_data) if issues_data else []


def is_backlog_milestone(milestone):
    """Check if milestone is a backlog milestone."""
    if not milestone:
        return False
    name = milestone.get('title', '').lower()
    return 'backlog' in name


def get_team_label(labels):
    """Get team label from issue labels, or None if no team label."""
    for label in labels:
        label_name = label.get('name', '')
        if label_name in TEAM_LABELS:
            return label_name
    return None


def get_assignee_name(login):
    """Convert GitHub login to student name."""
    return GITHUB_TO_NAME.get(login.lower(), login)


def generate_report(issues):
    """Generate the markdown report."""
    # Filter out backlog issues and instructor-only issues
    filtered_issues = []
    for issue in issues:
        if is_backlog_milestone(issue.get('milestone')):
            continue
        filtered_issues.append(issue)

    # Group by team label
    by_team = defaultdict(list)
    no_team = []

    for issue in filtered_issues:
        labels = issue.get('labels', [])
        team = get_team_label(labels)
        if team:
            by_team[team].append(issue)
        else:
            no_team.append(issue)

    # Group by assignee within each team
    def group_by_assignee(issue_list):
        by_assignee = defaultdict(list)
        unassigned = []
        for issue in issue_list:
            assignees = issue.get('assignees', [])
            if assignees:
                for assignee in assignees:
                    login = assignee.get('login', '')
                    if login.lower() not in EXCLUDED_USERS:
                        by_assignee[login].append(issue)
            else:
                unassigned.append(issue)
        return by_assignee, unassigned

    # Build report
    report = f"""# Issue Report

**Repository:** edge-anomaly-mesh
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Issues:** {len(filtered_issues)} (excluding backlog milestones)

---

## Summary

| Team | Open | Closed | Total |
|------|------|--------|-------|
"""

    # Summary stats
    for team in TEAM_LABELS:
        team_issues = by_team.get(team, [])
        open_count = sum(1 for i in team_issues if i.get('state') == 'OPEN')
        closed_count = sum(1 for i in team_issues if i.get('state') == 'CLOSED')
        report += f"| {team} | {open_count} | {closed_count} | {len(team_issues)} |\n"

    # No team label
    open_no_team = sum(1 for i in no_team if i.get('state') == 'OPEN')
    closed_no_team = sum(1 for i in no_team if i.get('state') == 'CLOSED')
    report += f"| (No Team Label) | {open_no_team} | {closed_no_team} | {len(no_team)} |\n"

    # Totals
    total_open = sum(1 for i in filtered_issues if i.get('state') == 'OPEN')
    total_closed = sum(1 for i in filtered_issues if i.get('state') == 'CLOSED')
    report += f"| **Total** | **{total_open}** | **{total_closed}** | **{len(filtered_issues)}** |\n"

    # Detail sections by team
    for team in TEAM_LABELS:
        team_issues = by_team.get(team, [])
        by_assignee, unassigned = group_by_assignee(team_issues)

        report += f"\n---\n\n## {team}\n\n"
        report += f"**Total Issues:** {len(team_issues)}\n\n"

        if not team_issues:
            report += "*No issues with this label*\n"
            continue

        # Get all team members for this team
        team_members = TEAM_MEMBERS.get(team, [])

        # List all team members (even those with no open issues)
        for login in sorted(team_members, key=lambda x: get_assignee_name(x)):
            name = get_assignee_name(login)
            # Find issues for this user (case-insensitive match)
            assignee_issues = by_assignee.get(login, [])
            # Also check lowercase version
            if not assignee_issues:
                for key in by_assignee:
                    if key.lower() == login.lower():
                        assignee_issues = by_assignee[key]
                        break
            open_issues = [i for i in assignee_issues if i.get('state') == 'OPEN']
            count = len(open_issues)

            report += f"### {name} ({count} open)\n\n"

            if open_issues:
                for issue in sorted(open_issues, key=lambda x: x['number']):
                    title = issue['title']
                    num = issue['number']
                    milestone = issue.get('milestone')
                    milestone_str = f" [{milestone.get('title')}]" if milestone else ""
                    report += f"- #{num}: {title}{milestone_str}\n"
            else:
                report += "*No open issues assigned*\n"
            report += "\n"

        # Unassigned issues (open only)
        open_unassigned = [i for i in unassigned if i.get('state') == 'OPEN']
        if open_unassigned:
            report += f"### Unassigned ({len(open_unassigned)} open)\n\n"
            for issue in sorted(open_unassigned, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                milestone = issue.get('milestone')
                milestone_str = f" [{milestone.get('title')}]" if milestone else ""
                report += f"- #{num}: {title}{milestone_str}\n"
            report += "\n"

    # No team label section (open issues only)
    open_no_team = [i for i in no_team if i.get('state') == 'OPEN']
    if open_no_team:
        report += "\n---\n\n## Issues Without Team Label\n\n"
        report += f"**Open Issues:** {len(open_no_team)}\n\n"

        by_assignee, unassigned = group_by_assignee(open_no_team)

        for login in sorted(by_assignee.keys(), key=lambda x: get_assignee_name(x)):
            name = get_assignee_name(login)
            assignee_issues = by_assignee[login]

            if not assignee_issues:
                continue

            report += f"### {name} ({len(assignee_issues)} open)\n\n"

            for issue in sorted(assignee_issues, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                milestone = issue.get('milestone')
                milestone_str = f" [{milestone.get('title')}]" if milestone else ""
                report += f"- #{num}: {title}{milestone_str}\n"
            report += "\n"

        if unassigned:
            report += f"### Unassigned ({len(unassigned)} open)\n\n"
            for issue in sorted(unassigned, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                milestone = issue.get('milestone')
                milestone_str = f" [{milestone.get('title')}]" if milestone else ""
                report += f"- #{num}: {title}{milestone_str}\n"
            report += "\n"

    return report


def main():
    print("Fetching issues from GitHub...")
    issues = get_issues()
    print(f"  Found {len(issues)} total issues")

    # Count backlog issues
    backlog_count = sum(1 for i in issues if is_backlog_milestone(i.get('milestone')))
    print(f"  Excluding {backlog_count} backlog issues")

    print("Generating report...")
    report = generate_report(issues)

    import os
    reports_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(reports_dir, 'issue_report.md')

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"  Created: issue_report.md")
    print("\nDone!")


if __name__ == '__main__':
    main()
