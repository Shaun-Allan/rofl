import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from config import LDAP_SERVER, BIND_DN, BIND_PASSWORD, BASE_DN


def get_access_group_info(group_cn):
    if not group_cn:
        return {'error': 'Missing group_cn parameter'}

    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, user=BIND_DN, password=BIND_PASSWORD, authentication=NTLM, auto_bind=True)

    try:
        conn.search(
            search_base=BASE_DN,
            search_filter=f'(&(objectClass=group)(cn={group_cn}))',
            search_scope=SUBTREE,
            attributes='*'
        )

        if not conn.entries:
            return {'error': f"Group '{group_cn}' not found"}

        group_entry = conn.entries[0]
        group_attributes = {
            attr if attr != "info" else "owners and authorisers": group_entry[attr].value
            for attr in group_entry.entry_attributes
        }

        # Get member DNs
        members_dns = group_attributes.get('member', [])
        if isinstance(members_dns, str):
            members_dns = [members_dns]

        # Fetch sAMAccountName and mail for each member
        member_details = []
        for member_dn in members_dns:
            conn.search(
                search_base=member_dn,
                search_filter='(objectClass=user)',
                search_scope=SUBTREE,
                attributes=['sAMAccountName', 'mail']
            )
            if conn.entries:
                user_entry = conn.entries[0]
                member_details.append({
                    'racf_id': user_entry.sAMAccountName.value,
                    'mail': user_entry.mail.value
                })

        group_attributes["member"] = member_details

        return group_attributes

    finally:
        conn.unbind()