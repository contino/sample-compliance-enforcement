import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# TO-DO: Use SNS instead

def send_email_via_ses(message):
    sender = "Emre Erkunt <emre@contino.io>"
    recipient = "Emre Erkunt <emre@contino.io>"
    # configuration_set = "ConfigSet"
    aws_region = "eu-west-1"
    subject = "WARNING: Non-Encrypted S3 Bucket Alert"
    charset = "UTF-8"
    body_plain_text = message

    client = boto3.client('ses', region_name=aws_region)

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body_plain_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
            # ConfigurationSetName=configuration_set,
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID: {}".format(response['MessageId']))
        print("From   : {}".format(sender))
        print("To     : {}".format(recipient))
        print("Subject: {}".format(subject))
        print("Message: {}".format(message))
