# import os
# from flask import current_app
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# from datetime import datetime

# from model.FolderAndFile import FolderAndFile

# class LogHelper:
#     @staticmethod
#     def log_action(action, details=""):
#         """Log user actions with timestamp, user, action, and details."""
#         logData = LogData()
#         logData.WriteLog(action, details="")

# class LogData:
#     filepath = ""
#     timestamp = None

#     def __init__(self):
#         self.filepath = FolderAndFile.get_activity_log_path('activity.log')
#         self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         self.user = LogData.get_current_user()


#     @staticmethod
#     def get_current_user():
#         if hasattr(current_user, "cn") and current_user.cn:
#             return current_user.cn
#         elif hasattr(current_user, "username") and current_user.username:
#             return current_user.username
#         elif hasattr(current_user, "sAMAccountName") and current_user.sAMAccountName:
#             return current_user.sAMAccountName
#         return "Unknown"

#     def WriteLog(self, action, details=""):
#         """Log user actions with timestamp, user, action, and details."""
        
#         with open(self.filepath, "a", encoding="utf-8") as f:
#             f.write(
#                 f"Timestamp: {self.timestamp} | "
#                 f"User: {self.user} | "
#                 f"Action: {action} | "
#                 f"Details: {details}\n"
#             )

#     def GetActivitiesLog(self):
#         logs = []

#         if os.path.exists(self.filepath):
#             with open(self.filepath, 'r') as f:
#                 for line in f:
#                     parts = line.strip().split(" | ")
#                     if len(parts) == 4:
#                         logs.append({
#                             "timestamp": parts[0].replace("Timestamp:", "").strip(),
#                             "user": parts[1].replace("User:", "").strip(),
#                             "action": parts[2].replace("Action:", "").strip(),
#                             "details": parts[3].replace("Details:", "").strip()
#                         })
#         return logs

#     def GetFilteredActivitiesLog(self, startDate, endDate, userName):
#         filtered_logs = self.GetActivitiesLog()

#         # Date filter
#         if startDate or endDate:
#             try:
#                 start_dt = datetime.strptime(startDate, "%Y-%m-%d") if startDate else datetime.min
#                 end_dt = datetime.strptime(endDate, "%Y-%m-%d") if endDate else datetime.max

#                 filtered_logs = [
#                     log for log in filtered_logs
#                     if start_dt <= datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S") <= end_dt
#                 ]

#             except Exception as e:
#                 print("Date filter error:", e)
            
#         # Username filter
#         if userName:
#             filtered_logs = [log for log in filtered_logs if userName.lower() in log["user"].lower()]

#         return filtered_logs

import os
from datetime import datetime, timedelta

from flask import current_app, session
from flask_login import current_user

from model.FolderAndFile import FolderAndFile


class LogHelper:
    @staticmethod
    def log_action(action, details="", username=None):
        """
        Log user actions with timestamp, user, action, and details.
        """
        logData = LogData(username=username)
        logData.WriteLog(action, details)


class LogData:
    filepath = ""
    timestamp = None

    def __init__(self, username=None):
        self.filepath = FolderAndFile.get_activity_log_path("activity.log")
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Use explicitly passed username if available
        if username:
            self.user = str(username)
        else:
            self.user = LogData.get_current_user()

    @staticmethod
    def get_current_user():
        """
        Get currently logged-in user from Flask-Login or Session.
        """
        try:

            # Flask-Login User
            if current_user and not current_user.is_anonymous:

                if hasattr(current_user, "cn") and current_user.cn:
                    return str(current_user.cn)

                if hasattr(current_user, "username") and current_user.username:
                    return str(current_user.username)

                if hasattr(current_user, "sAMAccountName") and current_user.sAMAccountName:
                    return str(current_user.sAMAccountName)

                if hasattr(current_user, "id") and current_user.id:
                    return str(current_user.id)

            # Session Values
            if session.get("uname"):
                return str(session.get("uname"))

            if session.get("username"):
                return str(session.get("username"))

            if session.get("user"):
                return str(session.get("user"))

            if session.get("_user_id"):
                return str(session.get("_user_id"))

        except Exception as e:
            print("User fetch error:", str(e))

        return "Unknown"

    def WriteLog(self, action, details=""):
        """
        Write activity log entry.
        """

        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(
                    f"Timestamp: {self.timestamp} | "
                    f"User: {self.user} | "
                    f"Action: {action} | "
                    f"Details: {details}\n"
                )

        except Exception as e:
            print("Log write error:", str(e))

    def GetActivitiesLog(self):
        """
        Read all activity logs.
        """

        logs = []

        if not os.path.exists(self.filepath):
            return logs

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:

                    parts = line.strip().split(" | ")

                    if len(parts) == 4:
                        logs.append(
                            {
                                "timestamp": parts[0].replace("Timestamp:", "").strip(),
                                "user": parts[1].replace("User:", "").strip(),
                                "action": parts[2].replace("Action:", "").strip(),
                                "details": parts[3].replace("Details:", "").strip(),
                            }
                        )

        except Exception as e:
            print("Log read error:", str(e))

        return logs

    def GetFilteredActivitiesLog(
        self,
        startDate=None,
        endDate=None,
        userName=None,
        action=None,
    ):
        """
        Filter logs by date, username and action.
        """

        filtered_logs = self.GetActivitiesLog()

        # Date Filter
        if startDate or endDate:
            try:

                start_dt = (
                    datetime.strptime(startDate, "%Y-%m-%d")
                    if startDate
                    else datetime.min
                )

                end_dt = (
                    datetime.strptime(endDate, "%Y-%m-%d") + timedelta(days=1)
                    if endDate
                    else datetime.max
                )

                filtered_logs = [
                    log
                    for log in filtered_logs
                    if start_dt
                    <= datetime.strptime(
                        log["timestamp"],
                        "%Y-%m-%d %H:%M:%S",
                    )
                    < end_dt
                ]

            except Exception as e:
                print("Date filter error:", str(e))

        # Username Filter
        if userName:
            filtered_logs = [
                log
                for log in filtered_logs
                if userName.lower() in log["user"].lower()
            ]

        # Action Filter
        if action and action.strip():
            filtered_logs = [
                log
                for log in filtered_logs
                if log["action"].lower() == action.lower()
            ]

        return filtered_logs