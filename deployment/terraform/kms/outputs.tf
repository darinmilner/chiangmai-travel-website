# --- Outputs ---
output "kms_key_arns" {
  description = "Map of created KMS key ARNs"
  value = {
    for k, v in aws_kms_key.kms_key : k => v.arn
  }
}

output "kms_alias_names" {
  description = "Map of created KMS alias names"
  value = {
    for k, v in aws_kms_alias.kms_alias : k => v.name
  }
}

output "kms_alias_to_arn" {
  description = "Map of alias names to KMS key ARNs"
  value = {
    for k, v in aws_kms_alias.kms_alias : v.name => aws_kms_key.kms_key[k].arn
  }
}
