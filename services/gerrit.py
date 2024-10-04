import requests

from ..models.users import Repo, add_event, add_repo

def fetch_data(username, gerrit_server, query):
    url = f"https://gerrit.{gerrit_server}.org/changes/?q=owner:{username}"
    response = requests.get(url)
    if (response.status_code == 200):
        return response.json()
    else:
        return None
    
# def update_repos(username):
#     repos = fetch_data(username, "repos")
#     for repo in repos:
#         add_repo(username, "github", "GH" + repo['id'], repo['name'], repo['html_url'])

def update_events(username):
    events = fetch_data(username, "events")
    for event in events:
        add_event("GR" + str(event['repo']['id']), str("GR" + event['id']), event['type'], event['created'])

def update_user(username):
    update_events(username)