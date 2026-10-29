import re as _re
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from model.Subcontractor import Subcontractor
from model.Utilities import HtmlHelper, ResponseHandler


subcontractor_bp = Blueprint('subcontractor', __name__)


def _validate_contractor(form):
    name     = form.get('Contractor_Name', '').strip()
    mobile   = form.get('Mobile_No', '').strip()
    pan      = form.get('PAN_No', '').strip().upper()
    email    = form.get('Email', '').strip()
    gst_type = form.get('GST_Registration_Type', '').strip()
    gst_no   = form.get('GST_No', '').strip().upper()

    if not name:
        return 'Contractor Name is required.'
    # Mobile No and PAN No are optional.
    # Validate format only when a value is provided.
    if mobile and not _re.fullmatch(r'[0-9]{10}', mobile):
        return 'Mobile No must be exactly 10 digits when provided.'
    if pan and not _re.fullmatch(r'[A-Z0-9]{10}', pan):
        return 'PAN No must be 10 uppercase letters/digits when provided.'
    if email and not _re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$', email):
        return 'Enter a valid email address.'
    if gst_type in ('Registered', 'Composition') and len(gst_no) != 15:
        return 'GST No must be exactly 15 characters when type is Registered or Composition.'
    return None


# ----------------------------------------------------------
# LIST + ADD
# ----------------------------------------------------------
@subcontractor_bp.route('/subcontractor', methods=['GET', 'POST'])
@login_required
def subcontract():

    sub = Subcontractor()

    # ---------------- GET ----------------
    if request.method == 'GET':
        subcontractors = sub.GetAllSubcontractors(request)
        if not sub.isSuccess:
            return HtmlHelper.json_response(
                ResponseHandler.fetch_failure("Subcontractor"), 500
            )
        return render_template('add_subcontractor.html', subcontractors=subcontractors)

    # ---------------- POST (ADD) ----------------
    err = _validate_contractor(request.form)
    if err:
        return jsonify({"success": False, "message": err}), 400

    dup_msg = sub.CheckDuplicates(request)
    if dup_msg:
        return jsonify({"success": False, "message": dup_msg}), 409

    sub.AddSubcontractor(request)
    if not sub.isSuccess:
        return jsonify({"success": False, "message": "Failed to add contractor. Please try again."}), 500

    return jsonify({"success": True, "message": "Contractor added successfully."})


# ----------------------------------------------------------
# EDIT
# ----------------------------------------------------------
@subcontractor_bp.route('/edit_subcontractor/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subcontractor(id):

    sub = Subcontractor()
    subcontractor = sub.GetSubcontractorByID(id)

    if not subcontractor:
        return HtmlHelper.json_response(
            ResponseHandler.fetch_failure("Subcontractor"), 404
        )

    # ---------------- POST (UPDATE) ----------------
    if request.method == 'POST':
        err = _validate_contractor(request.form)
        if err:
            return jsonify({"success": False, "message": err}), 400

        dup_msg = sub.CheckDuplicates(request, exclude_id=id)
        if dup_msg:
            return jsonify({"success": False, "message": dup_msg}), 409

        sub.EditSubcontractor(request, id)
        if not sub.isSuccess:
            return jsonify({"success": False, "message": "Failed to update contractor."}), 500

        return jsonify({"success": True})

    return render_template('edit_subcontractor.html', subcontractor=subcontractor)


# ----------------------------------------------------------
# DELETE
# ----------------------------------------------------------
@subcontractor_bp.route('/deleteSubContractor/<int:id>', methods=['POST'])
@login_required
def deleteSubContractor(id):

    sub = Subcontractor()

    if sub.CheckContractorLinked(id):
        return jsonify({
            "success": False,
            "linked": True,
            "message": "This contractor has active work assignments and cannot be deleted. Please deactivate instead."
        }), 409

    sub.DeleteSubcontractor(request, id)
    if not sub.isSuccess:
        return jsonify({"success": False, "message": "Failed to delete contractor."}), 500

    return jsonify({"success": True})


# ----------------------------------------------------------
# GET SINGLE CONTRACTOR (for View Details modal)
# ----------------------------------------------------------
@subcontractor_bp.route('/api/subcontractor/<int:id>', methods=['GET'])
@login_required
def api_get_subcontractor(id):
    sub  = Subcontractor()
    data = sub.GetSubcontractorByID(id)
    if not data:
        return jsonify({"success": False}), 404
    return jsonify({
        "success":  True,
        "id":       data[0],
        "name":     data[1]  or '',
        "address":  data[2]  or '',
        "mobile":   data[3]  or '',
        "pan":      data[4]  or '',
        "email":    data[5]  or '',
        "gender":   data[6]  or '',
        "gst_type": data[7]  or '',
        "gst_no":   data[8]  or '',
        "password": data[9]  or '',
        "status":   data[10] or 'Active',
        "created":  str(data[11]) if data[11] else ''
    })


# ----------------------------------------------------------
# STATUS CHANGE  (Activate / Deactivate)
# ----------------------------------------------------------
@subcontractor_bp.route('/api/subcontractor/status_change', methods=['POST'])
@login_required
def api_status_change():

    data = request.get_json()
    contractor_id = data.get('contractor_id') if data else None
    new_status    = data.get('status')        if data else None

    if not contractor_id or new_status not in ('Active', 'Inactive'):
        return jsonify({"success": False, "message": "Invalid parameters."}), 400

    sub = Subcontractor()
    sub.SetContractorStatus(contractor_id, new_status)
    if not sub.isSuccess:
        return jsonify({"success": False, "message": "Failed to update status."}), 500

    return jsonify({"success": True, "new_status": new_status})
