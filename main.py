# main.py
from flask import Flask, render_template
from flask_login import LoginManager, login_required
from model.Auth import User

# Import Blueprints / Controllers
from controllers.auth_controller import auth_bp
from controllers.log_controller import log_bp
from controllers.state_controller import state_bp
from controllers.district_controller import district_bp
from controllers.block_controller import block_bp
from controllers.village_controller import village_bp
from controllers.invoice_controller import invoice_bp
from controllers.subcontractor_controller import subcontractor_bp
from controllers.payment_controller import payment_bp
from controllers.gst_release_controller import gst_release_bp
from controllers.excel_upload_controller import excel_bp 
from controllers.report_controller import report_bp
from controllers.pmc_report_controller import pmc_report_bp

from controllers.hold_types_controller import hold_bp
from controllers.master_data_controller import master_data_bp
from controllers.balance_to_debit_controller import balance_to_debit_bp
from controllers.credit_debit_note_controller import cdn_bp
from controllers.creditNote import credit_bp
from controllers.hold_release_controller import hr_bp
from controllers.delete_pmc_controller import del_pmc_bp
from dotenv import load_dotenv
import os

# ---------------- Initialize App ----------------
app = Flask(__name__)

load_dotenv()
Secret_Key = os.getenv("SECRET_KEY")
app.secret_key = Secret_Key

# ---------------- Login Manager ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ---------------- Home Route ----------------
@app.route('/')
@login_required
def index():
    return render_template("index.html")

# ---------------- Changelog Route ----------------
@app.route('/changelog')
@login_required
def changelog():
    return render_template("changelog.html")

# ---------------- Register Blueprints ----------------

app.register_blueprint(auth_bp)
app.register_blueprint(log_bp)
app.register_blueprint(state_bp)
app.register_blueprint(district_bp)
app.register_blueprint(block_bp)
app.register_blueprint(village_bp)
app.register_blueprint(invoice_bp)
app.register_blueprint(subcontractor_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(gst_release_bp)
app.register_blueprint(excel_bp) 
app.register_blueprint(report_bp)
app.register_blueprint(pmc_report_bp)
app.register_blueprint(hold_bp)
app.register_blueprint(master_data_bp)
app.register_blueprint(balance_to_debit_bp)
app.register_blueprint(cdn_bp)
app.register_blueprint(credit_bp)
app.register_blueprint(hr_bp)
app.register_blueprint(del_pmc_bp)

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5020, debug=True)



