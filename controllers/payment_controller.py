from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from model.payment import Paymentmodel
from model.Log import LogHelper

payment_bp = Blueprint('payment_bp', __name__)


# ----------------------------------------------------------
# ADD PAYMENT  (GET: render page  |  POST: JSON)
# ----------------------------------------------------------
@payment_bp.route('/add_payment', methods=['GET', 'POST'])
@login_required
def add_payment():
    if request.method == 'POST':
        utr = request.form.get('utr', '').strip()

        if not utr:
            return jsonify({"success": False, "message": "UTR is required."}), 400

        if Paymentmodel.check_duplicate_utr(utr):
            short = utr[:40] + ('...' if len(utr) > 40 else '')
            return jsonify({"success": False,
                            "message": f"UTR '{short}' is already registered. Duplicate UTR not allowed."}), 409

        subcontractor_id = request.form.get('subcontractor_id', '').strip()
        pmc_no           = request.form.get('PMC_No', '').strip()
        invoice_no       = request.form.get('invoice_No', '').strip()
        amount           = request.form.get('Amount_with_TDS', '0')
        tds_percentage   = request.form.get('TDS_Percentage', '0')
        tds_amount       = request.form.get('TDS_Payment_Amount', '0')
        total_amount     = request.form.get('total_amount', '0')
        payment_date     = request.form.get('payment_date', '') or None
        payment_status   = request.form.get('payment_status', 'Paid')

        LogHelper.log_action("Add Payment",
                             f"User {current_user.id} added payment PMC={pmc_no} UTR={utr[:30]}")

        result = Paymentmodel.insert_payment(
            subcontractor_id, pmc_no, invoice_no,
            amount, tds_percentage, tds_amount, total_amount,
            utr, payment_date, payment_status
        )

        if result:
            return jsonify({"success": True, "message": "Payment added successfully."})
        return jsonify({"success": False, "message": "Failed to add payment. Please try again."}), 500

    payments = Paymentmodel.fetch_all_payments() or []
    return render_template('add_payment.html', payments=payments)


# ----------------------------------------------------------
# SEARCH CONTRACTORS  (autocomplete)
# ----------------------------------------------------------
@payment_bp.route('/api/payment/search_contractors')
@login_required
def api_search_contractors():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})
    results = Paymentmodel.search_contractors(q)
    return jsonify({'results': [
        {'id': r['Contractor_Id'], 'name': r['Contractor_Name']}
        for r in results
    ]})


# ----------------------------------------------------------
# GET PAYMENT BY ID  (View Details API)
# ----------------------------------------------------------
@payment_bp.route('/api/payment/<int:payment_id>', methods=['GET'])
@login_required
def api_get_payment(payment_id):
    payment = Paymentmodel.fetch_payment_by_id(payment_id)
    if not payment:
        return jsonify({"success": False}), 404

    def fstr(v):
        return str(v) if v is not None else '0.00'

    return jsonify({
        "success":    True,
        "id":         payment.get('Payment_Id'),
        "contractor": payment.get('Contractor_Name') or '',
        "pmc":        str(payment.get('PMC_No') or ''),
        "invoice":    str(payment.get('Invoice_No') or ''),
        "amount":     fstr(payment.get('Amount_with_TDS')),
        "tds_pct":    fstr(payment.get('TDS_Percentage')),
        "tds_amt":    fstr(payment.get('TDS_Payment_Amount')),
        "total":      fstr(payment.get('Amount_after_TDS_Deduction')),
        "utr":        payment.get('UTR') or '',
        "date":       str(payment.get('Payment_Date')) if payment.get('Payment_Date') else '',
        "status":     payment.get('Payment_Status') or 'Paid',
    })


# ----------------------------------------------------------
# GET PMC NOS BY SUBCONTRACTOR  (existing route, kept)
# ----------------------------------------------------------
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
    connection.close()
    pmc_nos = [row[0] for row in results]
    return jsonify({'pmc_nos': pmc_nos})


# ----------------------------------------------------------
# GET INVOICES BY CONTRACTOR + PMC
# ----------------------------------------------------------
@payment_bp.route('/api/payment/invoices/<int:contractor_id>/<int:pmc_no>')
@login_required
def api_invoices_for_payment(contractor_id, pmc_no):
    invoices = Paymentmodel.get_invoices_by_contractor_pmc(contractor_id, pmc_no)
    result = [
        {
            'invoice_no':    str(inv.get('invoice_no', '') or ''),
            'basic_amount':  str(inv.get('Basic_Amount', '0') or '0'),
            'final_amount':  str(inv.get('Final_Amount', '0') or '0'),
        }
        for inv in invoices
    ]
    return jsonify({'invoices': result})


# ----------------------------------------------------------
# EDIT PAYMENT  (GET: render form  |  POST: JSON)
# ----------------------------------------------------------
@payment_bp.route('/edit_payment/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def edit_payment(payment_id):
    if request.method == 'POST':
        utr = request.form.get('utr', '').strip()

        if not utr:
            return jsonify({"success": False, "message": "UTR is required."}), 400

        if Paymentmodel.check_duplicate_utr(utr, exclude_id=payment_id):
            return jsonify({"success": False,
                            "message": "UTR is already registered to another payment."}), 409

        pmc_no         = request.form.get('PMC_No', '').strip()
        invoice_no     = request.form.get('invoice_No', '').strip()
        amount         = request.form.get('Amount_with_TDS', '0')
        tds_percentage = request.form.get('TDS_Percentage', '0')
        tds_amount     = request.form.get('TDS_Payment_Amount', '0')
        total_amount   = request.form.get('total_amount', '0')
        payment_date   = request.form.get('payment_date', '') or None
        payment_status = request.form.get('payment_status', 'Paid')

        LogHelper.log_action("Edit Payment",
                             f"User {current_user.id} edited payment {payment_id}")

        result = Paymentmodel.call_update_payment_proc(
            payment_id, pmc_no, invoice_no,
            amount, tds_percentage, tds_amount, total_amount,
            utr, payment_date, payment_status
        )

        if result is True:
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Failed to update payment. Please try again."}), 500

    payment_data = Paymentmodel.fetch_payment_by_id(payment_id)
    if not payment_data:
        return "Payment not found", 404

    return render_template('edit_payment.html', payment_data=payment_data)


# ----------------------------------------------------------
# DELETE PAYMENT  (POST → JSON)
# ----------------------------------------------------------
@payment_bp.route('/delete_payment/<int:payment_id>', methods=['POST'])
@login_required
def delete_payment(payment_id):
    success, pmc_no, invoice_no = Paymentmodel.delete_payment(payment_id)
    if not success:
        return jsonify({"success": False, "message": "Payment not found or failed to delete."}), 500

    LogHelper.log_action("Delete Payment",
                         f"User {current_user.id} deleted payment {payment_id}")
    return jsonify({"success": True})
