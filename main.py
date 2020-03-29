
from nsxclient import NsxClient
import operations


def main():
    # Get args
    args = operations.parse_args()
    oper = ["security", "segment", "fw"]
    if args.operation not in oper:
        exit_status = operations.errors_printer("please choose valid operation")
        return exit_status
    # Create NsxClient object
    nsx_client = NsxClient(args.ip)
    operations.authorize_operation(nsx_client, args)
    if args.operation == "security":
        operations.security_operation(nsx_client, args)
    if args.operation == "segment":
        operations.segment_operation(nsx_client, args)
    if args.operation == "fw":
        operations.fw_operation(nsx_client, args)


if __name__ == '__main__':
    main()
