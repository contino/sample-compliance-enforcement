variable "region" {
  default = "eu-west-1"
}

variable "email-group" {
  description     = "E-mail address for suspicious account activity and event-driven security notifications"
  type = "string"
}

variable "function_name" {
  default = "s3-bucket-enforcement"
}

variable "function_handler" {
  default = "enforce.handler.main"
}

