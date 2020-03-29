#!/usr/bin/python

# This Client receive CSV file (mapping.csv) and TXT file (vms.txt)
# The files have to be in the same directory as the script.
# Files should contain the tags and scopes information for the security group.


"""
Example :
env --> prod
app --> ishaiApp
os --> linux
The Client will create a securiy group named "custom-prod-ishaiApp-linux" with 3 tag crateria (env: prod, app: ishaiApp and os: linux)
"""
# Writen by Ishai Shahak at 12/4/19
# Updated by Ishai Shahak at 22/01/20

import requests
import json
import time
import argparse
import pandas
from termcolor import colored
import os
from datetime import datetime
import logging
from operations import errors_printer, welcome_printer, summary_printer,\
    security_operation, segment_operation, authorize_operation, parse_args


requests.packages.urllib3.disable_warnings()  # Ignore from requests module warnings

# make this tool executable from anywhere
project_dir = os.path.dirname(os.path.dirname(__file__))
os.sys.path.append(project_dir)

ADD_GROUP_URI = "api/v1/ns-groups"
CHECK_SG_EXIST = "api/v1/ns-groups"
AUTHORIZATION_URI = "api/session/create"
ADD_TAGS_URI = "api/v1/fabric/virtual-machines?action=update_tags"
ADD_SEGMENT_POLICY_URI = "policy/api/v1/infra"
ADD_SEGMENT_MANAGER_URI = "api/v1/logical-switches"
ADD_FW_SECTION_URI = "api/v1/firewall/sections"
ADD_GROUP_POLICY_URI = "policy/api/v1/infra"

# Logging operation
date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
log_file = open('nsx_log.txt', 'w')
logging.basicConfig(filename='nsx_log.txt', level=logging.INFO)
log_file.close()


class NsxClient:

    def __init__(self, nsx_manager):
        self.session = requests.Session()
        self.nsx_manager = nsx_manager

    def authorize(self, username, password):
        self.username = username
        self.password = password
        url = f"https://{self.nsx_manager}/{AUTHORIZATION_URI}"
        data = {"j_username": self.username, "j_password": self.password}
        response = self.session.request("POST", url, data=data, verify=False)
        self.xsrf_token = response.headers['X-XSRF-TOKEN']
        self.headers = {
            'Content-Type': "application/json",
            'User-Agent': "PostmanRuntime/7.19.0",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': self.nsx_manager,
            'Accept-Encoding': "gzip, deflate",
            'Content-Length': "573",
            'Connection': "keep-alive",
            'cache-control': "no-cache",
            'X-XSRF-TOKEN': self.xsrf_token
        }

###                       REST API                          ###
    # Helpers
    def get_vm_ids(self):
        vm_ids = []
        removed_vms = []
        vms = self.mapping['VM']
        for vm in vms:
            str_vm = str(vm).replace("\n", "")
            url = f"https://{self.nsx_manager}/api/v1/fabric/virtual-machines?display_name={str_vm}"
            payload = {}
            response = self.session.request("GET", url, headers=self.headers, data=json.dumps(payload), verify=False)
            to_json = response.json()
            try:
                results = to_json.get("results")
                vm_id = results[0].get("external_id")
                vm_ids.append(vm_id)
            except IndexError:
                vm_ids.append(0)
                logging.error(f"{date}: VM {str_vm} does not exists")
                print(colored(f"{date}: VM {str_vm} does not exists", 'red', attrs=['bold']))
                continue
        return vm_ids

    def check_sg_exist(self, sg_name):
        sg_names = []
        url = f"https://{self.nsx_manager}/{CHECK_SG_EXIST}"
        payload = {}
        response = self.session.request("GET", url, headers=self.headers, data=json.dumps(payload), verify=False)
        results = response.json().get("results")
        for x in range(0, len(results)-1):
            name = results[x].get("display_name")
            sg_names.append(name)
        if sg_name in sg_names:
            return True
        else:
            return False

    # Network functions
    def add_segment_manager(self, file_path):
        self.segments = pandas.read_csv(file_path, sep=',')

        for x in range(0, len(self.segments)):
            segment_name = self.segments['NAME'][x]
            vlan = str(self.segments['VLAN'][x])
            url = f"https://{self.nsx_manager}/{ADD_SEGMENT_MANAGER_URI}"
            payload ={
              "transport_zone_id": "91045f1d-1e1d-4188-833f-2936dba17030",
              "admin_state": "UP",
              "display_name": f"ls_{segment_name}",
              "vlan": vlan
            }
            response = self.session.request("POST", url, headers=self.headers, data=json.dumps(payload), verify=False)
            if response.status_code == 201:
                print(f"Segment {segment_name} added. ")
            else:
                print(response.text)

    # Security groups & tags functions
    def add_security_group(self, file_path):
        self.mapping = pandas.read_csv(file_path, sep=',')
        self.sg_count = 0
        logging.info(f"{date}: Starting to add security groups...")
        print(colored("Starting to add security groups...", 'green', attrs=['bold']))
        print("-----------")
        time.sleep(2)
        # REST API calls
        url = f"https://{self.nsx_manager}/{ADD_GROUP_URI}"

        for x in range(0, len(self.mapping['VM'])):
            env_tag = self.mapping['ENV'][x]
            app_tag = self.mapping['APP'][x]
            os_tag = self.mapping['OS'][x]
            display_name = f"custom-{env_tag}-{app_tag}-{os_tag}"
            if not self.check_sg_exist(display_name):
                payload = {
                    "display_name": display_name,
                    "membership_criteria": [
                        {
                            "resource_type": "NSGroupComplexExpression",
                            "expressions": [
                                {
                                    "resource_type": "NSGroupTagExpression",
                                    "target_type": "VirtualMachine",
                                    "scope": "env",
                                    "tag": env_tag
                                },
                                {
                                    "resource_type": "NSGroupTagExpression",
                                    "target_type": "VirtualMachine",
                                    "scope": "app",
                                    "tag": app_tag
                                },
                                {
                                    "resource_type": "NSGroupTagExpression",
                                    "target_type": "VirtualMachine",
                                    "scope": "os",
                                    "tag": os_tag
                                }
                            ]
                        }
                    ]
                }
                response = self.session.request("POST", url, data=json.dumps(payload), headers=self.headers, verify=False)

                if str(response.status_code) == "201":
                    self.sg_count = self.sg_count + 1
                    time.sleep(1)
                    logging.info(f"{date}: Security group {display_name} added.")
                    print(f"{date}: Security group {display_name} added.")
                else:
                    print(response.text)
            else:
                logging.warning(f"{date}: Security group {display_name} already exists")
                print(colored(f"{date}: Security group {display_name} already exists", 'yellow', attrs=['bold']))
                continue
        if self.sg_count == len(self.mapping['VM']):
            time.sleep(2)
            print("-----------")
            logging.info(f"{date}: All Security groups added.")
            print(colored(f"\n{date}: All Security groups added.", 'green', attrs=['bold']))

    def add_tags(self):
        self.st_count = 0
        logging.info(f"{date}: Starting to add security tags...")
        print(colored("\nStarting to add security tags...", 'green', attrs=['bold']))
        print("-----------")
        vm_ids = self.get_vm_ids()
        time.sleep(2)

        for x in range(0, len(self.mapping['VM'])):
            if vm_ids[x] is 0:
                continue
            url = f"https://{self.nsx_manager}/{ADD_TAGS_URI}"

            payload = {
                "external_id": f"{vm_ids[x]}",
                "tags": [
                    {"scope": "env", "tag": self.mapping['ENV'][x]},
                    {"scope": "app", "tag": self.mapping['APP'][x]},
                    {"scope": "os", "tag": self.mapping['OS'][x]}
                ]
            }
            response = self.session.request("POST", url, headers=self.headers, data=json.dumps(payload), verify=False)
            if str(response.status_code) == "204":
                self.st_count = self.st_count + 1
                logging.info(f"{date}: Tags added to VM {self.mapping['VM'][x]}")
                print(f"{date}: Tags added to VM {self.mapping['VM'][x]}")
        if self.st_count == len(self.mapping['VM']):
            time.sleep(2)
            print("-----------")
            logging.info(f"{date}: All Tags added.")
            print(colored("All Tags added.", 'green', attrs=['bold']))

        # print(f"Tags added to VM {self.mapping['VM'][x]}")
        # if self.st_count == len(self.mapping['VM']):
        #     time.sleep(2)
        #     print("-----------")
        #     print(colored("All Tags added.", 'green', attrs=['bold']))

    # DFW functions
    def add_fw_section(self, file_path):
        self.sections = pandas.read_csv(file_path, sep=',')
        url = f"https://{self.nsx_manager}/{ADD_FW_SECTION_URI}"

        logging.info(f"{date}: Starting to add fw sections...")
        print(colored("\nStarting to add fw sections...", 'green', attrs=['bold']))

        for x in range(0, len(self.sections['section'])):
            section_name = self.sections['section'][x]
            payload = {"display_name": section_name, "section_type": "LAYER3", "stateful": "true"}
            response = self.session.request("POST", url, headers=self.headers, data=json.dumps(payload), verify=False)
            if str(response.status_code) == "201":
                logging.info(f"{date}: FW section {section_name} added.")
                time.sleep(2)
                print("-----------")
                print(colored(f"FW section {section_name} added.", 'green', attrs=['bold']))
###                                                         ###

###                       Policy API                        ###
    # Helpers
    def get_groups_ids(self):
        groups_ids = []
        url = f"https://{self.nsx_manager}/policy/api/v1/infra/domains/default/groups"
        payload = {}
        response = self.session.request("GET", url, headers=self.headers, data=json.dumps(payload), verify=False)
        results = response.json().get("results")
        for x in range(0, len(results) - 1):
            id = results[x].get("id")
            groups_ids.append(id)
        return groups_ids

    # Security groups & tags functions
    def add_segment_policy(self, file_path):
        segments = pandas.read_csv(file_path, sep=',')
        segments_names = segments["NAME"]
        vlan_id = segments["VLAN"]
        for x in range(0, len(segments_names)):
            url = f"https://{self.nsx_manager}/{ADD_SEGMENT_POLICY_URI}"
            payload ={
              "resource_type": "Infra",
              "children": [
                {
                  "resource_type": "ChildSegment",
                  "Segment": {
                    "resource_type": "Segment",
                    "transport_zone_path": "/infra/sites/default/enforcement-points/"
                                           "default/transport-zones/91045f1d-1e1d-4188-833f-2936dba17030",
                    "id": segments_names[x],
                    "display_name": segments_names[x],
                    "vlan_ids": [str(vlan_id[x])]
                  }
                }
              ]
            }
            response = self.session.request("PATCH", url, headers=self.headers, data=json.dumps(payload), verify=False)
            if response.status_code == 200:
                print(f"Segment {segments_names[x]} added. ")
            else:
                print(response.text)

    def add_group_policy(self, file_path):
        self.mapping = pandas.read_csv(file_path, sep=',')
        self.sg_count = 0
        groups_ids = self.get_groups_ids()
        logging.info(f"{date}: Starting to add security groups...")
        print(colored("Starting to add security groups...", 'green', attrs=['bold']))
        print("-----------")
        time.sleep(2)
        # REST API calls
        url = f"https://{self.nsx_manager}/{ADD_GROUP_POLICY_URI}"

        for x in range(0, len(self.mapping['VM'])):
            env_tag = self.mapping['ENV'][x]
            app_tag = self.mapping['APP'][x]
            os_tag = self.mapping['OS'][x]
            id = f"custom-{env_tag}-{app_tag}-{os_tag}"
            if id not in groups_ids:
                payload = {
                    "resource_type": "Infra",
                    "children": [
                        {
                            "resource_type": "ChildDomain",
                            "Domain": {
                                "id": "default",
                                "resource_type": "Domain",
                                "children": [
                                    {
                                        "resource_type": "ChildGroup",
                                        "marked_for_delete": "false",
                                        "Group": {
                                            "resource_type": "Group",
                                            "id": f"custom-{env_tag}-{app_tag}-{os_tag}",
                                            "expression": [
                                                {
                                                    "member_type": "VirtualMachine",
                                                    "value": f"ENV|{env_tag}",
                                                    "key": "Tag",
                                                    "operator": "EQUALS",
                                                    "resource_type": "Condition"
                                                },
                                                {
                                                    "conjunction_operator": "AND",
                                                    "resource_type": "ConjunctionOperator",
                                                    "_protection": "NOT_PROTECTED"
                                                },
                                                {
                                                    "member_type": "VirtualMachine",
                                                    "value": f"APP|{app_tag}",
                                                    "key": "Tag",
                                                    "operator": "EQUALS",
                                                    "resource_type": "Condition"
                                                },
                                                {
                                                    "conjunction_operator": "AND",
                                                    "resource_type": "ConjunctionOperator",
                                                    "_protection": "NOT_PROTECTED"
                                                },
                                                {
                                                    "member_type": "VirtualMachine",
                                                    "value": f"OS|{os_tag}",
                                                    "key": "Tag",
                                                    "operator": "EQUALS",
                                                    "resource_type": "Condition"
                                                }

                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
                response = self.session.request("PATCH", url, data=json.dumps(payload), headers=self.headers,
                                                verify=False)
                if str(response.status_code) == "200":
                    groups_ids.append(id)
                    self.sg_count = self.sg_count + 1
                    time.sleep(1)
                    logging.info(f"{date}: Security group {id} added.")
                    print(f"{date}: Security group {id} added.")
            else:
                logging.warning(f"{date}: Security group {id} already exists")
                print(colored(f"{date}: Security group {id} already exists", 'yellow', attrs=['bold']))
###                                                         ###

