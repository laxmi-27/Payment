from flask import Blueprint, render_template, request, jsonify,send_file
from flask_login import login_required, current_user

from model.Report import ReportHelper
from model.Log import LogHelper
import os

# DOWNLOAD_FOLDER = "static/download"
report_bp = Blueprint("report", __name__)


# ---------------- Report Page ----------------
@report_bp.route("/report")
@login_required
def report_page():
    return render_template("/report.html")


# ---------------- Search Contractor ----------------
@report_bp.route("/search_contractor", methods=["POST"])
@login_required
def search_contractor():

    subcontractor_name = request.form.get("subcontractor_name")

    LogHelper.log_action(
        "Search Contractor",
        f"User {current_user.id} searched contractor '{subcontractor_name}'"
    )

    data = ReportHelper.search_contractor(request)

    return jsonify(data)

# ---------------- Contractor Report by contractor id ----------------
@report_bp.route('/contractor_report/<int:contractor_id>')
@login_required
def contractor_report(contractor_id):

    data = ReportHelper.get_contractor_report(contractor_id)

    return render_template(
        'subcontractor_report.html',
        contractor_id=contractor_id,
        **data
    )

# # ---------------- Contractor Download Report by contractor id ----------------

@report_bp.route('/download_report/<int:contractor_id>')
def download_report(contractor_id):
    output_file, error = ReportHelper.create_contractor_report(contractor_id)
    
    if error:
        return error, 404
      

    # Send the file to the user
    return send_file(output_file, as_attachment=True)