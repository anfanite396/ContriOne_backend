from .github import update_user as update_github
from .gitlab import update_user as update_gitlab
from ..models.users import User, UserPlatform
from apscheduler.schedulers.background import BackgroundScheduler

def update_user(user_id):
    platforms = UserPlatform.query.filter_by(user_id=user_id).all()
    for platform in platforms:
        if platform.platform == "github":
            update_github(platform.username)
        elif platform.platform == "gitlab":
            update_gitlab(platform.username)
        elif platform.platform == "gerrit":
            pass
        else:
            return "Platform not found"
        
def update_data():
    users = User.query.all()

    for user in users:
        update_user(user.id)

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", hours=24)