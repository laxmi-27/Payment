from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from model.District import District
from model.State import State

district_bp = Blueprint('district', __name__)
district = District()

# ------- District page --------
@district_bp.route('/add_district', methods=['GET', 'POST'])
@login_required
def add_district():
    # district = District()

    if request.method == 'POST':
        district.AddDistrict(request=request)
        return district.resultMessage

    state = State()
    states = state.GetAllStates(request=request)

    districtdata = district.GetAllDistricts(request=request)

    return render_template(
        'add_district.html',
        districtdata=districtdata,
        states=states
    )

# ------- District check --------
@district_bp.route('/check_district', methods=['POST'])
@login_required
def check_district():

    # district = District()

    return district.CheckDistrict(request=request)

# ------- District delete by district id --------
@district_bp.route('/delete_district/<int:district_id>')
@login_required
def delete_district(district_id):

    # district = District()

    district.DeleteDistrict(request=request, district_id=district_id)

    if not district.isSuccess:
        return district.resultMessage
    else:
        return redirect(url_for('district.add_district'))


# ------- District update by district id --------
@district_bp.route('/edit_district/<int:district_id>', methods=['GET', 'POST'])
@login_required
def edit_district(district_id):

    # district = District()
    state = State()

    if request.method == 'POST':

        district.EditDistrict(request=request, district_id=district_id)

        if district.isSuccess:
            flash("District updated successfully!", "success")
            return redirect(url_for('district.add_district'))
        else:
            flash(district.resultMessage, "error")

    districtdata = district.GetDistrictByID(request=request, district_id=district_id)

    if not districtdata:
        flash("District not found", "error")
        return redirect(url_for('district.add_district'))

    states = state.GetAllStates(request=request)

    return render_template(
        'edit_district.html',
        districtdata=districtdata,
        states=states
    )