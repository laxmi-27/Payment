from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from model.Subcontractor import Subcontractor
from model.Utilities import HtmlHelper, ResponseHandler


subcontractor_bp = Blueprint('subcontractor', __name__)


# ----------------------------------------------------------
# LIST + ADD
# ----------------------------------------------------------
@subcontractor_bp.route('/subcontractor', methods=['GET', 'POST'])
@login_required
def subcontract():

    sub = Subcontractor()
    # ---------------- GET ----------------
    if request.method == 'GET':
        subcontractor = sub.GetAllSubcontractors(request)

        if not sub.isSuccess:
            return HtmlHelper.json_response(
                ResponseHandler.fetch_failure("Subcontractor"), 500
            )

        return render_template('add_subcontractor.html', subcontractor=subcontractor)

    # ---------------- POST (ADD) ----------------
    if request.method == 'POST':

        sub.AddSubcontractor(request)

        if not sub.isSuccess:
            return HtmlHelper.json_response(
                ResponseHandler.add_failure("Subcontractor"), 500
            )

        # Reload list after insert
        subcontractor = sub.GetAllSubcontractors(request)

        return render_template('add_subcontractor.html', subcontractor=subcontractor)


# ----------------------------------------------------------
# EDIT
# ----------------------------------------------------------
@subcontractor_bp.route('/edit_subcontractor/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subcontractor(id):

    sub = Subcontractor()

    # Fetch data
    subcontractor = sub.GetSubcontractorByID(id)

    if not subcontractor:
        return HtmlHelper.json_response(
            ResponseHandler.fetch_failure("Subcontractor"), 404
        )

    # ---------------- POST (UPDATE) ----------------
    if request.method == 'POST':

        sub.EditSubcontractor(request, id)

        if not sub.isSuccess:
            return HtmlHelper.json_response(
                ResponseHandler.update_failure("Subcontractor"), 500
            )

        return redirect(url_for('subcontractor.subcontract'))

    return render_template('edit_subcontractor.html', subcontractor=subcontractor)


# ----------------------------------------------------------
# DELETE
# ----------------------------------------------------------
@subcontractor_bp.route('/deleteSubContractor/<int:id>', methods=['GET', 'POST'])
@login_required
def deleteSubContractor(id):

    sub = Subcontractor()

    sub.DeleteSubcontractor(request, id)

    if not sub.isSuccess:
        return HtmlHelper.json_response(
            ResponseHandler.delete_failure("Subcontractor"), 500
        )

    return redirect(url_for('subcontractor.subcontract'))