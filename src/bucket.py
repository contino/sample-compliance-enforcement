from boto3 import client
from botocore.exceptions import ClientError


def check_bucket_encryption(bucket_name):
    print('Validating S3 Bucket: {}'.format(bucket_name))
    s3 = client('s3')
    result = True
    messages = []
    try:
        s3.get_bucket_encryption(Bucket=bucket_name)
        print('Bucket Encryption: Enabled')
        messages.append('Bucket Encryption: Enabled')
    except ClientError as e:
        if str(e).endswith('The server side encryption configuration was not found'):
            print('Bucket Encryption: Disabled')
            messages.append('Bucket Encryption: Disabled')
            result = False
        else:
            print('Exception: {}'.format(e))

    return (result, messages)
