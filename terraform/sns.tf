resource "aws_sns_topic" "aws_config_sns_topic" {
  name      = "account-activity-notifications"

  provisioner "local-exec" {
    command = "aws sns subscribe --topic-arn ${self.arn} --region ${var.region} --protocol email --notification-endpoint ${var.email-group}"
  }
}