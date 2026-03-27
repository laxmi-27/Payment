from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from model.HoldTypes import HoldTypes
from model.GST import GST

hold_bp = Blueprint("hold_types", __name__)


# ---------------- ADD HOLD TYPE ----------------
@hold_bp.route('/add_hold_type', methods=['GET','POST'])
@login_required
def add_hold_type():
    hold = HoldTypes()

    if request.method == 'POST':
        hold.AddHoldType(request)
        # ✅ Always redirect to same page (NO JSON)
        return redirect(url_for("hold_types.add_hold_type"))

    # GET request → show data
    hold_types = hold.GetAllHoldTypes()

    return render_template(
        "add_hold_type.html",
        Hold_Types_data=hold_types
    )

# ---------------- CHECK HOLD TYPE (OPTIONAL LIKE BLOCK) ----------------
@hold_bp.route('/check_hold_type', methods=['POST'])
@login_required
def check_hold_type():

    hold = HoldTypes()
    return hold.CheckHoldType(request)   # if exists


# ---------------- EDIT HOLD TYPE ----------------
@hold_bp.route('/edit_hold_type/<int:id>', methods=['GET','POST'])
@login_required
def edit_hold_type(id):

    hold = HoldTypes()

    if request.method == 'POST':
        hold.EditHoldType(request, id)   # ✅
        return hold.resultMessage

    hold_data = hold.GetHoldTypeByID(id)   # ✅

    return render_template(
        "edit_hold_type.html",
        hold_type=hold_data
    )


# ---------------- DELETE HOLD TYPE ----------------
@hold_bp.route('/delete_hold_type/<int:id>')
@login_required
def delete_hold_type(id):

    hold = HoldTypes()
    hold.DeleteHoldType(request, id)   # ✅

    return redirect(url_for("hold_types.add_hold_type"))


# ---------------- GST ----------------
@hold_bp.route('/unreleased_gst')
@login_required
def unreleased_gst():

    data = GST.get_unreleased_gst()

    return render_template(
        "unreleased_gst.html",
        data=data
    )