data "nsxt_policy_service" "http" {
  display_name = "HTTP"
}
data "nsxt_policy_service" "icmp" {
  display_name = "ICMP ALL"
}

data "nsxt_policy_service" "bootps" {
  display_name = "bootps"
}

# variable "groups" {
#   description = "Create IAM users with these names"
#   type        = "map"
#   default     = {
#         name1: "custom-avivapp-app-linux"
#         name2: "custom-avivapp-db-linux"
#     }
# }

locals {
  # We've included this inline to create a complete example, but in practice
  # this is more likely to be loaded from a file using the "file" function.
#   csv_data = <<-CSV
#     src,dst
#     custom-avivapp-app-linux,custom-avivapp-db-linux
#     custom-avivapp-db-linux,custom-avivapp-app-linux
#   CSV
  rules = csvdecode(file("${path.module}/test.csv"))
}

resource "nsxt_policy_security_policy" "policy1" {
    # for_each = { for inst in local.rules : inst.src => src } #for_each = var.groups
    count = length(local.rules)
    display_name = local.rules[count.index].src #var.groups[count.index]
    description  = "Terraform provisioned Security Policy"
    category     = "Application"
    locked       = false
    stateful     = true
    tcp_strict   = false
    scope        = ["/infra/domains/default/groups/${local.rules[count.index].src}"]
    rule {
    display_name       = "allow_icmp"
    source_groups      = ["/infra/domains/default/groups/${local.rules[count.index].src}"]
    destination_groups = ["/infra/domains/default/groups/${local.rules[count.index].dst}"]
    action             = "ALLOW"
    services           = [data.nsxt_policy_service.bootps.path]
    logged             = true
    }
}
