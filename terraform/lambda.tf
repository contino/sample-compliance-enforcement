data "archive_file" "src" {
  type = "zip"
  source_dir = "${path.module}/../src"
  output_path = "${path.module}/${var.function_name}.zip"
}

resource "aws_lambda_permission" "s3-bucket-enforce-function-policy" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.s3-bucket-enforce.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.s3_bucket_create.arn}"
}

resource "aws_lambda_function" "s3-bucket-enforce" {
  filename         = "${path.module}/${var.function_name}.zip"
  function_name    = "${var.function_name}"
  role             = "${aws_iam_role.s3-bucket-enforce-role.arn}"
  handler          = "${var.function_handler}"
  source_code_hash = "${data.archive_file.src.output_base64sha256}"
  runtime          = "python3.7"
  timeout          = 60
  reserved_concurrent_executions = 4
}