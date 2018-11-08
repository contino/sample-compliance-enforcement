# Sample Compliance Enforcement

This repository includes a sample compliance enforcement by using AWS Lambda. 

## Story

```
GIVEN I have an S3 Bucket Created
When the encryption is not set
Then notify me via email
```

## Background

The code written in Python 3. It runs compliance tests ( currently just S3 Encryption check ) against given S3 bucket and then sends an email if the validation fails using AWS SES. 

## Requirements & Installation

In order to run this Lamba, you need several stuff on AWS and on your computer ;

### 1. Serverless Framework

As Contino, we recommend to use [Serverless Framework](https://www.serverless.com) for all operations on Serverless code. This requires an account on www.serverless.com in order to create this application. Thus go register, if you haven't.

### 2. AWS Account

Of course you need an AWS Account. Ask on #tech-support Slack channel if you need a playground account. You also need to configure some stuff on your AWS Account.

1. Enable CloudTrail, otherwise you won't see `s3:CreateBucket` events on CloudWatch.
2. The serverless function will create an IAM role already, modify that role to have the following ;

```
{
    "Effect": "Allow",
    "Action": [
        "s3:GetEncryptionConfiguration",
        "s3:DeleteBucket"
    ],
    "Resource": "*"
},
{
    "Effect": "Allow",
    "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
    ],
    "Resource": "arn:aws:ses:eu-west-1:765554814255:identity/<your_email_in_SES>"
}
```
3. Validate an email address in AWS SES in order to send emails as sender.

These all should be done in Terraform, but unfortunately I had to do this in ~2 hours without knowing how Serverless was working. Thus any PR is appreciated. :)

### 3. Run Serverless

It is quite trivial to run it. Load your AWS keys on a console and then run ;

```
# serverless login
# serverless deploy -v
```

Viola.

# Running the DEMO

The `tests` directorey has some terraform files that you can run for DEMOing to a customer. It creates two S3 Buckets, one encrypted, one not encrypted.

When you make everything correctly. Whenever you `apply` this terraform, you should have an email ( that you validated through AWS SES ) one of the buckets ( the one that is unencrypted ) is failing the validation.

# Further thoughts

It is quite easy to add more checks like if the bucket `acl` is private, if the `kms` key that is used is a custom one, etc. These can be added as more checks in the `bucket.py` and a list of validation could be send to the user.

Also, better to have a generic class for these checking and have a code style like in inspec, for e.g.

```python
bucket = Obj(bucket_name)

with send_email('....')
    bucket.is_encrypted()
    bucket.is_private()
    bucket.is_awesome()
    ....
```
