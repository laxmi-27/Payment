# routes/gst_release_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from model.gst_release import GSTRelease
from model.Log import LogHelper

gst_release_bp = Blueprint('gst_release_bp', __name__)
gst_service = GSTRelease()

# ---------------- ADD GST RELEASE ----------------
@gst_release_bp.route('/add_gst_release', methods=['GET', 'POST'])
@login_required
def add_gst_release():
    if request.method == 'POST':
        gst_service.AddGSTRelease(request)
        LogHelper.log_action("Add GST Release", "User added GST release")
        flash(gst_service.resultMessage, 'success' if gst_service.isSuccess else 'error')
        return redirect(url_for('gst_release_bp.add_gst_release'))

    gst_releases = gst_service.GetAllGSTReleases()
    return render_template('add_gst_release.html', gst_releases=gst_releases)

# ---------------- EDIT GST RELEASE ----------------
@gst_release_bp.route('/edit_gst_release/<int:gst_release_id>', methods=['GET', 'POST'])
@login_required
def edit_gst_release(gst_release_id):
    gst_data = gst_service.GetGSTReleaseByID(gst_release_id)
    if not gst_data:
        return "GST Release not found", 404

    if request.method == 'POST':
        gst_service.EditGSTRelease(request, gst_release_id)
        LogHelper.log_action("Edit GST Release", "User edited GST release")
        flash(gst_service.resultMessage, 'success' if gst_service.isSuccess else 'error')
        return redirect(url_for('gst_release_bp.add_gst_release'))

    return render_template('edit_gst_release.html', gst_release_data=gst_data)

# ---------------- DELETE GST RELEASE ----------------
@gst_release_bp.route('/delete_gst_release/<int:gst_release_id>', methods=['GET', 'POST'])
@login_required
def delete_gst_release(gst_release_id):
    gst_service.DeleteGSTRelease(gst_release_id)
    LogHelper.log_action("Delete GST Release", "User deleted GST release")
    flash(gst_service.resultMessage, 'success' if gst_service.isSuccess else 'error')
    return redirect(url_for('gst_release_bp.add_gst_release'))