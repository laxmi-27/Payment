



from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

import config
from model.Village import Village
from model.State import State

# Create Blueprint
village_bp = Blueprint('village', __name__)
village = Village()

# ------------------------- Add Village -------------------------
@village_bp.route('/add_village', methods=['GET', 'POST'])
@login_required
def add_village():

    # village = Village()
 
    if request.method == 'POST':
        village.AddVillage(request=request)
        return village.resultMessage

    state = State()
    states = state.GetAllStates(request=request)
    villages = village.GetAllVillages(request=request)

    return render_template(
        'add_village.html',
        states=states,
        villages=villages
    )


# ------------------------- Fetch Districts -------------------------
@village_bp.route('/get_districts/<int:state_id>')
@login_required
def get_districts(state_id):

    connection = config.get_db_connection()
    cursor = connection.cursor()

    cursor.callproc("GetDistrictByStateID", [state_id])
    districts = []

    for rs in cursor.stored_results():
        districts = rs.fetchall()

    cursor.close()
    connection.close()

    return jsonify([{"id": d[0], "name": d[1]} for d in districts])


# ------------------------- Fetch Blocks -------------------------
@village_bp.route('/get_blocks/<int:district_id>')
@login_required
def get_blocks(district_id):

    connection = config.get_db_connection()
    cursor = connection.cursor()

    cursor.callproc("GetBlocksByDistrictID", [district_id])
    blocks = []

    for rs in cursor.stored_results():
        blocks = rs.fetchall()

    cursor.close()
    connection.close()

    return jsonify([{"id": b[0], "name": b[1]} for b in blocks])


# ------------------------- Check Village -------------------------
@village_bp.route('/check_village', methods=['POST'])
@login_required
def check_village():
    # village = Village()
    return village.CheckVillage(request=request)


@village_bp.route('/delete_village/<int:village_id>')
@login_required
def delete_village(village_id):
    # village = Village()
    village.DeleteVillage(request=request, village_id=village_id)

    # ✅ Convert resultMessage to string if it's a Response or tuple
    raw_msg = village.resultMessage

    if isinstance(raw_msg, tuple):
        # e.g., (<Response ...>, 200)
        msg = "Village deleted successfully!"
    elif hasattr(raw_msg, 'get_data'):
        # Flask Response object
        msg = raw_msg.get_data(as_text=True)  # get raw text
    else:
        # fallback
        msg = str(raw_msg) if raw_msg else "Village deleted successfully!"

    return jsonify({
        "status": "success" if village.isSuccess else "error",
        "message": msg
    })

# ------------------------- Edit Village -------------------------
@village_bp.route('/edit_village/<int:village_id>', methods=['GET', 'POST'])
@login_required
def edit_village(village_id):

    # village = Village()

    if request.method == 'POST':

        village.EditVillage(request=request, village_id=village_id)

        if village.isSuccess:
            flash(village.resultMessage, "success")
            return redirect(url_for('village.add_village'))

        else:
            flash(village.resultMessage, "error")

            village_data = village.GetVillageByID(id=village_id) or []
            blocks = village.GetAllBlocks() or []

            return render_template(
                'edit_village.html',
                village_data=village_data,
                blocks=blocks
            )

    else:
        # ✅ FIXED HERE (removed request)
        village_data = village.GetVillageByID(id=village_id)

        if not village.isSuccess:
            flash(village.resultMessage, "error")
            return redirect(url_for('village.add_village'))

        blocks = village.GetAllBlocks() or []

        return render_template(
            'edit_village.html',
            village_data=village_data or [],
            blocks=blocks
        )