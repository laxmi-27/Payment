# import os
# from dotenv import load_dotenv
# from flask_login import UserMixin
# from ldap3 import Server, Connection, ALL
# from ldap3.core.exceptions import LDAPBindError

# # Load .env
# load_dotenv()


# class DefaultCredentials:
#     username = os.getenv("DEFAULT_USERNAME")
#     password = os.getenv("DEFAULT_PASSWORD")


# class LoginLDAP:

#     def __init__(self, request):

#         self.username = request.form.get("username", "").strip()
#         self.password = request.form.get("password", "")

#         self.isDefaultCredentials = False
#         self.isValidLogin = False
#         self.errorMessage = ""

#         # ldap_server = "ldap://localhost:389"
#         ldap_server = "ldap://192.168.0.25:389"
#         ldap_user_dn = f"uid={self.username},ou=users,dc=lcepl,dc=org"

#         # fallback admin login
#         if (
#             self.username == DefaultCredentials.username
#             and self.password == DefaultCredentials.password
#         ):
#             self.isDefaultCredentials = True
#             self.isValidLogin = True
#             return

#         try:

#             server = Server(ldap_server, get_info=ALL)

#             conn = Connection(
#                 server,
#                 user=ldap_user_dn,
#                 password=self.password,
#                 auto_bind=True
#             )

#             if conn.bound:
#                 self.isValidLogin = True

#         except LDAPBindError:
#             self.errorMessage = "Invalid LDAP credentials"

#         except Exception as e:
#             self.errorMessage = str(e)


# class User(UserMixin):

#     def __init__(self, username):
#         self.id = username

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

        # ================= LDAP CONFIG =================
        ldap_server = "ldap://host.docker.internal:389"

        base_dn = "ou=users,dc=lcepl,dc=org"

        ldap_admin_dn = "cn=admin,dc=lcepl,dc=org"
        ldap_admin_password = "Lcepl1950@2026"

        # ================= DEFAULT LOGIN =================
        if (
            self.username == DefaultCredentials.username
            and self.password == DefaultCredentials.password
        ):
            self.isDefaultCredentials = True
            self.isValidLogin = True
            return

        try:

            server = Server(ldap_server, get_info=ALL)

            # ================= ADMIN BIND =================
            admin_conn = Connection(
                server,
                user=ldap_admin_dn,
                password=ldap_admin_password,
                auto_bind=True
            )

            # ================= SEARCH USER =================
            admin_conn.search(
                search_base=base_dn,
                search_filter=f"(|(uid={self.username})(cn={self.username})(mail={self.username}))",
                attributes=["uid", "cn", "mail"]
            )

            if not admin_conn.entries:
                self.errorMessage = "User not found"
                return

            # Actual LDAP DN
            user_dn = admin_conn.entries[0].entry_dn

            print("LDAP User DN:", user_dn)

            # ================= USER AUTH =================
            user_conn = Connection(
                server,
                user=user_dn,
                password=self.password,
                auto_bind=True
            )

            if user_conn.bound:
                self.isValidLogin = True

            user_conn.unbind()
            admin_conn.unbind()

        except LDAPBindError:
            self.errorMessage = "Invalid username or password"

        except Exception as e:
            self.errorMessage = str(e)


class User(UserMixin):

    def __init__(self, username):
        self.id = username

    def get_id(self):
        return self.id

