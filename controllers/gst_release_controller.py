from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from model.gst_release import GSTRelease
from model.Log import LogHelper

gst_release_bp = Blueprint('gst_release_bp', __name__)
gst_service = GSTRelease()


# ---------------- ADD GST RELEASE ----------------
@gst_release_bp.route('/add_gst_release', methods=['GET', 'POST'])
@login_required
def add_gst_release():
    if request.method == 'POST':
        utr = request.form.get('UTR', '').strip()
        if not utr:
            return jsonify({"success": False, "message": "UTR is required."}), 400
        gst_service.AddGSTRelease(request)
        LogHelper.log_action("Add GST Release", "User added GST release")
        return jsonify({"success": gst_service.isSuccess, "message": gst_service.resultMessage})

    gst_releases = gst_service.GetAllGSTReleasesWithNames()
    return render_template('add_gst_release.html', gst_releases=gst_releases)


# ---------------- API: GET SINGLE GST RELEASE ----------------
@gst_release_bp.route('/api/gst_release/<int:gst_release_id>', methods=['GET'])
@login_required
def api_get_gst_release(gst_release_id):
    data = gst_service.GetGSTReleaseByIDWithName(gst_release_id)
    if not data:
        return jsonify({"success": False}), 404

    def fstr(v):
        return str(v) if v is not None else '0.00'

    return jsonify({
        "success":   True,
        "id":        data.get('GST_Release_Id'),
        "contractor": data.get('Contractor_Name') or '',
        "pmc":       str(data.get('PMC_No') or ''),
        "invoice":   str(data.get('Invoice_No') or ''),
        "date":      str(data.get('Invoice_Date')) if data.get('Invoice_Date') else '',
        "basic":     fstr(data.get('Basic_Amount')),
        "final_amt": fstr(data.get('Final_Amount')),
        "total":     fstr(data.get('Total_Amount')),
        "utr":       data.get('UTR') or '',
    })


# ---------------- EDIT GST RELEASE ----------------
@gst_release_bp.route('/edit_gst_release/<int:gst_release_id>', methods=['GET', 'POST'])
@login_required
def edit_gst_release(gst_release_id):
    gst_data = gst_service.GetGSTReleaseByID(gst_release_id)
    if not gst_data:
        return "GST Release not found", 404

    if request.method == 'POST':
        utr = request.form.get('UTR', '').strip()
        if not utr:
            flash("UTR is required.", 'error')
            return redirect(url_for('gst_release_bp.edit_gst_release', gst_release_id=gst_release_id))
        gst_service.EditGSTRelease(request, gst_release_id)
        LogHelper.log_action("Edit GST Release", "User edited GST release")
        flash(gst_service.resultMessage, 'success' if gst_service.isSuccess else 'error')
        return redirect(url_for('gst_release_bp.add_gst_release'))

    return render_template('edit_gst_release.html', gst_release_data=gst_data)


# ---------------- DELETE GST RELEASE ----------------
@gst_release_bp.route('/delete_gst_release/<int:gst_release_id>', methods=['POST'])
@login_required
def delete_gst_release(gst_release_id):
    gst_service.DeleteGSTRelease(gst_release_id)
    LogHelper.log_action("Delete GST Release", "User deleted GST release")
    return jsonify({"success": gst_service.isSuccess, "message": gst_service.resultMessage})
