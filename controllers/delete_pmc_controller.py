from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import config
from model.Log import LogHelper

del_pmc_bp = Blueprint('del_pmc_bp', __name__)


def _get_conn():
    return config.get_db_connection()


def _placeholders(lst):
    return ','.join(['%s'] * len(lst))


@del_pmc_bp.route('/delete_pmc')
@login_required
def delete_pmc_page():
    return render_template('delete_pmc.html')


@del_pmc_bp.route('/api/delete_pmc/preview', methods=['POST'])
@login_required
def preview_delete_pmc():
    data          = request.get_json(force=True)
    contractor_id = int(data.get('contractor_id') or 0)
    pmc_nos       = [int(p) for p in (data.get('pmc_nos') or []) if str(p).strip()]

    if not contractor_id or not pmc_nos:
        return jsonify({'success': False, 'message': 'No contractor or PMC numbers selected.'})

    conn = None
    try:
        conn   = _get_conn()
        cursor = conn.cursor(dictionary=True)
        ph     = _placeholders(pmc_nos)

        cursor.execute(
            f"SELECT COUNT(*) AS cnt FROM payment p JOIN invoices i ON p.Invoice_Id = i.Invoice_Id "
            f"WHERE p.PMC_No IN ({ph}) AND i.Subcontractor_Id = %s",
            pmc_nos + [contractor_id]
        )
        payments_count = cursor.fetchone()['cnt']

        cursor.execute(
            f"SELECT COUNT(*) AS cnt FROM invoices WHERE PMC_No IN ({ph}) AND Subcontractor_Id = %s",
            pmc_nos + [contractor_id]
        )
        invoices_count = cursor.fetchone()['cnt']

        cursor.execute(
            f"SELECT COUNT(*) AS cnt FROM gst_releases WHERE PMC_No IN ({ph}) AND Contractor_ID = %s",
            pmc_nos + [contractor_id]
        )
        gst_count = cursor.fetchone()['cnt']

        cursor.execute(
            f"SELECT COUNT(*) AS cnt FROM credit_note WHERE PMC_No IN ({ph}) AND Contractor_Id = %s",
            pmc_nos + [contractor_id]
        )
        cdn_count = cursor.fetchone()['cnt']

        cursor.execute(
            f"SELECT COUNT(*) AS cnt FROM hold_release WHERE PMC_No IN ({ph}) AND Contractor_Id = %s",
            pmc_nos + [contractor_id]
        )
        hr_count = cursor.fetchone()['cnt']

        return jsonify({
            'success': True,
            'counts': {
                'payments':    payments_count,
                'invoices':    invoices_count,
                'gst_release': gst_count,
                'credit_notes': cdn_count,
                'hold_release': hr_count,
            }
        })
    except Exception as e:
        print("ERROR in preview_delete_pmc:", e)
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if conn:
            try:
                cursor.close(); conn.close()
            except Exception:
                pass


@del_pmc_bp.route('/api/delete_pmc/execute', methods=['POST'])
@login_required
def execute_delete_pmc():
    data          = request.get_json(force=True)
    contractor_id = int(data.get('contractor_id') or 0)
    pmc_nos       = [int(p) for p in (data.get('pmc_nos') or []) if str(p).strip()]

    if not contractor_id or not pmc_nos:
        return jsonify({'success': False, 'message': 'No contractor or PMC numbers selected.'})

    conn = None
    try:
        conn   = _get_conn()
        cursor = conn.cursor()
        ph     = _placeholders(pmc_nos)
        args   = pmc_nos + [contractor_id]

        # 1. Delete payments first (via invoice join since payment has no direct contractor FK)
        cursor.execute(
            f"DELETE p FROM payment p JOIN invoices i ON p.Invoice_Id = i.Invoice_Id "
            f"WHERE p.PMC_No IN ({ph}) AND i.Subcontractor_Id = %s", args
        )

        # 2. Delete invoices (invoice_holds auto-cascade via ON DELETE CASCADE)
        cursor.execute(
            f"DELETE FROM invoices WHERE PMC_No IN ({ph}) AND Subcontractor_Id = %s", args
        )

        # 3. Delete GST releases
        cursor.execute(
            f"DELETE FROM gst_releases WHERE PMC_No IN ({ph}) AND Contractor_ID = %s", args
        )

        # 4. Delete credit/debit notes
        cursor.execute(
            f"DELETE FROM credit_note WHERE PMC_No IN ({ph}) AND Contractor_Id = %s", args
        )

        # 5. Delete hold release
        cursor.execute(
            f"DELETE FROM hold_release WHERE PMC_No IN ({ph}) AND Contractor_Id = %s", args
        )

        conn.commit()

        LogHelper.log_action(
            "Delete PMC Records",
            f"Deleted PMC records {pmc_nos} for Contractor ID {contractor_id}"
        )

        return jsonify({'success': True, 'message': f'{len(pmc_nos)} PMC record(s) deleted successfully.'})

    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        print("ERROR in execute_delete_pmc:", e)
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if conn:
            try:
                cursor.close(); conn.close()
            except Exception:
                pass
