import requests
import json
import smtplib

requests.packages.urllib3.disable_warnings()  # Ignore from requests module warnings

## CONSTANTS ##

# SEND EMAIL CONSTANTS #
SMTP_SERVER = '10.0.8.50'
SMTP_PORT = 25
SENDER = 'nsxt-events@vmware.com'
RECEIVERS = ['Yadin.Lugassi@cyberark.com']

## CONSTANTS ##

def get_new_vms():
    new_vms = []
    url = "https://10.0.90.150/api/v1/fabric/virtual-machines"
    payload = {}
    headers = {'Content-Type': 'application/json','Authorization': 'Basic YWRtaW46Q3liZXIxMCsxMD0yMCE='}

    response = requests.request("GET", url, headers=headers, data=json.dumps(payload), verify=False)
    to_json = response.json()
    results = to_json.get('results')

    for x in range(0,len(results)):
        vm = results[x]
        if not vm.get('tags'):
            new_vms.append(vm.get('display_name'))
            # with open('new_vms', 'a+') as filehandle:
            #     filehandle.write('%s\n' % f"{vm.get('display_name')}")

    return new_vms


def send_email(message, smtp_server, smtp_port, sender, receivers):
    try:
       smtpObj = smtplib.SMTP(smtp_server, smtp_port)
       smtpObj.sendmail(sender, receivers, message)
       print("Successfully sent email")

    except:
       print("Error: unable to send email")


def message_builder():
    message = "Please see new vms without NSX-T security tags: \n\n--------"
    new_vms = get_new_vms()

    for vm in new_vms:
        message = message + "\n" + vm
        message = message + "\n-----------\n\nPlease tag those vms in order to get the relevant security policy for those vms"

    return message

def main():
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    sender = SENDER
    receivers = RECEIVERS
    message = message_builder()

    send_email(message, smtp_server, smtp_port, sender, receivers)

if __name__ == '__main__':
    main()