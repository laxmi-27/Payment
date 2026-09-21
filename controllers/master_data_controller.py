from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import config
import mysql.connector

master_data_bp = Blueprint('master_data', __name__)

# ──────────────────────────────────────────────
# PAGE RENDER
# ──────────────────────────────────────────────

@master_data_bp.route('/master_data')
@login_required
def master_data():
    return render_template('master_data.html')


# ──────────────────────────────────────────────
# HIERARCHY TABLE
# ──────────────────────────────────────────────

@master_data_bp.route('/api/master/hierarchy')
@login_required
def api_hierarchy():
    def _int(v):
        try:
            return int(v) if v else None
        except (ValueError, TypeError):
            return None

    state_id    = _int(request.args.get('state_id'))
    district_id = _int(request.args.get('district_id'))
    block_id    = _int(request.args.get('block_id'))
    status      = request.args.get('status', '')
    search      = request.args.get('search', '')

    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc('GetMasterHierarchy',
                        (state_id, district_id, block_id, status, search))
        rows = []
        for rs in cursor.stored_results():
            for r in rs.fetchall():
                rows.append({
                    'state_id':         r[0],  'state_name':     r[1],  'state_status':    r[2],
                    'district_id':      r[3],  'district_name':  r[4],  'district_status': r[5],
                    'block_id':         r[6],  'block_name':     r[7],  'block_status':    r[8],
                    'village_id':       r[9],  'village_name':   r[10], 'village_status':  r[11],
                    'updated_at': str(r[12])[:10] if r[12] else '—',
                })
        return jsonify({'rows': rows, 'count': len(rows)})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ──────────────────────────────────────────────
# STATE SUMMARY
# ──────────────────────────────────────────────

@master_data_bp.route('/api/master/state_summary/<int:state_id>')
@login_required
def api_state_summary(state_id):
    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc('GetStateSummary', (state_id,))
        row = None
        for rs in cursor.stored_results():
            row = rs.fetchone()
        if not row:
            return jsonify({'error': 'State not found'}), 404
        return jsonify({
            'state_name':      row[0],
            'status':          row[1],
            'last_updated':    str(row[2])[:10] if row[2] else '—',
            'district_count':  row[3],
            'block_count':     row[4],
            'village_count':   row[5],
        })
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ──────────────────────────────────────────────
# DROPDOWN DATA
# ──────────────────────────────────────────────

@master_data_bp.route('/api/master/active_districts/<int:state_id>')
@login_required
def api_active_districts(state_id):
    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc('GetActiveDistrictsByState', (state_id,))
        data = []
        for rs in cursor.stored_results():
            data = [{'id': r[0], 'name': r[1]} for r in rs.fetchall()]
        return jsonify(data)
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@master_data_bp.route('/api/master/active_blocks/<int:district_id>')
@login_required
def api_active_blocks(district_id):
    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc('GetActiveBlocksByDistrict', (district_id,))
        data = []
        for rs in cursor.stored_results():
            data = [{'id': r[0], 'name': r[1]} for r in rs.fetchall()]
        return jsonify(data)
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@master_data_bp.route('/api/master/filter_options')
@login_required
def api_filter_options():
    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT State_Id, State_Name FROM states ORDER BY State_Name")
        states = [{'id': r[0], 'name': r[1]} for r in cursor.fetchall()]
        cursor.execute("SELECT District_id, District_Name FROM districts ORDER BY District_Name")
        districts = [{'id': r[0], 'name': r[1]} for r in cursor.fetchall()]
        cursor.execute("SELECT Block_Id, Block_Name FROM blocks ORDER BY Block_Name")
        blocks = [{'id': r[0], 'name': r[1]} for r in cursor.fetchall()]
        return jsonify({'states': states, 'districts': districts, 'blocks': blocks})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ──────────────────────────────────────────────
# INLINE ADD
# ──────────────────────────────────────────────

@master_data_bp.route('/api/master/add_district', methods=['POST'])
@login_required
def api_add_district():
    data     = request.json or {}
    name     = (data.get('name') or '').strip()
    state_id = data.get('state_id')
    status   = data.get('status', 'Active')

    if not name or not state_id:
        return jsonify({'error': 'District name and state are required.'}), 400

    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT District_id FROM districts "
            "WHERE LOWER(TRIM(District_Name))=LOWER(TRIM(%s)) AND State_Id=%s",
            (name, state_id))
        if cursor.fetchone():
            return jsonify({'error': 'District already exists under this state.'}), 409
        cursor.execute(
            "INSERT INTO districts (District_Name, State_Id, status) VALUES (%s, %s, %s)",
            (name, state_id, status))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'District added.', 'id': cursor.lastrowid})
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@master_data_bp.route('/api/master/add_block', methods=['POST'])
@login_required
def api_add_block():
    data        = request.json or {}
    name        = (data.get('name') or '').strip()
    district_id = data.get('district_id')
    status      = data.get('status', 'Active')

    if not name or not district_id:
        return jsonify({'error': 'Block name and district are required.'}), 400

    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Block_Id FROM blocks "
            "WHERE LOWER(TRIM(Block_Name))=LOWER(TRIM(%s)) AND District_id=%s",
            (name, district_id))
        if cursor.fetchone():
            return jsonify({'error': 'Block already exists under this district.'}), 409
        cursor.execute(
            "INSERT INTO blocks (Block_Name, District_id, status) VALUES (%s, %s, %s)",
            (name, district_id, status))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Block added.', 'id': cursor.lastrowid})
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@master_data_bp.route('/api/master/add_village', methods=['POST'])
@login_required
def api_add_village():
    data     = request.json or {}
    name     = (data.get('name') or '').strip()
    block_id = data.get('block_id')
    status   = data.get('status', 'Active')

    if not name or not block_id:
        return jsonify({'error': 'Village name and block are required.'}), 400

    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Village_Id FROM villages "
            "WHERE LOWER(TRIM(Village_Name))=LOWER(TRIM(%s)) AND Block_Id=%s",
            (name, block_id))
        if cursor.fetchone():
            return jsonify({'error': 'Village already exists under this block.'}), 409
        cursor.execute(
            "INSERT INTO villages (Village_Name, Block_Id, status) VALUES (%s, %s, %s)",
            (name, block_id, status))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Village added.', 'id': cursor.lastrowid})
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ──────────────────────────────────────────────
# STATUS CHANGE (with optional cascade)
# ──────────────────────────────────────────────

@master_data_bp.route('/api/master/status_change', methods=['POST'])
@login_required
def api_status_change():
    data        = request.json or {}
    etype       = data.get('type')      # state / district / block / village
    eid         = data.get('id')
    action      = data.get('action')    # activate / deactivate
    cascade     = bool(data.get('cascade', False))
    new_status  = 'Active' if action == 'activate' else 'Inactive'

    if etype not in ('state', 'district', 'block', 'village') or not eid:
        return jsonify({'error': 'Invalid parameters.'}), 400

    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()

        if etype == 'state':
            cursor.execute("UPDATE states SET status=%s WHERE State_Id=%s", (new_status, eid))
            if cascade:
                cursor.execute("UPDATE districts SET status=%s WHERE State_Id=%s", (new_status, eid))
                cursor.execute(
                    "UPDATE blocks b JOIN districts d ON b.District_id=d.District_id "
                    "SET b.status=%s WHERE d.State_Id=%s", (new_status, eid))
                cursor.execute(
                    "UPDATE villages v "
                    "JOIN blocks b ON v.Block_Id=b.Block_Id "
                    "JOIN districts d ON b.District_id=d.District_id "
                    "SET v.status=%s WHERE d.State_Id=%s", (new_status, eid))

        elif etype == 'district':
            cursor.execute("UPDATE districts SET status=%s WHERE District_id=%s", (new_status, eid))
            if cascade:
                cursor.execute("UPDATE blocks SET status=%s WHERE District_id=%s", (new_status, eid))
                cursor.execute(
                    "UPDATE villages v JOIN blocks b ON v.Block_Id=b.Block_Id "
                    "SET v.status=%s WHERE b.District_id=%s", (new_status, eid))

        elif etype == 'block':
            cursor.execute("UPDATE blocks SET status=%s WHERE Block_Id=%s", (new_status, eid))
            if cascade:
                cursor.execute("UPDATE villages SET status=%s WHERE Block_Id=%s", (new_status, eid))

        elif etype == 'village':
            cursor.execute("UPDATE villages SET status=%s WHERE Village_Id=%s", (new_status, eid))

        conn.commit()
        label = 'activated' if action == 'activate' else 'deactivated'
        return jsonify({'status': 'success',
                        'message': f'{etype.capitalize()} {label} successfully.'})
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

@master_data_bp.route('/api/master/delete', methods=['POST'])
@login_required
def api_delete():
    data  = request.json or {}
    etype = data.get('type')
    eid   = data.get('id')

    if etype not in ('state', 'district', 'block', 'village') or not eid:
        return jsonify({'error': 'Invalid parameters.'}), 400

    conn = config.get_db_connection()
    try:
        cursor = conn.cursor()

        if etype == 'state':
            cursor.execute("SELECT COUNT(*) FROM districts WHERE State_Id=%s", (eid,))
            n = cursor.fetchone()[0]
            if n:
                return jsonify({'error': f'Cannot delete: {n} district(s) linked. Deactivate instead.'}), 409
            cursor.execute("DELETE FROM states WHERE State_Id=%s", (eid,))

        elif etype == 'district':
            cursor.execute("SELECT COUNT(*) FROM blocks WHERE District_id=%s", (eid,))
            n = cursor.fetchone()[0]
            if n:
                return jsonify({'error': f'Cannot delete: {n} block(s) linked. Deactivate instead.'}), 409
            cursor.execute("DELETE FROM districts WHERE District_id=%s", (eid,))

        elif etype == 'block':
            cursor.execute("SELECT COUNT(*) FROM villages WHERE Block_Id=%s", (eid,))
            n = cursor.fetchone()[0]
            if n:
                return jsonify({'error': f'Cannot delete: {n} village(s) linked. Deactivate instead.'}), 409
            cursor.execute("DELETE FROM blocks WHERE Block_Id=%s", (eid,))

        elif etype == 'village':
            cursor.execute("DELETE FROM villages WHERE Village_Id=%s", (eid,))

        conn.commit()
        return jsonify({'status': 'success', 'message': f'{etype.capitalize()} deleted.'})
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
