import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from ldap3 import Server, Connection, ALL, SIMPLE, SUBTREE
from config import (
    LDAP_SERVER, 
    BIND_DN,
    BIND_PASSWORD,
    BASE_DN,
    PROXIES,
    ATLASSIAN_USERNAME,
    ATLASSIAN_PASSWORD,
    ATLASSIAN_BASE_URL,
    JIRA_ENDPOINT,
    CONFLUENCE_ENDPOINT,
    GITLAB_BASE_URL,
    DEV_GITLAB_ID,
    DEV_GITLAB_ROLE
)
from requests.auth import HTTPBasicAuth
import requests
import re

def get_access_group_info(group_cn):
    if not group_cn:
        return {'error': 'Missing group_cn parameter'}

    # Initialize LDAP server and connection using SIMPLE authentication
    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, user=BIND_DN, password=BIND_PASSWORD, authentication=SIMPLE, auto_bind=True)

    try:
        # Search for the group
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

        
        

        
        
        
#Confluence Groups
def getting_groups(space_name):
    group_names_list = []
    jira_url = "{}/wiki/api/v2/spaces/{}/permissions/?jql=&limit=250".format(ATLASSIAN_BASE_URL,space_name)

    auth = HTTPBasicAuth(ATLASSIAN_USERNAME, ATLASSIAN_PASSWORD)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("GET", jira_url, auth=auth, headers=headers, proxies=PROXIES, verify=False)

    if response.status_code == 200:
        data = response.json()
        group_ids_set = set()
        for permission in data.get("results",[]):
            group_type = permission.get("principal",{}).get("type")
            group_id = permission.get("principal",{}).get("id")
            if group_id not in group_ids_set and group_type == "group" :
                group_ids_set.add(group_id)
        group_ids_list = list(group_ids_set)    
        global_group_ids = ["bc9794bc-8b57-45ee-863b-9fa588ea758c" ,"862fe571-cd61-46e8-85a6-3e19a6d6b50d", "983c76e0-02a1-4152-a53d-78c3df613766","0e234c1c-2ae3-44de-a885-1abfc3075cdd","0b543b1a-2e98-4d85-bdfd-64dc0cce5639"]

        my_group_ids = [ids for ids in group_ids_list if ids not in global_group_ids]
        for group_id in my_group_ids:
            group_name_url = "{}/wiki/rest/api/group/by-id?id={}".format(ATLASSIAN_BASE_URL,group_id)
            response = requests.request("GET", group_name_url, auth=auth, headers=headers, proxies=PROXIES, verify=False)
            if response.status_code == 200:
                data = response.json()
                group_name = data["name"]
                group_names_list.append(group_name)
                print(group_names_list)
            else:
                print(response)
                print(f"Error getting group names:{response.json()}")
    else:
        group_names_list = None
    return group_names_list

def get_space_id(space_name):
    group_names_list = []
    jira_url = "{}{}/{}".format(ATLASSIAN_BASE_URL,CONFLUENCE_ENDPOINT,space_name)

    auth = HTTPBasicAuth(ATLASSIAN_USERNAME, ATLASSIAN_PASSWORD)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("GET", jira_url, auth=auth, headers=headers, proxies=PROXIES, verify=False)
    # print(response.text)
    if response.status_code == 200:
        data = response.json()
        space_id = data["id"]
    elif response.status_code == 404:
        space_id =None
    else:
        space_id =None
    return space_id

def get_confluence_space_role_groups(space_key: str) -> dict:
    """
    Retrieve role groups for one or more Confluence spaces based on space keys.

    Args:
        space_key (str): Comma-separated space keys (e.g., "FIN, HR")

    Returns:
        dict: A dictionary mapping each space key to its role groups or an error message.
    """
    if not space_key:
        return {"Error": "No space key provided"}

    user_space_input = space_key.split(',')
    space_identifier = [item.strip().upper() for item in user_space_input]

    role_groups_dict = {}
    if space_identifier:
        for space_name in space_identifier:
            space_id = get_space_id(space_name)
            if space_id:
                get_role_groups_list = getting_groups(space_id)
                key = f"Result_{space_name}"
                value = get_role_groups_list
            else:
                key = f"Result_{space_name}"
                value = f"There is no space or the user does not have permission to view the space {space_name}."
            role_groups_dict[key] = value
    else:
        role_groups_dict["Error"] = "No space keys found"

    return role_groups_dict


#Jira Groups
def remove_special_charaters(text):
    special_characters_pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(special_characters_pattern, '', text)

def get_project_keys_and_names():  
    jira_url = f"{ATLASSIAN_BASE_URL}{JIRA_ENDPOINT}"
    project_keys = []
    project_names =[]
    project_ids= []
    auth = HTTPBasicAuth(ATLASSIAN_USERNAME, ATLASSIAN_PASSWORD)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("GET", jira_url, auth=auth, headers=headers, proxies=PROXIES)
    if response.status_code == 200:
        result = response.json()
        for issue in result:
            if "archived" in issue:
                trueorfalse = issue["archived"]
                if trueorfalse == "True":
                    break
            else:
                project_key = issue["key"].upper()
                project_name = issue["name"].strip().upper()
                encoded_project_name = remove_special_charaters(project_name)
                project_id = issue["id"]
                project_keys.append(project_key)
                project_names.append(encoded_project_name)
                project_ids.append(project_id)
    return project_keys, project_names, project_ids

def get_role_groups(project_keys, project_names, project_ids, project_identifier):
    if project_identifier in project_keys or project_identifier in project_ids:
        project_name = project_identifier

    elif project_identifier in project_names:
        pos = project_names.index(project_identifier)
        project_name = project_keys[pos]
    else:
        group_names_list = f"No Project found with identifier {project_identifier}"
        return group_names_list

    group_names = []
    jira_url = "{}{}/{}/permissionscheme?expand=permissions".format(ATLASSIAN_BASE_URL, JIRA_ENDPOINT, project_name)
    print(jira_url)

    auth = HTTPBasicAuth(ATLASSIAN_USERNAME, ATLASSIAN_PASSWORD)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("GET", jira_url, auth=auth, headers=headers, proxies=PROXIES, verify=False)
    print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        group_names_set = set()
        for permission in data.get("permissions",[]):
            group_names = permission.get("holder",{}).get("parameter")
            if group_names not in group_names_set and group_names != "10100" and group_names != None:
                group_names_set.add(group_names)
        group_names_list = list(group_names_set)    
    else:
        group_names_list = f"Error:{response.json()['errorMessages']}"
    return group_names_list    

def get_jira_project_role_groups(project_key: str) -> dict:
    """
    Retrieve role groups for one or more Jira projects based on project keys.

    Args:
        project_key (str): Comma-separated project keys (e.g., "ABC, DEF")

    Returns:
        dict: A dictionary mapping each project key to its role groups or an error message.
    """
    if not project_key:
        return {"Error": "No project key provided"}

    project_keys, project_names, project_ids = get_project_keys_and_names()
    user_project_input = project_key.split(',')
    project_identifier = [item.strip().upper() for item in user_project_input]

    role_groups_dict = {}
    if project_identifier:
        for project_name in project_identifier:
            encoded_project_name = remove_special_charaters(project_name)
            get_role_groups_list = get_role_groups(
                project_keys, project_names, project_ids, encoded_project_name
            )
            key = f"Result_{project_name}"
            value = get_role_groups_list if get_role_groups_list else "Error"
            role_groups_dict[key] = value
    else:
        role_groups_dict["Error"] = "No project keys found"

    return role_groups_dict


#Gitlab Groups
def get_gitlab_group_id_based_on_bl(group_bl: str) -> str:
    """
    Fetches the GitLab group ID for a given group full path (group_bl).
    """
    
    headers = {"Authorization": f"Bearer {DEV_GITLAB_ID}"}
    page = 1
    per_page = 100

    while True:
        url = f"{GITLAB_BASE_URL}/api/v4/groups?per_page={per_page}&page={page}"
        print(url)
        response = requests.get(url, headers=headers)
        print(response.status_code) 
        groups = response.json()
        print("ghropus", groups)
        

        if not groups:
            break
        for group in groups:    
            print("hey: ", group)
            if group.get('full_path') == group_bl:
                return group.get('id', "")

        page += 1

    raise ValueError(f"Could not find group ID for {group_bl}")


def get_gitlab_role_groups(group_id: str) -> list:
    """
    Fetches the SAML role groups for a given GitLab group ID.
    """
    url = f"{GITLAB_BASE_URL}/api/v4/groups/{group_id}/saml_group_links"
    headers = {"private-token": DEV_GITLAB_ROLE}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()