import requests
from colorama import init
from termcolor import colored
import pyfiglet
import time
import logging
import argparse
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description='This is HELP doc for NsxClient tool')
    parser.add_argument("-i", "--ip", help="IP address of the NSX Manager.")
    parser.add_argument("-u", "--username", help="Username of the NSX Manager.")
    parser.add_argument("-p", "--password", help="Passowrd of the NSX Manager.")
    parser.add_argument("-f", "--filepath", help="mapping file path")
    parser.add_argument("-o", "--operation", help="which operation do you want to run")
    args = parser.parse_args()
    return args


def errors_printer(message):
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file = open('nsx_log.txt', 'w')
    logging.basicConfig(filename='nsx_log.txt', level=logging.INFO)
    log_file.close()

    init()  # colors for prints (Mandatory!!)
    logging.error(f"{date}: {message}")
    print(colored(message, 'red', attrs=['bold']))
    exit_status = 1
    return exit_status


def welcome_printer():
    init()  # colors for prints (Mandatory!!)
    font = pyfiglet.Figlet(font='standard')
    welcome_message = font.renderText("Hello to NsxClient!!")
    print(welcome_message)


def summary_printer(sg_count, st_count):
    # Summery
    time.sleep(2)
    print(colored("\nSUMMARY", 'green', attrs=['bold']))
    print(colored("-----------", 'green', attrs=['bold']))
    print(colored(f"Security group added: {sg_count}\n"
                  f"Security tag added: {st_count}", 'green', attrs=['bold']))


def authorize_operation(nsx_client,args):
    try:
        nsx_client.authorize(args.username, args.password)
    except requests.exceptions.ConnectionError:
        exit_status = errors_printer("You have a connection error to NSX-T manager,"
                                     " please validate you details and try again")
        return exit_status
    except KeyError:
        exit_status = errors_printer("Invalid user and password, Please try again.")
        return exit_status
    except:
        exit_status = errors_printer("usage: nsxclient.py -i [IP] -u [USERNAME] -p [PASSWORD] -f [PATH]")
        return exit_status


def security_operation(nsx_client, args):
    # Security group function
    try:
        welcome_printer()
        nsx_client.add_group_policy(args.filepath)
    except (FileNotFoundError, AttributeError, ValueError) as e:
        exit_status = errors_printer("mapping file not found")
        return exit_status
    # Security tag function
    nsx_client.add_tags()
    summary_printer(nsx_client.sg_count, nsx_client.st_count)


def segment_operation(nsx_client, args):
    try:
        welcome_printer()
        nsx_client.add_segment_policy(args.filepath)
    except TypeError:
        exit_status = errors_printer("json can't deal with int varible, please change vlan object type to str")
        return exit_status


def fw_operation(nsx_client, args):
    try:
        welcome_printer()
        nsx_client.add_fw_section(args.filepath)
    except:
        exit_status = errors_printer("You have an issue with the fw section operation")
        return exit_status
