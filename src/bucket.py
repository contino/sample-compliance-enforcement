from boto3 import client
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Bucket(object):
    def __init__(self, bucket_name, auto_fix=False):
        self.s3 = client('s3')
        self.bucket_name = bucket_name
        self.auto_fix = auto_fix
        self.results = []
        self.messages = []

    def _return(self, result, message):
        self.messages.extend(message)
        logger.info(message)
        self.results.extend(message)

    def is_encrypted(self):
        logger.info('Checking if {} S3 Bucket is encrypted.'.format(self.bucket_name))
        try:
            self.s3.get_bucket_encryption(Bucket=self.bucket_name)
            self._return(True, 'Bucket Encryption for {}: Enabled'.format(self.bucket_name))
        except ClientError as e:
            if str(e).endswith('The server side encryption configuration was not found'):
                self._return(False, 'Bucket Encryption for {}: Disabled'.format(self.bucket_name))

                if self.auto_fix:
                    self.set_encrypted()

            else:
                print('Exception: {}'.format(e))

    def set_encrypted(self):
        logger.info('Changed bucket encryption for {} to ENABLED. [NOT IMPLEMENTED YET]')

    def is_private(self):
        logger.info('Checking if {} S3 Bucket is private.'.format(self.bucket_name))

        grantee = self.s3.get_bucket_acl(Bucket=self.bucket_name)['Grants'][0]['Grantee']
        if 'URI' in grantee:
            self._return(False, 'Bucket Access for {}: Public'.format(self.bucket_name))

        self._return(True, 'Bucket Access for {}: Private'.format(self.bucket_name))

        if self.auto_fix:
            self.set_private()

    def set_private(self):
        logger.info('Changed bucket access for {} to PRIVATE. [NOT IMPLEMENTED YET]')
