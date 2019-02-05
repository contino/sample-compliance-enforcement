import json
from src.email import send_email_via_ses
from src.bucket import Bucket

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(event, context):
    print('*** Enforcement triggered ****')

    bucket_name = event.get('detail', {}).get(
        'requestParameters', {}).get('bucketName', None)

    if bucket_name is None:
        print('Unable to get bucket name!')
        return

    bucket = Bucket(bucket_name)
    bucket.is_encrypted()
    bucket.is_private()

    if False in bucket.results:
        logger.info('Bucket validation failure for {}. Triggering SNS.'.format(bucket_name))
        text = "Bucket validation failure for {}. Here are the results :\n\n" \
            "{}\n".format(bucket_name, "\n * ".join(bucket.messages))

        send_email_via_ses(text)
        return

    logger.info('All validations passed for {} S3 bucket.'.format(bucket_name))
    logger.info('******************************')
