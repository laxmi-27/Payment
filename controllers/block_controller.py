import config
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required

from model.State import State
from model.Block import Block
from model.Utilities import HtmlHelper

block_bp = Blueprint('block', __name__)
block = Block()
# --- Add Block page -------
@block_bp.route('/add_block', methods=['GET', 'POST'])
@login_required
def add_block():
    # block = Block()

    if request.method == 'POST':
        block.AddBlock(request)
        return block.resultMessage
    
    state = State()
    states = state.GetAllStates(request=request)

    block_data = block.GetAllBlocks(request)

    return render_template(
        'add_block.html',
        states=states,
        block_data=block_data
    )


# ✅ NEW ROUTE (FIX FOR DISTRICT FETCH)
@block_bp.route('/get_districts/<int:state_id>')
@login_required
def get_districts(state_id):

    connection = config.get_db_connection()
    cursor = connection.cursor()

    cursor.callproc("GetDistrictsByStateId", (state_id,))

    districts = []
    for rs in cursor.stored_results():
        districts = rs.fetchall()

    cursor.close()
    connection.close()

    district_list = []

    for district in districts:
        district_list.append({
            "id": district[0],
            "name": district[1]
        })

    return jsonify(district_list)


@block_bp.route('/check_block', methods=['POST'])
@login_required
def check_block():

    # block = Block()
    return block.CheckBlock(request)


@block_bp.route('/edit_block/<int:block_id>', methods=['GET', 'POST'])
@login_required
def edit_block(block_id):

    
#   block = Block()
    if request.method == 'POST':
        block.EditBlock(request, block_id)
        block.resultMessage

        if block.resultMessage:
            flash("Block updated successfully!", "success")
            return redirect(url_for('block.add_block'))
        else:
            flash(block.resultMessage, "error")

        
    connection = config.get_db_connection()
    cursor = connection.cursor()

    cursor.callproc("GetAllStates")
    for rs in cursor.stored_results():
        states = rs.fetchall()

    cursor.callproc("GetAllDistricts")
    for rs in cursor.stored_results():
        districts = rs.fetchall()

    block_data = block.GetBlockByID(block_id)

    cursor.close()
    connection.close()

    return render_template(
        'edit_block.html',
        block_data=block_data,
        states=states,
        districts=districts
    )


@block_bp.route('/delete_block/<int:block_id>')
@login_required
def delete_block(block_id):

    # block = Block()
    block.DeleteBlock(request, block_id)

    return redirect(url_for('block.add_block'))