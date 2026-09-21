import config
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required

from model.State import State
from model.Block import Block

block_bp = Blueprint('block', __name__)
block = Block()


@block_bp.route('/add_block', methods=['GET', 'POST'])
@login_required
def add_block():
    if request.method == 'POST':
        block.AddBlock(request)
        return block.resultMessage

    state = State()
    states = state.GetActiveStates()
    block_data = block.GetAllBlocks()
    return render_template('add_block.html', states=states, block_data=block_data)


@block_bp.route('/get_districts/<int:state_id>')
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


@block_bp.route('/check_block', methods=['POST'])
@login_required
def check_block():
    return block.CheckBlock(request)


@block_bp.route('/edit_block/<int:block_id>', methods=['GET', 'POST'])
@login_required
def edit_block(block_id):
    if request.method == 'POST':
        block.EditBlock(request, block_id)
        if block.isSuccess:
            flash("Block updated successfully!", "success")
            return redirect(url_for('block.add_block'))
        else:
            flash(str(block.resultMessage), "error")

    conn = config.get_db_connection()
    cursor = conn.cursor()
    cursor.callproc("GetActiveStates")
    states = []
    for rs in cursor.stored_results():
        states = rs.fetchall()
    cursor.callproc("GetAllDistricts")
    districts = []
    for rs in cursor.stored_results():
        districts = rs.fetchall()
    block_data = block.GetBlockByID(block_id)
    cursor.close()
    conn.close()
    return render_template('edit_block.html', block_data=block_data, states=states, districts=districts)


@block_bp.route('/delete_block/<int:block_id>')
@login_required
def delete_block(block_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    count = block.CheckBlockHasVillages(block_id)
    if count > 0:
        if is_ajax:
            return jsonify({
                'status': 'has_villages',
                'message': f'This block cannot be deleted because {count} village(s) are linked to it.',
                'village_count': count
            }), 409
        return redirect(url_for('block.add_block'))

    block.DeleteBlock(request, block_id)
    if is_ajax:
        if block.isSuccess:
            return jsonify({'status': 'success', 'message': 'Block deleted successfully.'}), 200
        return block.resultMessage
    return redirect(url_for('block.add_block'))


@block_bp.route('/can_delete_block/<int:block_id>')
@login_required
def can_delete_block(block_id):
    count = block.CheckBlockHasVillages(block_id)
    if count > 0:
        return jsonify({
            'can_delete': False, 'village_count': count,
            'message': f'This block cannot be deleted because {count} village(s) are linked to it.'
        }), 200
    return jsonify({'can_delete': True}), 200


@block_bp.route('/activate_block/<int:block_id>', methods=['POST'])
@login_required
def activate_block(block_id):
    return block.ActivateBlock(block_id)


@block_bp.route('/deactivate_block/<int:block_id>', methods=['POST'])
@login_required
def deactivate_block(block_id):
    return block.DeactivateBlock(block_id)


@block_bp.route('/block_villages/<int:block_id>')
@login_required
def block_villages(block_id):
    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Village_Id, Village_Name, COALESCE(status,'Active') "
            "FROM villages WHERE Block_Id=%s ORDER BY Village_Name", (block_id,))
        rows = cursor.fetchall()
        return jsonify({'villages': [{'id': r[0], 'name': r[1], 'status': r[2]} for r in rows], 'count': len(rows)})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
