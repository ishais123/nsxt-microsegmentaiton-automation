// This terraform IaC create a segments from CSV file
// NSX-T version - 2.5
// Terraform version - v0.12.24
// NSX-T provider version - v2.0.0

locals{
  overlay_tz = "tz-overlay"
  vlan_tz = "tz-vlan"
  segments = csvdecode(file("${path.module}/segments.csv"))
}

data "nsxt_policy_transport_zone" "overlay_transport_zone" {
  display_name = local.overlay_tz
}

data "nsxt_policy_transport_zone" "vlan_transport_zone" {
  transport_type = "VLAN_BACKED"
  display_name = local.vlan_tz
}

resource "nsxt_policy_tier1_gateway" "tier1_gw" {
  count = length(local.segments)
  description               = "Tier-1 provisioned by Terraform"
  display_name              = "tf-Tier1-${local.segments[count.index].segment}"
  default_rule_logging      = "false"
  enable_firewall           = "true"
  route_advertisement_types = ["TIER1_STATIC_ROUTES", "TIER1_CONNECTED"]
  pool_allocation           = "ROUTING"
}

resource "nsxt_policy_segment" "segment1" {
    count = length(local.segments)
    display_name      = "tf-${local.segments[count.index].segment}"
    description       = "Terraform provisioned Segment"
    transport_zone_path = data.nsxt_policy_transport_zone.overlay_transport_zone.path
    connectivity_path = nsxt_policy_tier1_gateway.tier1_gw[count.index].path
    subnet   {
        cidr = "${local.segments[count.index].subnet}"
      }
}

