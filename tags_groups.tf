// This terraform create a security groups and security tags base on CSV files that he got
// The first CSV should be tags mapping
// The second CSV should be virtual machines list
// NSX-T version - 2.5
// Terraform version - v0.12.24
// NSX-T provider version - v2.0.0


provider "nsxt" {
  host                     = var.nsx_manager
  username                 = var.nsx_username
  password                 = var.nsx_password
  allow_unverified_ssl     = true
  max_retries              = 10
  retry_min_delay          = 500
  retry_max_delay          = 5000
  retry_on_status_codes    = [429]
}
locals {
  tags = csvdecode(file("${path.module}/tags.csv"))
  vms = csvdecode(file("${path.module}/vms.csv"))
}

data "nsxt_policy_vm" "nsxt_vm1" {
  count = length(local.vms)
  display_name = "${local.vms[count.index].VM}"
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
    display_name = "custom-${local.tags[count.index].ENV}-${local.tags[count.index].APP}-${local.tags[count.index].OWNER}"
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

