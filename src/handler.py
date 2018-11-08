import json
from src.email import send_email_via_ses
from src.bucket import check_bucket_encryption


def main(event, context):
    print('*** Enforcement triggered ****')

    bucket_name = event.get('detail', {}).get(
        'requestParameters', {}).get('bucketName', None)

    if bucket_name is None:
        print('Unable to get bucket name!')
        return

    validation, message = check_bucket_encryption(bucket_name)

    if validation is False:
        print('Bucket validation failure for {}. Sending email.'.format(bucket_name))
        text = "Bucket validation failure for {}. Here are the results :\n\n" \
            "{}\n".format(bucket_name, "\n * ".join(message))

        send_email_via_ses(text)
        return

    print('All validations passed for {} S3 bucket.'.format(bucket_name))
    print('******************************')
