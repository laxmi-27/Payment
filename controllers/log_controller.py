from flask import Blueprint, render_template, request
from flask_login import login_required

from model.Log import LogData

log_bp = Blueprint('log', __name__)


@log_bp.route('/activity_log', methods=['GET', 'POST'])
@login_required
def activity_log():

    start_date = request.values.get("start_date")
    end_date = request.values.get("end_date")
    user_name = request.values.get("username")

    logData = LogData()

    filtered_logs = logData.GetFilteredActivitiesLog(
        start_date,
        end_date,
        user_name
    )
    return render_template(
        "activity_log.html",
        logs=filtered_logs,
        start_date=start_date,
        end_date=end_date,
        username=user_name
    )