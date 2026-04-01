# controllers/invoice_controller.py

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from model.Invoice import *
from model.Log import LogHelper

invoice_bp = Blueprint('invoice', __name__)

# ------------------------------- Helpers -------------------------------
def handle_exception(func):
    """Decorator to handle exceptions and return JSON error responses."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    wrapper.__name__ = func.__name__
    return wrapper

def log_action(action: str, detail: str):
    LogHelper.log_action(action, f"User {current_user.id} {detail}")


# ------------------------------- Add Invoice -------------------------------
@invoice_bp.route('/add_invoice', methods=['GET', 'POST'])
@login_required
@handle_exception
def add_invoice():
    if request.method == 'POST':
        data = request.form
        village_name = data.get('village')
        village_result = get_village_id(village_name)

        if not village_result:
            return jsonify({"status": "error", "message": f"Village '{village_name}' not found"}), 400

        village_id = village_result['Village_Id']
        invoice_id = insert_invoice(data, village_id)
        # assign_subcontractor(data, village_id)
       
        insert_hold_types(data, invoice_id)

        log_action("Add invoice", f"added invoice '{data.get('pmc_no')}'")
        return jsonify({"status": "success", "message": "Invoice added successfully"}), 201

    invoices = get_all_invoice_details()
    villages = get_all_villages()
    return render_template('add_invoice.html', invoices=invoices, villages=villages)


# ------------------------------- Search Subcontractor -------------------------------
@invoice_bp.route('/search_subcontractor', methods=['POST'])
@login_required
@handle_exception
def search_subcontractor():
    query = request.form.get("query", "").strip()
    results = search_contractors(query)

    if not results:
        return "<li>No subcontractor found</li>"

    return "".join(f"<li data-id='{r['Contractor_Id']}'>{r['Contractor_Name']}</li>" for r in results)


# ------------------------------- Get Hold Types -------------------------------
@invoice_bp.route('/get_hold_types', methods=['GET'])
@login_required
@handle_exception
def get_hold_types():
    hold_types = get_all_hold_types()
    log_action("Get hold type", f"retrieved hold types '{hold_types}'")
    return jsonify(hold_types)


# ------------------------------- Edit Invoice -------------------------------
@invoice_bp.route('/edit_invoice/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
@handle_exception
def edit_invoice(invoice_id):
    if request.method == 'POST':
        data = request.form
        update_invoice(data, invoice_id)
        # update_inpayment(data)
        log_action("Edit invoice", f"edited invoice '{invoice_id}'")
        return jsonify({"status": "success", "message": "Invoice updated successfully"}), 200

    invoice = get_invoice_by_id(invoice_id)
    return render_template('edit_invoice.html', invoice=invoice)


# ------------------------------- Delete Invoice -------------------------------
@invoice_bp.route('/delete_invoice/<int:invoice_id>', methods=['GET'])
@login_required
@handle_exception
def delete_invoice_route(invoice_id):
    delete_invoice_data(invoice_id, current_user.id)
    log_action("Delete invoice", f"deleted invoice '{invoice_id}'")
    return jsonify({"status": "success", "message": f"Invoice {invoice_id} deleted successfully."})