import boto3
from logging import getLogger, INFO

logger = getLogger()
logger.setLevel(INFO)


class Sns(object):
    def __init__(self, arn):
        self.sns = boto3.client('sns')
        self.arn = arn
        self.message = [
            '*****************************************',
            'Bucket validation failure:',
            'Here are the results :\n\n'
        ]

    def _print_message(self):
        return " \n".join(self.message)

    def add_message(self, message):
        if type(message) is list:
            self.message.extend(message)
        else:
            self.message.append(message)

        logger.info('SNS :: Appending new message to the email: {}'.format(message))
        logger.info('SNS :: Current Message: {}'.format(self._print_message()))

    def publish(self):
        logger.info('SNS :: Publishing SNS Topic : {}'.format(self.arn))
        response = self.sns.publish(
            TargetArn=self.arn,
            Message=self._print_message(),
            Subject='[ALARM] Bucket Validation Notification',
        )
        logger.info('SNS :: Published via id : {}'.format(response))
