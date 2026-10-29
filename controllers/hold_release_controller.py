from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from model.hold_release import HoldRelease
from model.Log import LogHelper
import config

hr_bp      = Blueprint('hr_bp', __name__)
hr_service = HoldRelease()


def _parse_hold_col(value):
    """hold_col = 't:<hold_type_id>' (custom hold type) | 'f:<SD_Amount|Hydro_Testing>' | ''"""
    value = (value or '').strip()
    if value.startswith('t:') and value[2:].isdigit():
        return {'hold_type_id': int(value[2:]), 'fixed_hold': None}
    if value.startswith('f:') and value[2:] in ('SD_Amount', 'Hydro_Testing'):
        return {'hold_type_id': None, 'fixed_hold': value[2:]}
    return {'hold_type_id': None, 'fixed_hold': None}


def _parse_form(form):
    def amt(key):
        try:
            return float(form.get(key) or 0)
        except (ValueError, TypeError):
            return 0.0

    return {
        'PMC_No':          (form.get('PMC_No') or '').strip(),
        'invoice_no':      (form.get('invoice_no') or '').strip(),
        'Invoice_Details': (form.get('Invoice_Details') or '').strip(),
        'Basic_Amount':    amt('Basic_Amount'),
        'Final_Amount':    amt('Final_Amount'),
        'Total_Amount':    amt('Total_Amount'),
        'UTR':             (form.get('UTR') or '').strip(),
        'Contractor_Id':   int(form.get('Contractor_ID') or 0),
        **_parse_hold_col(form.get('hold_col')),
    }


# ── Get PMC Nos by Subcontractor (used by credit_note.html autocomplete) ──
@hr_bp.route('/get_pmc_nos_by_subcontractor_hr/<int:subcontractorId>')
@login_required
def get_pmc_nos_by_subcontractor(subcontractorId):
    conn = None
    try:
        conn = config.get_db_connection()
        cursor = conn.cursor()
        cursor.callproc('GetDistinctPMCNoByContractorId', [subcontractorId])
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify({'pmc_nos': [row[0] for row in results]})
    except Exception as e:
        print("ERROR in get_pmc_nos_by_subcontractor:", e)
        return jsonify({'pmc_nos': []})
    finally:
        if conn:
            try:
                cursor.close()
                conn.close()
            except Exception:
                pass


# ── Main page ──────────────────────────────────────────────────────────
@hr_bp.route('/hold_release', methods=['GET', 'POST'])
@login_required
def hold_release():
    if request.method == 'POST':
        data = _parse_form(request.form)
        if not (data['hold_type_id'] or data['fixed_hold']):
            return jsonify({"success": False,
                            "message": "Please select the hold column this release belongs to."})
        hr_service.add(data)
        LogHelper.log_action("Add Hold Release", "User added a hold release record")
        return jsonify({"success": hr_service.isSuccess, "message": hr_service.resultMessage})

    records = hr_service.get_all()
    return render_template('add_hold_release.html', records=records,
                           hold_types=hr_service.get_hold_types())


# ── Edit ───────────────────────────────────────────────────────────────
@hr_bp.route('/edit_hold_release/<int:hr_id>', methods=['GET', 'POST'])
@login_required
def edit_hold_release(hr_id):
    record = hr_service.get_by_id(hr_id)
    if not record:
        return "Hold Release not found", 404

    if request.method == 'POST':
        data = _parse_form(request.form)
        if not (data['hold_type_id'] or data['fixed_hold']):
            flash('Please select the hold column this release belongs to.', 'error')
            return redirect(url_for('hr_bp.edit_hold_release', hr_id=hr_id))
        hr_service.update(hr_id, data)
        LogHelper.log_action("Edit Hold Release", "User edited a hold release record")
        flash(hr_service.resultMessage, 'success' if hr_service.isSuccess else 'error')
        return redirect(url_for('hr_bp.hold_release'))

    return render_template('edit_hold_release.html', record=record,
                           hold_types=hr_service.get_hold_types())


# ── Delete ─────────────────────────────────────────────────────────────
@hr_bp.route('/delete_hold_release/<int:hr_id>', methods=['POST'])
@login_required
def delete_hold_release(hr_id):
    hr_service.delete(hr_id)
    LogHelper.log_action("Delete Hold Release", "User deleted a hold release record")
    return jsonify({"success": hr_service.isSuccess, "message": hr_service.resultMessage})