from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from model.District import District
from model.State import State

district_bp = Blueprint('district', __name__)
district = District()


@district_bp.route('/add_district', methods=['GET', 'POST'])
@login_required
def add_district():
    if request.method == 'POST':
        district.AddDistrict(request=request)
        return district.resultMessage

    state = State()
    states = state.GetActiveStates()
    districtdata = district.GetAllDistricts()
    return render_template('add_district.html', districtdata=districtdata, states=states)


@district_bp.route('/check_district', methods=['POST'])
@login_required
def check_district():
    return district.CheckDistrict(request=request)


@district_bp.route('/delete_district/<int:district_id>')
@login_required
def delete_district(district_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    count = district.CheckDistrictHasBlocks(district_id)
    if count > 0:
        if is_ajax:
            return jsonify({
                'status': 'has_blocks',
                'message': f'This district cannot be deleted because {count} block(s) are linked to it.',
                'block_count': count
            }), 409
        return redirect(url_for('district.add_district'))

    district.DeleteDistrict(request=request, district_id=district_id)
    if is_ajax:
        if district.isSuccess:
            return jsonify({'status': 'success', 'message': 'District deleted successfully.'}), 200
        return district.resultMessage
    if district.isSuccess:
        return redirect(url_for('district.add_district'))
    return district.resultMessage


@district_bp.route('/can_delete_district/<int:district_id>')
@login_required
def can_delete_district(district_id):
    count = district.CheckDistrictHasBlocks(district_id)
    if count > 0:
        return jsonify({
            'can_delete': False, 'block_count': count,
            'message': f'This district cannot be deleted because {count} block(s) are linked to it.'
        }), 200
    return jsonify({'can_delete': True}), 200


@district_bp.route('/edit_district/<int:district_id>', methods=['GET', 'POST'])
@login_required
def edit_district(district_id):
    state = State()
    if request.method == 'POST':
        district.EditDistrict(request=request, district_id=district_id)
        if district.isSuccess:
            flash("District updated successfully!", "success")
            return redirect(url_for('district.add_district'))
        else:
            flash(str(district.resultMessage), "error")

    districtdata = district.GetDistrictByID(request=request, district_id=district_id)
    if not districtdata:
        flash("District not found", "error")
        return redirect(url_for('district.add_district'))

    states = state.GetActiveStates()
    return render_template('edit_district.html', districtdata=districtdata, states=states)


@district_bp.route('/activate_district/<int:district_id>', methods=['POST'])
@login_required
def activate_district(district_id):
    return district.ActivateDistrict(district_id)


@district_bp.route('/deactivate_district/<int:district_id>', methods=['POST'])
@login_required
def deactivate_district(district_id):
    return district.DeactivateDistrict(district_id)


@district_bp.route('/district_blocks/<int:district_id>')
@login_required
def district_blocks(district_id):
    import config, mysql.connector
    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Block_Id, Block_Name, COALESCE(status,'Active') "
            "FROM blocks WHERE District_id=%s ORDER BY Block_Name", (district_id,))
        rows = cursor.fetchall()
        return jsonify({'blocks': [{'id': r[0], 'name': r[1], 'status': r[2]} for r in rows], 'count': len(rows)})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
