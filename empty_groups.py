import requests
import json


requests.packages.urllib3.disable_warnings()  # Ignore from requests module warnings

payload = {}
headers = {'Content-Type': 'application/json', 'Authorization': 'Basic YWRtaW46Q3liZXIxMCsxMD0yMCE='}

def get_groups_ids():
    groups_ids = []

    url = f"https://10.0.90.150/policy/api/v1/infra/domains/default/groups"

    response = requests.request("GET", url, headers=headers, data=json.dumps(payload), verify=False)

    to_json = response.json()
    results = to_json.get('results')
    for x in range(0, len(results)):
        group_id = results[x].get('id')
        groups_ids.append(group_id)
    return groups_ids

def get_empty_groups(groups_ids):
    empty_groups = []
    for group_id in groups_ids:
        url = f"https://10.0.90.150/policy/api/v1/infra/domains/default/groups/{group_id}/members/virtual-machines"
        try:
            response = requests.request("GET", url, headers=headers, data=json.dumps(payload), verify=False)
            to_json = response.json()
            results = to_json.get('results')
            if (len(results) < 1):
                print(f"{group_id} is empty")
                empty_groups.append(group_id)
        except:
            continue
    return empty_groups

def delete_empty_groups(groups_ids):
    for group in groups_ids:
        if "custom" in group or "pl" in group:
            url = f"https://10.0.90.150/policy/api/v1/infra/domains/default/groups/{group}"
            response = requests.request("DELETE", url, headers=headers, data=json.dumps(payload), verify=False)
            print(f"group {group} deleted because it was empty group")
        else:
            continue

groups_ids = get_groups_ids()
empty_groups = get_empty_groups(groups_ids)
delete_empty_groups(empty_groups)
