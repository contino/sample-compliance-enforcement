resource "aws_cloudtrail" "cloudtrail-s3-events" {
  name                          = "cloudtrail-s3-events"
  s3_bucket_name                = "${aws_s3_bucket.account-cloudtrail-events.id}"
  s3_key_prefix                 = "s3-events"
  include_global_service_events = false

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::"]
    }
  }
}

