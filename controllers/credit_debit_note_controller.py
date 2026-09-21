from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from model.credit_debit_note import CreditDebitNote
from model.Log import LogHelper

cdn_bp = Blueprint('cdn_bp', __name__)
cdn_service = CreditDebitNote()


def _parse_form(form):
    def f(key, default=0):
        v = form.get(key, '') or str(default)
        try:
            return float(v)
        except (ValueError, TypeError):
            return float(default)

    return {
        'Note_Type':          (form.get('Note_Type') or '').strip(),
        'PMC_No':             (form.get('PMC_No') or '').strip(),
        'Invoice_No':         (form.get('Invoice_No') or '').strip(),
        'Basic_Amount':       f('Basic_Amount'),
        'Debit_Amount':       f('Debit_Amount'),
        'After_Debit_Amount': f('After_Debit_Amount'),
        'GST_Amount':         f('GST_Amount'),
        'Final_Amount':       f('Final_Amount'),
        'Payment_Amount':     f('Payment_Amount'),
        'Total_Amount':       f('Total_Amount'),
        'UTR':                (form.get('UTR') or '').strip(),
        'Contractor_Id':      int(form.get('Contractor_ID') or 0),
    }


# ── Main page (Add + List) ─────────────────────────────────────────────
@cdn_bp.route('/credit_debit_note', methods=['GET', 'POST'])
@login_required
def credit_debit_note():
    if request.method == 'POST':
        data = _parse_form(request.form)
        cdn_service.add(data)
        LogHelper.log_action("Add Credit/Debit Note", "User added a credit/debit note")
        return jsonify({"success": cdn_service.isSuccess, "message": cdn_service.resultMessage})

    notes = cdn_service.get_all()
    return render_template('add_credit_debit_note.html', notes=notes)


# ── Edit ───────────────────────────────────────────────────────────────
@cdn_bp.route('/edit_credit_debit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_credit_debit_note(note_id):
    note = cdn_service.get_by_id(note_id)
    if not note:
        return "Credit/Debit Note not found", 404

    if request.method == 'POST':
        data = _parse_form(request.form)
        cdn_service.update(note_id, data)
        LogHelper.log_action("Edit Credit/Debit Note", "User edited a credit/debit note")
        flash(cdn_service.resultMessage, 'success' if cdn_service.isSuccess else 'error')
        return redirect(url_for('cdn_bp.credit_debit_note'))

    return render_template('edit_credit_debit_note.html', note=note)


# ── Delete ─────────────────────────────────────────────────────────────
@cdn_bp.route('/delete_credit_debit_note/<int:note_id>', methods=['POST'])
@login_required
def delete_credit_debit_note(note_id):
    cdn_service.delete(note_id)
    LogHelper.log_action("Delete Credit/Debit Note", "User deleted a credit/debit note")
    return jsonify({"success": cdn_service.isSuccess, "message": cdn_service.resultMessage})
