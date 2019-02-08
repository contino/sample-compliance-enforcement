resource "aws_ssm_parameter" "whitelist_buckets" {
  name        = "/cf/security/s3-enforce/bucket_exceptions"
  type        = "String"
  value       = "none"
  description = "Comma separated exception buckets"
  overwrite   = true
}