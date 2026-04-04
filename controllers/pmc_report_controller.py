from flask import Blueprint, render_template, send_from_directory,send_file
from flask_login import login_required
# from model.PmcReport import PmcReport
from model.UnifiedReportService import UnifiedReportService
pmc_report_bp = Blueprint("pmc_report", __name__)

# ---------------- Contractor Report by pmc no ----------------

@pmc_report_bp.route("/pmc_report/<pmc_no>")
@login_required
def pmc_report(pmc_no):
    data = UnifiedReportService.get_report(pmc_no=pmc_no)
    if not data:
        return "No PMC found with this number", 404

    return render_template(
        "pmc_report.html",
        info=data["info"],
        invoices=data["invoices"],
        hold_types=data["hold_types"],
        hold_data=data["hold_data"],          # <-- add this line
        gst_rel=data["gst_rel"],
        payments=data["payments"],
        credit_note=data["credit_note"],
        hold_release=data["hold_release"],
        total=data["total"]
    )
# ---------------- Contractor Download Report by pmc no ----------------

@pmc_report_bp.route("/download_pmc_report/<pmc_no>")
@login_required
def download_pmc_report(pmc_no):

    output_file = UnifiedReportService.download(pmc_no=pmc_no)

    if not output_file:
        return "No contractor found for this PMC No", 404

    return send_file(output_file, as_attachment=True)