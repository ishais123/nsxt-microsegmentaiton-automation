// This terraform create a security groups and security tags base on CSV files that he got
// The first CSV should be tags mapping
// The second CSV should be virtual machines list
// NSX-T version - 2.5
// Terraform version - v0.12.24
// NSX-T provider version - v2.0.0

locals {
  tags = csvdecode(file("${path.module}/tags.csv"))
  vms = csvdecode(file("${path.module}/vms.csv"))
}

data "nsxt_policy_vm" "nsxt_vm1" {
  count = length(local.vms)
  display_name = can("${local.vms[count.index].VM}")
}

resource "nsxt_policy_vm_tags" "vm1_tags" {
  count = length(local.vms)
  instance_id = "${data.nsxt_policy_vm.nsxt_vm1[count.index].id}"

  dynamic "tag" {
    for_each = local.tags[count.index]
    content {
    scope = tag.key
    tag = tag.value
    }
  }
}

resource "nsxt_policy_group" "group1" {
    count = length(local.tags)
    display_name = "custom-${local.tags[count.index].ENV}-${local.tags[count.index].APP}-${local.tags[count.index].OS}"
    description  = "Terraform provisioned Group"

    criteria {
        dynamic "condition" {
          for_each = local.tags[count.index]
          content{
            key         = "Tag"
            member_type = "VirtualMachine"
            operator    = "EQUALS"
            value       = "${condition.key}|${condition.value}"
          }
        }
    }
}

output "security_groups"{
  value = nsxt_policy_group.group1[0].display_name
}

