#!/usr/bin/env python3
"""Generate issue report grouped by team labels and assignees."""

import json
import subprocess
from collections import defaultdict
from datetime import datetime

# Target milestones (all sprints, excluding backlogs)
TARGET_MILESTONES = ['W26-Sprint-1', 'W26-Sprint-2', 'W26-Sprint-3']

# Target issues per person
TARGET_PER_PERSON = 10

# GitHub repo URL for issue links
REPO_URL = 'https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh'

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


def is_target_milestone(milestone):
    """Check if milestone matches target milestones (excludes backlogs)."""
    if not milestone:
        return False
    title = milestone.get('title', '')
    # Exclude backlogs
    if 'backlog' in title.lower():
        return False
    return title in TARGET_MILESTONES


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
    # Filter to only include target milestone issues
    filtered_issues = []
    for issue in issues:
        if is_target_milestone(issue.get('milestone')):
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
    milestones_str = ', '.join(TARGET_MILESTONES)
    report = f"""# Issue Report: All Sprints

**Repository:** edge-anomaly-mesh
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Milestones:** {milestones_str}
**Target per Person:** {TARGET_PER_PERSON} issues
**Total Issues:** {len(filtered_issues)}

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
    open_no_team_count = sum(1 for i in no_team if i.get('state') == 'OPEN')
    closed_no_team_count = sum(1 for i in no_team if i.get('state') == 'CLOSED')
    report += f"| (No Team Label) | {open_no_team_count} | {closed_no_team_count} | {len(no_team)} |\n"

    # Totals
    total_open = sum(1 for i in filtered_issues if i.get('state') == 'OPEN')
    total_closed = sum(1 for i in filtered_issues if i.get('state') == 'CLOSED')
    report += f"| **Total** | **{total_open}** | **{total_closed}** | **{len(filtered_issues)}** |\n"

    # Detail sections by team
    for team in TEAM_LABELS:
        team_issues = by_team.get(team, [])
        by_assignee, unassigned = group_by_assignee(team_issues)

        # Get all team members for this team
        team_members = TEAM_MEMBERS.get(team, [])
        team_goal = len(team_members) * TARGET_PER_PERSON
        team_total = len(team_issues)

        report += f"\n---\n\n## {team} ({team_total}/{team_goal})\n\n"

        # List all team members
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
            closed_issues = [i for i in assignee_issues if i.get('state') == 'CLOSED']
            total = len(assignee_issues)

            # Count shared issues (issues with multiple assignees)
            shared_count = sum(1 for i in assignee_issues if len(i.get('assignees', [])) > 1)
            individual_count = total - shared_count

            if shared_count > 0:
                count_str = f"({individual_count} individual, {shared_count} shared)"
            else:
                count_str = f"({total})"

            report += f"### {name} {count_str}\n\n"

            if not assignee_issues:
                report += "*No issues assigned*\n"
            else:
                # List open issues first, then closed with strikethrough
                for issue in sorted(open_issues, key=lambda x: x['number']):
                    title = issue['title']
                    num = issue['number']
                    report += f"- [#{num}]({REPO_URL}/issues/{num}): {title}\n"
                for issue in sorted(closed_issues, key=lambda x: x['number']):
                    title = issue['title']
                    num = issue['number']
                    report += f"- ~~[#{num}]({REPO_URL}/issues/{num}): {title}~~\n"
            report += "\n"

        # Unassigned issues
        if unassigned:
            open_unassigned = [i for i in unassigned if i.get('state') == 'OPEN']
            closed_unassigned = [i for i in unassigned if i.get('state') == 'CLOSED']
            report += f"### Unassigned ({len(unassigned)})\n\n"
            for issue in sorted(open_unassigned, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                report += f"- [#{num}]({REPO_URL}/issues/{num}): {title}\n"
            for issue in sorted(closed_unassigned, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                report += f"- ~~[#{num}]({REPO_URL}/issues/{num}): {title}~~\n"
            report += "\n"

    # No team label section
    if no_team:
        report += "\n---\n\n## Issues Without Team Label\n\n"

        by_assignee, unassigned = group_by_assignee(no_team)

        for login in sorted(by_assignee.keys(), key=lambda x: get_assignee_name(x)):
            name = get_assignee_name(login)
            assignee_issues = by_assignee[login]

            if not assignee_issues:
                continue

            open_issues = [i for i in assignee_issues if i.get('state') == 'OPEN']
            closed_issues = [i for i in assignee_issues if i.get('state') == 'CLOSED']

            report += f"### {name} ({len(assignee_issues)})\n\n"

            for issue in sorted(open_issues, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                report += f"- [#{num}]({REPO_URL}/issues/{num}): {title}\n"
            for issue in sorted(closed_issues, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                report += f"- ~~[#{num}]({REPO_URL}/issues/{num}): {title}~~\n"
            report += "\n"

        if unassigned:
            open_unassigned = [i for i in unassigned if i.get('state') == 'OPEN']
            closed_unassigned = [i for i in unassigned if i.get('state') == 'CLOSED']
            report += f"### Unassigned ({len(unassigned)})\n\n"
            for issue in sorted(open_unassigned, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                report += f"- [#{num}]({REPO_URL}/issues/{num}): {title}\n"
            for issue in sorted(closed_unassigned, key=lambda x: x['number']):
                title = issue['title']
                num = issue['number']
                report += f"- ~~[#{num}]({REPO_URL}/issues/{num}): {title}~~\n"
            report += "\n"

    return report


def main():
    print("Fetching issues from GitHub...")
    issues = get_issues()
    print(f"  Found {len(issues)} total issues")

    # Count target milestone issues
    target_count = sum(1 for i in issues if is_target_milestone(i.get('milestone')))
    print(f"  Found {target_count} issues across {len(TARGET_MILESTONES)} milestones (excluding backlogs)")

    print("Generating report...")
    report = generate_report(issues)

    import os
    reports_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(reports_dir, 'ISSUE_REPORT.md')

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"  Created: ISSUE_REPORT.md")
    print("\nDone!")


if __name__ == '__main__':
    main()
