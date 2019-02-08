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

Since current Lambda function checks for `Private/Public` data,
upon `terraform apply` you should have 2 different emails about the buckets listed above. 
You should NOT have any email regarding to the private buckets.

The code is also capable to check for encryption via `is_encrypted()` method, but there is no 
remediation planned for now, since it may require some custom KMS stuff.

## Remediations
The code will remediate automatically the problematic buckets + the account if Public access is open.

## Exception Bucket

The code will also have a look on `/cf/security/s3-enforce/bucket_exceptions` path in SSM Parameter Store
if there are any buckets are listed there (as comma separated). The reason having this is to have some buckets
within the exception list where they are ignored on any remediations.

When there is at least 1 exception within this path, all ACCOUNT-WIDE Public Block Access remediations
will be skipped.


# Why there are some python libs within the `src/` folder ?

That is because AWS Lambda in eu-west-1 does not have the latest `boto3` library that can access to
`s3control` client. That's why we are embedding those within the lambda package. When AWS updates their
Lambda stacks, then this can be removed.