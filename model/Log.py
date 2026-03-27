import os
from flask import current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from datetime import datetime

from model.FolderAndFile import FolderAndFile

class LogHelper:
    @staticmethod
    def log_action(action, details=""):
        """Log user actions with timestamp, user, action, and details."""
        logData = LogData()
        logData.WriteLog(action, details="")

class LogData:
    filepath = ""
    timestamp = None

    def __init__(self):
        self.filepath = FolderAndFile.get_activity_log_path('activity.log')
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.user = LogData.get_current_user()


    @staticmethod
    def get_current_user():
        if hasattr(current_user, "cn") and current_user.cn:
            return current_user.cn
        elif hasattr(current_user, "username") and current_user.username:
            return current_user.username
        elif hasattr(current_user, "sAMAccountName") and current_user.sAMAccountName:
            return current_user.sAMAccountName
        return "Unknown"

    def WriteLog(self, action, details=""):
        """Log user actions with timestamp, user, action, and details."""
        
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(
                f"Timestamp: {self.timestamp} | "
                f"User: {self.user} | "
                f"Action: {action} | "
                f"Details: {details}\n"
            )

    def GetActivitiesLog(self):
        logs = []

        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                for line in f:
                    parts = line.strip().split(" | ")
                    if len(parts) == 4:
                        logs.append({
                            "timestamp": parts[0].replace("Timestamp:", "").strip(),
                            "user": parts[1].replace("User:", "").strip(),
                            "action": parts[2].replace("Action:", "").strip(),
                            "details": parts[3].replace("Details:", "").strip()
                        })
        return logs

    def GetFilteredActivitiesLog(self, startDate, endDate, userName):
        filtered_logs = self.GetActivitiesLog()

        # Date filter
        if startDate or endDate:
            try:
                start_dt = datetime.strptime(startDate, "%Y-%m-%d") if startDate else datetime.min
                end_dt = datetime.strptime(endDate, "%Y-%m-%d") if endDate else datetime.max

                filtered_logs = [
                    log for log in filtered_logs
                    if start_dt <= datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S") <= end_dt
                ]

            except Exception as e:
                print("Date filter error:", e)
            
        # Username filter
        if userName:
            filtered_logs = [log for log in filtered_logs if userName.lower() in log["user"].lower()]

        return filtered_logs