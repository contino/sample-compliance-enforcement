# Sample Compliance Enforcement

CHANGE ME



This repository includes a sample compliance enforcement by using AWS Lambda. 

## Story

```cucumber
Given I have an S3 Bucket Created
When the encryption is not set
And the bucket is public
Then notify me via email
And remediate the bucket
```

## Background

The code written in Python 3. It runs compliance tests ( currently just S3 Encryption check ) against given S3 bucket and then sends an email if the validation fails using AWS SES. 

## Requirements & Installation

No requirements - except a valid AWS role that have enough privileges to apply terraform - is needed.

Within the `tests/` directory, get into `tests/01_PrepareAccount` and simply run ;

```bash
$ terraform init
$ terraform plan
$ terraform apply
```

You will receive a email from Amazon SNS to confirm the topic subscription. Just click the confirmation link.

Viola, all is there.

# Running the DEMO

Within the `tests/` directory, there is also `tests/02_TestingS3Buckets` path.
This path includes a very simple terraform hcl files creating 4 different buckets with ;

1. Unencrypted + Private
2. Unencrypted + Public
3. Encrypted + Private
4. Encrypted + Public

Since current Lambda function checks for `Private/Public` and `Encrypted/Unencrypted` data,
upon `terraform apply` you should have 3 different emails about the buckets listed above. 
You should NOT have any email regarding to the 3rd bucket ( Encrypted + Private ).
