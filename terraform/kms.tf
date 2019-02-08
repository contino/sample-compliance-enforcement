resource "aws_kms_key" "cloudtrail-bucket-key" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
}