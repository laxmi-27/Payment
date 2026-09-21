from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from model.State import State

state_bp = Blueprint('state', __name__)
state = State()


@state_bp.route('/add_state', methods=['GET', 'POST'])
@login_required
def add_state():
    if request.method == 'POST':
        state.AddState(request=request)
        return state.resultMessage

    statedata = state.GetAllStates(request=request)
    return render_template('add_state.html', statedata=statedata)


@state_bp.route('/check_state', methods=['POST'])
@login_required
def check_state():
    return state.CheckStateWithStatus(request=request)


@state_bp.route('/delete_state/<int:id>')
@login_required
def deleteState(id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    count = state.CheckStateHasDistricts(id)
    if count > 0:
        if is_ajax:
            return jsonify({
                'status': 'has_districts',
                'message': f'This state cannot be deleted because {count} district(s) are linked to it.',
                'district_count': count
            }), 409
        return redirect(url_for('state.add_state'))

    state.DeleteState(request=request, id=id)
    if is_ajax:
        if state.isSuccess:
            return jsonify({'status': 'success', 'message': 'State deleted successfully.'}), 200
        return state.resultMessage
    if state.isSuccess:
        return redirect(url_for('state.add_state'))
    return state.resultMessage


@state_bp.route('/edit_state/<int:id>', methods=['GET', 'POST'])
@login_required
def editState(id):
    if request.method == 'POST':
        state.EditState(request=request, id=id)
        if state.isSuccess:
            return redirect(url_for('state.add_state'))
        return state.resultMessage

    statedata = state.GetStateByID(request=request, id=id)
    if not state.isSuccess:
        return state.resultMessage
    if statedata is None:
        statedata = []
    return render_template('edit_state.html', state=statedata)


@state_bp.route('/can_delete_state/<int:id>')
@login_required
def canDeleteState(id):
    count = state.CheckStateHasDistricts(id)
    if count > 0:
        return jsonify({'can_delete': False, 'district_count': count,
                        'message': f'This state cannot be deleted because {count} district(s) are linked to it.'}), 200
    return jsonify({'can_delete': True}), 200


@state_bp.route('/activate_state/<int:id>', methods=['POST'])
@login_required
def activateState(id):
    return state.ActivateState(id)


@state_bp.route('/deactivate_state/<int:id>', methods=['POST'])
@login_required
def deactivateState(id):
    return state.DeactivateState(id)


@state_bp.route('/state_districts/<int:id>')
@login_required
def stateDistricts(id):
    districts = state.GetDistrictsByState(id)
    data = [{'id': d[0], 'name': d[1]} for d in districts]
    return jsonify({'districts': data, 'count': len(data)})
