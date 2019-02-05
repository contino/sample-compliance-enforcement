output "secure_bucket_name" {
  value = "${aws_s3_bucket.encrypted_s3_bucket.arn}"
}

output "insecure_bucket_name" {
  value = "${aws_s3_bucket.unencrypted_s3_bucket.arn}"
}
