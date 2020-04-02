locals {
  services = csvdecode(file("${path.module}/services.csv"))
}


resource "nsxt_policy_service" "service_l4port" {
    count = length(local.services)
    description  = "L4 ports service provisioned by Terraform"
    display_name = "${local.services[count.index].name}"

    l4_port_set_entry {
    display_name      = "${local.services[count.index].name}"
    description       = "TCP port 80 entry"
    protocol          = "${local.services[count.index].protocol}"
    destination_ports = [ "${local.services[count.index].portnumber}" ]
    }
}