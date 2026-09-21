from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from model.credit import creditmodel
from model.Log import LogHelper

credit_bp = Blueprint('credit_bp', __name__)

# ---------------- ADD ----------------
@credit_bp.route('/add_credit_note', methods=['GET', 'POST'])
@login_required
def add_credit_note():

    notes_dict = creditmodel.fetch_all_credit_notes()

    notes = [
        [
            n['Credit_Note_Id'],
            n.get('Contractor_Name') or '—',
            n['PMC_No'],
            n['invoice_no'],
            n['Invoice_Details'],
            n['Basic_Amount'],
            n['Debit_Amount'],
            n['After_Debit_Amount'],
            n['GST_Amount'],
            n['Final_Amount'],
            n['Payment_Amount'],
            n['Total_Amount'],
            n['UTR']
        ]
        for n in notes_dict
    ]

    if request.method == 'POST':
        form = request.form

        creditmodel.insert_credit_note(
            form['subcontractor_id'],
            form['PMC_No'],
            form['note_type'],
            form['invoice_No'],
            form['basic_amount'],
            form['debit_amount'],
            form['after_debit_amount'],
            form['gst_amount'],
            form['final_amount'],
            form['Payment_Amount'],
            form['Total_Amount'],
            form['UTR']
        )

        return redirect(url_for('credit_bp.add_credit_note'))

    return render_template('credit_note.html', notes=notes)


# ---------------- EDIT ----------------
@credit_bp.route('/edit_credit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_credit(id):

    data = creditmodel.fetch_credit_by_id(id)

    if request.method == 'POST':
        form = request.form

        creditmodel.update_credit(
            id,
            form['PMC_No'],
            form['note_type'],
            form['invoice_No'],
            form['basic_amount'],
            form['debit_amount'],
            form['after_debit_amount'],
            form['gst_amount'],
            form['final_amount'],
            form['Payment_Amount'],
            form['Total_Amount'],
            form['UTR']
        )

        return redirect(url_for('credit_bp.add_credit_note'))

    return render_template('edit_credit.html', data=data)


# ---------------- DELETE ----------------
@credit_bp.route('/delete_credit/<int:id>')
@login_required
def delete_credit(id):

    creditmodel.delete_credit(id)

    return redirect(url_for('credit_bp.add_credit_note'))
