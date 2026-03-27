import os
from dotenv import load_dotenv
from flask_login import UserMixin
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError

# Load .env
load_dotenv()


class DefaultCredentials:
    username = os.getenv("DEFAULT_USERNAME")
    password = os.getenv("DEFAULT_PASSWORD")


class LoginLDAP:

    def __init__(self, request):

        self.username = request.form.get("username", "").strip()
        self.password = request.form.get("password", "")

        self.isDefaultCredentials = False
        self.isValidLogin = False
        self.errorMessage = ""

        ldap_server = "ldap://localhost:389"
        ldap_user_dn = f"uid={self.username},ou=users,dc=lcepl,dc=org"

        # fallback admin login
        if (
            self.username == DefaultCredentials.username
            and self.password == DefaultCredentials.password
        ):
            self.isDefaultCredentials = True
            self.isValidLogin = True
            return

        try:

            server = Server(ldap_server, get_info=ALL)

            conn = Connection(
                server,
                user=ldap_user_dn,
                password=self.password,
                auto_bind=True
            )

            if conn.bound:
                self.isValidLogin = True

        except LDAPBindError:
            self.errorMessage = "Invalid LDAP credentials"

        except Exception as e:
            self.errorMessage = str(e)


class User(UserMixin):

    def __init__(self, username):
        self.id = username