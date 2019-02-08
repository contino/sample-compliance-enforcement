# Assume role for Lambda Function
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "s3-bucket-enforce-role" {
  name               = "${var.function_name}"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role.json}"
}

# IAM Policy Required for Logging
data "aws_iam_policy_document" "execution" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
    ]

    resources = [
      "arn:${data.aws_partition.current.partition}:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "arn:${data.aws_partition.current.partition}:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.function_name}:*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:Get*",
      "s3:PutBucketAcl",
      "s3:PutBucketPublicAccessBlock",
      "s3:PutAccountPublicAccessBlock"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "SNS:Publish"
    ]

    resources = [
      "${aws_sns_topic.aws_config_sns_topic.arn}"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "ssm:DescribeParameters",
      "ssm:Get*"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameter"
    ]

    resources = [
      "arn:aws:ssm:::parameter/cf/security/s3-enforce/*"
    ]
  }
}

resource "aws_iam_policy" "execution" {
  name   = "${var.function_name}-execution"
  policy = "${data.aws_iam_policy_document.execution.json}"
}

resource "aws_iam_policy_attachment" "execution" {
  name       = "${var.function_name}-execution"
  roles      = ["${aws_iam_role.s3-bucket-enforce-role.name}"]
  policy_arn = "${aws_iam_policy.execution.arn}"
}
