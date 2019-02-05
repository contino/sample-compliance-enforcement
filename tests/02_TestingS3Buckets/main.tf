resource "aws_s3_bucket" "unencrypted_s3_bucket" {
  bucket = "20190205-unencrypted-s3-bucket"
  region = "eu-west-1"

  versioning {
    enabled = true
  }
}

resource "aws_kms_key" "custom_kms_key" {
  description             = "Temporary KMS Key for S3 Encryption"
  deletion_window_in_days = 10
}

resource "aws_s3_bucket" "encrypted_s3_bucket" {
  bucket = "20190205-encrypted-s3-bucket"
  region = "eu-west-1"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.custom_kms_key.key_id}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
}
