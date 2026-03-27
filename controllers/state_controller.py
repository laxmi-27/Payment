from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from model.State import State

state_bp = Blueprint('state', __name__)

# ----- State page ------
@state_bp.route('/add_state', methods=['GET', 'POST'])
@login_required
def add_state():

    state = State()

    if request.method == 'POST':
        state.AddState(request=request)
        return state.resultMessage

    statedata = state.GetAllStates(request=request)

    return render_template('add_state.html', statedata=statedata)

# ----- State check ------
@state_bp.route('/check_state', methods=['POST'])
@login_required
def check_state():

    state = State()

    return state.CheckState(request=request)

# ----- State delete by state id ------
@state_bp.route('/delete_state/<int:id>')
@login_required
def deleteState(id):

    state = State()

    state.DeleteState(request=request, id=id)

    if not state.isSuccess:
        return state.resultMessage
    else:
        return redirect(url_for('state.add_state'))

# ----- State update by state id ------
@state_bp.route('/edit_state/<int:id>', methods=['GET', 'POST'])
@login_required
def editState(id):

    state = State()

    if request.method == 'POST':

        state.EditState(request=request, id=id)

        if state.isSuccess:
            return redirect(url_for('state.add_state'))
        else:
            return state.resultMessage

    statedata = state.GetStateByID(request=request, id=id)

    if not state.isSuccess:
        return state.resultMessage

    if statedata is None:
        statedata = []

    return render_template('edit_state.html', state=statedata)