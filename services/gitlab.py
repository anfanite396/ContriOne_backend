from dateutil import parser
from ..models.users import add_event, add_repo
from .requests import fetch_gitlab

def update_repos(username):
    repos = fetch_gitlab(username, "projects")
    for repo in repos:
        add_repo(username, "gitlab", "GL" + str(repo['id']), repo['name'], repo['http_url_to_repo'])

def update_events(username):
    events = fetch_gitlab(username, "events")
    for event in events:
        # add_repo(username, "gitlab", "GL" + str(event['repo']['id']), event['repo']['name'], event['repo']['url'])

        created_at_dt = parser.isoparse(event['created_at'])
        created_at_mysql = created_at_dt.strftime('%Y-%m-%d %H:%M:%S')
        add_event("GL" + str(event['project_id']), "GL" + str(event['id']), event['action_name'], created_at_mysql)

def update_user(username):
    update_repos(username)
    update_events(username)