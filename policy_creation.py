import requests
import pandas
from time import sleep
import json

requests.packages.urllib3.disable_warnings()  # Ignore from requests module warnings
policy = pandas.read_csv("policy.csv", sep=',')
url = "https://172.16.20.103/policy/api/v1/infra/"

for x in range(0, len(policy)):

    group = policy["group"][x]
    src = policy["src"][x]
    dst = policy["dst"][x]
    service = policy["service"][x]
    seq = f"0{x+1}"

    payload = {
    "resource_type": "Infra",
    "children": [
        {
        "resource_type": "ChildDomain",
        "marked_for_delete": False,
        "Domain": {
            "id": "default",
            "resource_type": "Domain",
            "marked_for_delete": False,
            "children": [
            {
                "resource_type": "ChildSecurityPolicy",
                "marked_for_delete": "false",
                "SecurityPolicy": {
                "id": f"{group}",
                "scope": [f"/infra/domains/default/groups/{group}"],
                "resource_type": "SecurityPolicy",
                "display_name": f"{group}-policy",
                "description": f"Security Policy for {group} group, deployed by Python",
                "rules": [
                    {
                    "resource_type": "Rule",
                    "id": f"{group}-rule-{seq}",
                    "description": f"{group}-rule-{seq}",
                    "display_name": f"{dst}-{service}",
                    "sequence_number": 50,
                    "source_groups": [
                        f"/infra/domains/default/groups/{src}"
                    ],
                    "destination_groups": [
                        f"/infra/domains/default/groups/{dst}"
                    ],
                    "services": [
                        f"/infra/services/{service}"
                    ],
                    "profiles": [
                        "ANY"
                    ],
                    "action": "ALLOW"
                    }
                ]
                }
            }
            ]
        }
        }
        ]
    }
    headers = {
    'Authorization': 'Basic YWRtaW46QnBvdnRtZzEhQnBvdnRtZzEh',
    'Content-Type': 'application/json',
    'Cookie': 'JSESSIONID=7FC87B693943BF78B0AEDA1A6F536C2C'
    }
    response = requests.request("PATCH", url, headers=headers, data=json.dumps(payload), verify=False)
    print(response.status_code)