import requests

def fetch_github(username, query=None):
    if query:
        url = f"https://api.github.com/users/{username}/{query}"
    else:
        url = f"https://api.github.com/users/{username}"
    
    response = requests.get(url)
    if (response.status_code == 200):
        return response.json()
    else:
        return None
    
def fetch_gitlab(username, query=None):
    if query:
        url = f"https://gitlab.com/api/v4/users/{username}/{query}"
    else:
        url = f"https://gitlab.com/api/v4/users?username={username}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for non-2XX responses
        data = response.json()
        if data:
            if query:
                return data
            else:
                return data[0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitLab user data: {e}")
        return None
