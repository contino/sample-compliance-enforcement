resource "aws_s3_bucket" "unencrypted_private_s3_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-unencrypted-private-s3-bucket"
  region = "eu-west-1"
  acl = "private"

  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket" "unencrypted_public-rw_s3_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-unencrypted-public-rw-s3-bucket"
  region = "eu-west-1"
  acl = "public-read-write"

  versioning {
    enabled = true
  }
}

resource "aws_kms_key" "custom_kms_key" {
  description             = "Temporary KMS Key for S3 Encryption"
  deletion_window_in_days = 10
}

resource "aws_s3_bucket" "encrypted_public-read_s3_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-encrypted-public-read-s3-bucket"
  region = "eu-west-1"
  acl = "public-read"

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

resource "aws_s3_bucket" "encrypted_private_read_s3_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-encrypted-private-read-s3-bucket"
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
