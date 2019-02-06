data "aws_iam_policy_document" "account-cloudtrail-events-bucket-policy-document" {
  statement {
    sid = "AWSCloudTrailAclCheck"
    effect = "Allow"
    principals {
      identifiers = [ "cloudtrail.amazonaws.com" ]
      type = "Service"
    }
    actions = [
      "s3:GetBucketAcl",
    ]

    resources = [
      "arn:aws:s3:::account-cloudtrail-events-${data.aws_caller_identity.current.account_id}"
    ]
  }

  statement {
    sid = "AWSCloudTrailWrite"
    effect = "Allow"
    principals {
      identifiers = [ "cloudtrail.amazonaws.com" ]
      type = "Service"
    }
    actions = [
      "s3:PutObject",
    ]

    resources = [
      "arn:aws:s3:::account-cloudtrail-events-${data.aws_caller_identity.current.account_id}/*"
    ]

    condition {
      test = "StringEquals"
      values = ["bucket-owner-full-control"]
      variable = "s3:x-amz-acl"
    }
  }
}

resource "aws_s3_bucket" "account-cloudtrail-events" {
  bucket        = "account-cloudtrail-events-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
  acl = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.cloudtrail-bucket-key.arn}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_policy" "account-cloudtrail-events-bucket-policy" {
  bucket = "${aws_s3_bucket.account-cloudtrail-events.id}"
  policy = "${data.aws_iam_policy_document.account-cloudtrail-events-bucket-policy-document.json}"
}