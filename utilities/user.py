import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import traceback
from ldap3 import Server, Connection, ALL, NTLM
from datetime import datetime
from config import LDAP_SERVER, BIND_DN, BIND_PASSWORD, BASE_DN

def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d-%b-%Y %H:%M")
    return str(dt)

def format_groups(group_dns):
    return [
        {
            "name": dn.split(',')[0].replace("CN=", ""),
            "dn": dn
        }
        for dn in group_dns
    ]


def get_user_info(racf_id):
    if not racf_id:
        return {"error": "Missing 'racf_id' in request"}

    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(
            server,
            user=BIND_DN,
            password=BIND_PASSWORD,
            authentication=NTLM,
            auto_bind=True
        )
        search_filter = f"(sAMAccountName={racf_id})"
        conn.search(BASE_DN, search_filter, attributes=['*'])
        if not conn.entries:
            return {"error": "User not found"}
        user = conn.entries[0].entry_attributes_as_dict
        formatted = {
            "Name": user.get("givenName", [""])[0],
            "Username": user.get("sAMAccountName", [""])[0],
            "Email": user.get("mail", [""])[0],
            "Cost Centre": user.get("rbsCostCentre", [""])[0],
            "Last Logon": format_datetime(user.get("lastLogon", [None])[0]),
            "Account Expires": format_datetime(user.get("accountExpires", [None])[0]),
            "Groups": format_groups(user.get("memberOf", [])),
            "Description": user.get("description", [""])[0],
            "Info": user.get("info", [""])[0]
        }
        return formatted
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}