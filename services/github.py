from datetime import datetime
from ..models.methods import add_event, add_repo
from .requests import fetch_github

def update_repos(username):
    repos = fetch_github(username, "repos")
    for repo in repos:
        add_repo(username, "github", "GH" + str(repo['id']), repo['name'], repo['html_url'])

def update_events(username):
    events = fetch_github(username, "events")
    for event in events:
        add_repo(username, "github", "GH" + str(event['repo']['id']), event['repo']['name'], event['repo']['url'])

        # Parse the ISO 8601 datetime string and remove the timezone info
        created_at_dt = datetime.fromisoformat(event['created_at'][:-1])
        created_at_mysql = created_at_dt.strftime('%Y-%m-%d %H:%M:%S')
        add_event("GH" + str(event['repo']['id']), "GH" + str(event['id']), event['type'], created_at_mysql)

def update_user(username):
    update_repos(username)
    update_events(username)