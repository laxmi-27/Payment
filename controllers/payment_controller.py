from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from model.payment import Paymentmodel
from model.Log import LogHelper

payment_bp = Blueprint('payment_bp', __name__)

# ------------------- Add Payment -------------------
@payment_bp.route('/add_payment', methods=['GET', 'POST'])
@login_required
def add_payment():
    payments_dicts = Paymentmodel.fetch_all_payments()
    # Convert to array for template
    payments = [
        [
            p['Payment_Id'], p['PMC_No'], p['Invoice_No'],
            p['Payment_Amount'], p['TDS_Payment_Amount'], p['Total_Amount'], p['UTR']
        ] for p in payments_dicts
    ] if payments_dicts else []

    if request.method == 'POST':
        subcontractor_id = request.form.get('subcontractor_id')
        pmc_no = request.form['PMC_No']
        invoice_no = request.form['invoice_No']
        amount = request.form['Payment_Amount']
        tds_amount = request.form['TDS_Payment_Amount']
        total_amount = request.form['total_amount']
        utr = request.form['utr']

        LogHelper.log_action("Add Payment", f"User {current_user.id} Add Payment '{pmc_no}'")
        Paymentmodel.insert_payment(subcontractor_id,pmc_no, invoice_no, amount, tds_amount, total_amount, utr)
        # Paymentmodel.update_inpayment(subcontractor_id, pmc_no, invoice_no, amount, tds_amount, total_amount, utr)

        return redirect(url_for('payment_bp.add_payment'))

    return render_template('add_payment.html', payments=payments)


# ------------------- Get PMC Nos -------------------
@payment_bp.route('/get_pmc_nos_by_subcontractor/<subcontractorId>')
@login_required
def get_pmc_nos_by_subcontractor(subcontractorId):
    connection = Paymentmodel.get_connection()
    cur = connection.cursor()
    cur.callproc('GetDistinctPMCNoByContractorId', [subcontractorId])
    results = []
    for result in cur.stored_results():
        results = result.fetchall()
    cur.close()
    pmc_nos = [row[0] for row in results]
    return jsonify({'pmc_nos': pmc_nos})


# ------------------- Edit Payment -------------------
@payment_bp.route('/edit_payment/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def edit_payment(payment_id):
    payment_data = Paymentmodel.fetch_payment_by_id(payment_id)

    if not payment_data:
        return "Payment not found", 404

    if request.method == 'POST':
        pmc_no = request.form['PMC_No']
        invoice_no = request.form['invoice_No']
        amount = request.form['Payment_Amount']
        tds_amount = request.form['TDS_Payment_Amount']
        total_amount = request.form['total_amount']
        utr = request.form['utr']

        LogHelper.log_action("Edit Payment", f"User {current_user.id} Edit Payment '{pmc_no}'")
        Paymentmodel.call_update_payment_proc(payment_id, pmc_no, invoice_no, amount, tds_amount, total_amount, utr)

        # Update inpayment
        # connection = Paymentmodel.get_connection()
        # cursor = connection.cursor()
        # cursor.callproc('UpdateInpaymentByPMCInvoiceUTR',[amount, tds_amount, total_amount, pmc_no, invoice_no, utr])

        # connection.commit()
        # cursor.close()
        # connection.close()

        return redirect(url_for('payment_bp.add_payment'))

    return render_template('edit_payment.html', payment_data=payment_data)

# ------------------- Delete Payment -------------------
@payment_bp.route('/delete_payment/<int:payment_id>', methods=['GET'])
@login_required
def delete_payment(payment_id):
    success, pmc_no, invoice_no = Paymentmodel.delete_payment(payment_id)

    if not success:
        flash("Payment not found or failed to delete", "error")
    else:
        LogHelper.log_action("Delete Payment", f"User {current_user.id} deleted Payment '{payment_id}'")
        flash(f"Payment ID {payment_id} deleted successfully.", "success")

    return redirect(url_for('payment_bp.add_payment'))