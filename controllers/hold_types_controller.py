from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from model.HoldTypes import HoldTypes

hold_bp = Blueprint("hold_types", __name__)
hold_service = HoldTypes()


# ---------------- LIST / ADD HOLD TYPE ----------------
@hold_bp.route('/add_hold_type', methods=['GET', 'POST'])
@login_required
def add_hold_type():
    if request.method == 'POST':
        hold_service.AddHoldType(request)
        return jsonify({"success": hold_service.isSuccess, "message": hold_service.resultMessage})

    hold_types = hold_service.GetAllHoldTypes()
    return render_template('add_hold_type.html', hold_types=hold_types)


# ---------------- API: GET SINGLE HOLD TYPE ----------------
@hold_bp.route('/api/hold_type/<int:hold_type_id>', methods=['GET'])
@login_required
def api_get_hold_type(hold_type_id):
    data = hold_service.GetHoldTypeByID(hold_type_id)
    if not data:
        return jsonify({"success": False}), 404

    def fstr(v):
        return str(v) if v is not None else ''

    return jsonify({
        "success":     True,
        "id":          data.get('hold_type_id'),
        "name":        data.get('hold_type') or '',
        "category":    data.get('hold_category') or '',
        "description": data.get('description') or '',
        "default_pct": fstr(data.get('default_hold_percentage')),
        "status":      data.get('status') or 'Active',
        "created":     str(data.get('created_date')) if data.get('created_date') else '',
        "updated":     str(data.get('last_updated_date')) if data.get('last_updated_date') else '',
    })


# ---------------- EDIT HOLD TYPE ----------------
@hold_bp.route('/edit_hold_type/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_hold_type(id):
    if request.method == 'POST':
        hold_service.EditHoldType(request, id)
        flash(hold_service.resultMessage, 'success' if hold_service.isSuccess else 'error')
        return redirect(url_for('hold_types.add_hold_type'))

    hold_data = hold_service.GetHoldTypeByID(id)
    if not hold_data:
        return "Hold Type not found", 404
    return render_template('edit_hold_type.html', hold_type=hold_data)


# ---------------- DELETE HOLD TYPE ----------------
@hold_bp.route('/delete_hold_type/<int:id>', methods=['POST'])
@login_required
def delete_hold_type(id):
    hold_service.DeleteHoldType(id)
    return jsonify({"success": hold_service.isSuccess, "message": hold_service.resultMessage})
