from .github import update_user as update_github
from .gitlab import update_user as update_gitlab
from ..models.users import User, UserPlatform
from apscheduler.schedulers.background import BackgroundScheduler

def update_user(user_id):
    platform_fetcher = {
            "github": update_github,
            "gitlab": update_gitlab,
        }
    
    platforms = UserPlatform.query.filter_by(user_id=user_id).all()
    for platform in platforms:
        try:
            update_function = platform_fetcher.get(platform.platform)
            if not update_function:
                return "Platform not found"
            
            update_function(platform.username)
        except Exception as e:
            return f"Error occurred while updating platforms: {e}"
        
def update_data():
    users = User.query.all()

    for user in users:
        update_user(user.id)

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", hours=24)