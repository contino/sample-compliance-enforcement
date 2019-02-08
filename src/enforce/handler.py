from enforce.sns import Sns
from enforce.bucket import Bucket
from logging import getLogger, INFO
import boto3

logger = getLogger()
logger.setLevel(INFO)


def main(event, context):
    print('*** Enforcement triggered ****')

    bucket_name = event.get('detail', {}).get(
        'requestParameters', {}).get('bucketName', None)

    if bucket_name is None:
        print('Unable to get bucket name!')
        return

    bucket = Bucket(bucket_name, auto_fix=True)
    # bucket.is_encrypted()
    bucket.is_private()

    logger.info('Validation Results: {}'.format(bucket.results))

    if False in bucket.results:
        logger.info('Bucket validation failure for {}. Triggering SNS.'.format(bucket_name))

        # This is for PoC purposes only, ARN needs to be discovered within the region, but it will also require
        # more IAM permissions to do that for now.
        account_id = boto3.client('sts').get_caller_identity().get('Account')
        sns = Sns(arn='arn:aws:sns:eu-west-1:{}:account-activity-notifications'.format(account_id))
        sns.add_message(bucket.messages)
        sns.publish()
        return False

    logger.info('All validations passed for {} S3 bucket.'.format(bucket_name))
    logger.info('******************************')
