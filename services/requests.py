import requests
from flask import current_app

def fetch_github(username, query=None):
    if query:
        url = f"https://api.github.com/users/{username}/{query}"
    else:
        url = f"https://api.github.com/users/{username}"
    
    try:
        response = requests.get(url)
        if (response.status_code == 200):
            return response.json()
        else:
            return None
    except Exception as e:
        current_app.logger.error(f"Error fetching Github user data: {e}")
        return None
    
def fetch_gitlab(username, query=None):
    if query:
        url = f"https://gitlab.com/api/v4/users/{username}/{query}"
    else:
        url = f"https://gitlab.com/api/v4/users?username={username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            if query:
                return response.json()
            return response.json()[0]
        else:
            None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitLab user data: {e}")
        return None
