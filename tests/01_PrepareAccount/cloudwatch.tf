resource "aws_cloudwatch_event_rule" "s3_bucket_create" {
  name        = "s3-bucket-create-tf"
  description = "Capture S3 Bucket Creations"

  event_pattern = <<PATTERN
{
  "source": [
    "aws.s3"
  ],
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "detail": {
    "eventSource": [
      "s3.amazonaws.com"
    ],
    "eventName": [
      "CreateBucket",
      "DeleteBucketPolicy",
      "PutBucketAcl",
      "PutBucketPublicAccessBlock"
    ]
  }
}
PATTERN
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = "${aws_cloudwatch_event_rule.s3_bucket_create.name}"
  target_id = "${aws_lambda_function.s3-bucket-enforce.function_name}"
  arn       = "${aws_lambda_function.s3-bucket-enforce.arn}"
}

//resource "aws_cloudwatch_log_group" "lambda-log-group" {
//  name = "/dlg/cloudfoundation/security/s3-bucket-enforce-lambda-function"
//}