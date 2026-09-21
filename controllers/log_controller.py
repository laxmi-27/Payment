from flask import Blueprint, render_template, request
from flask_login import login_required

from model.Log import LogData

log_bp = Blueprint('log', __name__)


@log_bp.route('/activity_log', methods=['GET', 'POST'])
@login_required
def activity_log():

    start_date = request.values.get("start_date")
    end_date   = request.values.get("end_date")
    user_name  = request.values.get("username")
    action_filter = request.values.get("action_filter")

    logData = LogData()

    all_logs      = logData.GetActivitiesLog()
    filtered_logs = logData.GetFilteredActivitiesLog(start_date, end_date, user_name)

    # Apply action filter (client-side fallback handled in template, but also filter server-side)
    if action_filter:
        filtered_logs = [l for l in filtered_logs if l.get('action', '').strip() == action_filter.strip()]

    # Unique actions for dropdown
    unique_actions = sorted({l.get('action', '').strip() for l in all_logs if l.get('action')})

    return render_template(
        "activity_log.html",
        logs=filtered_logs,
        start_date=start_date,
        end_date=end_date,
        username=user_name,
        action_filter=action_filter,
        unique_actions=unique_actions,
    )
