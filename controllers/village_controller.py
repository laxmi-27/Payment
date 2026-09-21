import config
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from model.Village import Village
from model.State import State

village_bp = Blueprint('village', __name__)
village = Village()


@village_bp.route('/add_village', methods=['GET', 'POST'])
@login_required
def add_village():
    if request.method == 'POST':
        village.AddVillage(request=request)
        return village.resultMessage

    state = State()
    states = state.GetActiveStates()
    villages = village.GetAllVillages()
    return render_template('add_village.html', states=states, villages=villages)


@village_bp.route('/get_districts/<int:state_id>')
@login_required
def get_districts(state_id):
    conn = config.get_db_connection()
    cursor = conn.cursor()
    cursor.callproc("GetDistrictsByStateId", (state_id,))
    districts = []
    for rs in cursor.stored_results():
        districts = rs.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{"id": d[0], "name": d[1]} for d in districts])


@village_bp.route('/get_blocks/<int:district_id>')
@login_required
def get_blocks(district_id):
    conn = config.get_db_connection()
    cursor = conn.cursor()
    cursor.callproc("GetBlocksByDistrictID", (district_id,))
    blocks = []
    for rs in cursor.stored_results():
        blocks = rs.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{"id": b[0], "name": b[1]} for b in blocks])


@village_bp.route('/check_village', methods=['POST'])
@login_required
def check_village():
    return village.CheckVillage(request=request)


@village_bp.route('/delete_village/<int:village_id>')
@login_required
def delete_village(village_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    village.DeleteVillage(request=request, village_id=village_id)
    if is_ajax:
        return jsonify({
            'status': 'success' if village.isSuccess else 'error',
            'message': 'Village deleted successfully.' if village.isSuccess else str(village.resultMessage)
        })
    return redirect(url_for('village.add_village'))


@village_bp.route('/edit_village/<int:village_id>', methods=['GET', 'POST'])
@login_required
def edit_village(village_id):
    if request.method == 'POST':
        village.EditVillage(request=request, village_id=village_id)
        if village.isSuccess:
            flash(village.resultMessage, "success")
            return redirect(url_for('village.add_village'))
        else:
            flash(village.resultMessage, "error")
            village_data = village.GetVillageByID(id=village_id) or []
            blocks = village.GetAllBlocks() or []
            return render_template('edit_village.html', village_data=village_data, blocks=blocks)

    village_data = village.GetVillageByID(id=village_id)
    if not village.isSuccess:
        flash(village.resultMessage, "error")
        return redirect(url_for('village.add_village'))
    blocks = village.GetAllBlocks() or []
    return render_template('edit_village.html', village_data=village_data or [], blocks=blocks)


@village_bp.route('/activate_village/<int:village_id>', methods=['POST'])
@login_required
def activate_village(village_id):
    return village.ActivateVillage(village_id)


@village_bp.route('/deactivate_village/<int:village_id>', methods=['POST'])
@login_required
def deactivate_village(village_id):
    return village.DeactivateVillage(village_id)
