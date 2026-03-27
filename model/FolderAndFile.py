import os
from flask import current_app


class FolderAndFile:

    # -----------------------------
    # BASE FOLDER METHODS
    # -----------------------------
    @staticmethod
    def get_download_folder():
        folder = os.path.join(current_app.root_path, "static", "downloads")

        if not os.path.exists(folder):
            os.makedirs(folder)

        os.makedirs(folder, exist_ok=True)
        return folder

    @staticmethod
    def get_upload_folder():
        folder = os.path.join(current_app.root_path, "static", "uploads")

        if not os.path.exists(folder):
            os.makedirs(folder)

        os.makedirs(folder, exist_ok=True)
        return folder

    @staticmethod
    def get_logs_folder():
        folder = os.path.join(current_app.root_path, "logs")

        if not os.path.exists(folder):
            os.makedirs(folder)

        os.makedirs(folder, exist_ok=True)
        return folder
    
    # FILE PATH METHODS - download
    @staticmethod
    def get_download_path(filename):
        return os.path.join(FolderAndFile.get_download_folder(), filename)
    
    # FILE PATH METHODS - upload file
    @staticmethod
    def get_upload_path(filename):
        return os.path.join(FolderAndFile.get_upload_folder(), filename)
    
    # FILE PATH METHODS - activity log file
    @staticmethod
    def get_activity_log_path(filename):
        return os.path.join(FolderAndFile.get_logs_folder(), filename)