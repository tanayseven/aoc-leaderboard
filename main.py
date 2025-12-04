import sys
from datetime import datetime
from pathlib import Path

import httpx

from tabulate import tabulate


def fetch_leaderboard(url: str, session_cookie: str = None) -> dict:
    headers = {}
    if session_cookie:
        headers['Cookie'] = f'session={session_cookie}'

    with httpx.Client() as client:
        response = client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        return response.json()


def format_completion_days(completion_day_level: dict) -> str:
    if not completion_day_level:
        return "No days yet"

    days = sorted(completion_day_level.keys(), key=int)
    day_data = []

    for day in days:
        stars_for_day = len(completion_day_level[day])
        star_display = '*' * stars_for_day
        day_data.append([f"Day {day}", star_display])

    # Create a simple sub-table
    sub_table = tabulate(day_data, headers=['Day', 'Stars'], tablefmt='simple')
    return sub_table


def display_leaderboard(data: dict, team_name: str):
    """Display the leaderboard data as a formatted table."""
    event = data['event']
    members = data['members']
    today = datetime.today().strftime("%d %B %Y")
    padding = 4

    message = f"{' ' * padding}Advent of Code {event} - {team_name} Leaderboard - {today}{' ' * padding}"

    print(f"\n{'=' * len(message)}")
    print(message)
    print(f"{'=' * len(message)}\n")

    # Prepare table data
    table_data = []
    for member_id, member_info in members.items():
        last_star_unix_ts = member_info['last_star_ts']
        last_star_ts = datetime.fromtimestamp(last_star_unix_ts)
        last_star_time_format = "%Y-%m-%d %H:%M:%S"
        if last_star_unix_ts == 0:
            last_star_earned = "No stars earned yet"
        else:
            last_star_earned = last_star_ts.strftime(last_star_time_format)
        table_data.append([
            '-',
            member_info['name'],
            format_completion_days(member_info['completion_day_level']),
            member_info['stars'],
            member_info['local_score'],
            last_star_earned,
        ])

    # Sort by local_score (descending), then by stars (descending)
    table_data.sort(key=lambda x: (x[4], x[3]), reverse=True)
    no = 1
    for row in table_data:
        if row[5] != "No stars earned yet":
            row[0] = no
            no += 1

    # Display table
    headers = ['#', 'Name', 'Completion Day Level', 'Stars', 'Local Score', 'Last Star Earned']
    print(tabulate(table_data, headers=headers, tablefmt='fancy_grid'))
    print()


def main():
    team_name_file = Path.cwd() / "aoc-team-name.txt"
    if not team_name_file.exists() or team_name_file.read_text().strip() == "":
        print("\nWarning: No team name file provided.")
        team_name = input("Enter your Advent of Code team name: ").strip()
        team_name_file.write_text(team_name)
    else:
        team_name = team_name_file.read_text()

    leaderboard_file = Path.cwd() / "aoc-leaderboard.txt"
    if not leaderboard_file.exists() or leaderboard_file.read_text().strip() == "":
        print("\nWarning: No leaderboard id provided")
        leaderboard_id = input("Enter the leaderboard id: ").strip().split("-")[0]
        leaderboard_file.write_text(leaderboard_id)
    else:
        leaderboard_id = leaderboard_file.read_text()

    url = f"https://adventofcode.com/2025/leaderboard/private/view/{leaderboard_id}.json"

    # Note: You'll need to provide your session cookie for authentication
    # You can find this in your browser's developer tools after logging into AoC
    cookie_file = Path.cwd() / "aoc-cookie.txt"
    if not cookie_file.exists() or cookie_file.read_text().strip() == "":
        print("\nWarning: No session cookie provided. The request may fail if authentication is required.")
        print("\tTo get your session cookie:")
        print("\t1. Log into adventofcode.com")
        print("\t2. Open browser developer tools (F12)")
        print("\t3. Go to Application/Storage > Cookies")
        print("\t4. Copy the value of the 'session' cookie\n")
        session_cookie = input("Enter your Advent of Code session cookie (or press Enter to skip): ").strip()
        cookie_file.write_text(session_cookie)
    else:
        session_cookie = cookie_file.read_text()
    if session_cookie.strip() == "":
        print("\nWarning: No session cookie provided.")
        sys.exit(1)

    try:
        data = fetch_leaderboard(url, session_cookie if session_cookie else None)
        display_leaderboard(data, team_name)
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.reason_phrase}")
        if e.response.status_code == 401 or e.response.status_code == 400:
            print("Authentication required. Please provide a valid session cookie.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()