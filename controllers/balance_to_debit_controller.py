from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import config

balance_to_debit_bp = Blueprint('balance_to_debit_bp', __name__)


def _get_all():
    conn = config.get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT b.id, b.contractor_id, s.Contractor_Name, b.balance_debit
            FROM balance_to_debit b
            JOIN subcontractors s ON s.Contractor_Id = b.contractor_id
            ORDER BY s.Contractor_Name
        """)
        return cur.fetchall()
    except Exception as e:
        print(f"Error fetching balance_to_debit: {e}")
        return []
    finally:
        cur.close()
        conn.close()


@balance_to_debit_bp.route('/balance_to_debit')
@login_required
def balance_to_debit_page():
    records = _get_all()
    return render_template('balance_to_debit.html', records=records)


@balance_to_debit_bp.route('/balance_to_debit/add', methods=['POST'])
@login_required
def add_balance_to_debit():
    contractor_id = request.form.get('contractor_id', '').strip()
    balance_debit = request.form.get('balance_debit', '0').strip()
    if not contractor_id:
        return jsonify({'success': False, 'message': 'Contractor is required.'}), 400
    try:
        balance_debit = float(balance_debit or 0)
        conn = config.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO balance_to_debit (contractor_id, balance_debit)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE balance_debit = VALUES(balance_debit)
        """, (contractor_id, balance_debit))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Saved successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@balance_to_debit_bp.route('/balance_to_debit/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_balance_to_debit(record_id):
    try:
        conn = config.get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM balance_to_debit WHERE id = %s", (record_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@balance_to_debit_bp.route('/api/balance_to_debit/search_contractors')
@login_required
def search_contractors_btd():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})
    try:
        conn = config.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT Contractor_Id AS id, Contractor_Name AS name
            FROM subcontractors
            WHERE Contractor_Name LIKE %s
            ORDER BY Contractor_Name LIMIT 20
        """, (f'%{q}%',))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'results': [], 'error': str(e)})
