from boto3 import client
from botocore.exceptions import ClientError
from logging import getLogger, INFO

logger = getLogger()
logger.setLevel(INFO)


class Bucket(object):
    def __init__(self, bucket_name, auto_fix=False):
        self.s3 = client('s3')
        self.bucket_name = bucket_name
        self.auto_fix = auto_fix
        self.results = []
        self.messages = []

    def _return(self, result, message):
        self.messages.append(message)
        logger.info(message)
        self.results.append(result)
        return result

    def is_encrypted(self):
        logger.info('Checking if {} S3 Bucket is encrypted.'.format(self.bucket_name))
        try:
            self.s3.get_bucket_encryption(Bucket=self.bucket_name)
            self._return(True, 'Bucket Encryption for {}: Enabled'.format(self.bucket_name))
            return True
        except ClientError as e:
            if str(e).endswith('The server side encryption configuration was not found'):
                self._return(False, 'Bucket Encryption for {}: Disabled'.format(self.bucket_name))

                if self.auto_fix:
                    self.set_encrypted()

                return False
            else:
                print('Exception: {}'.format(e))
                return False

    def set_encrypted(self):
        logger.info('Changed bucket encryption for {} to ENABLED. [NOT IMPLEMENTED YET]')

    def is_private(self):
        logger.info('Checking if {} S3 Bucket is private.'.format(self.bucket_name))

        private = False
        grantee = self.s3.get_bucket_acl(Bucket=self.bucket_name)['Grants']

        for grant in grantee:
            if 'URI' in grant['Grantee']:
                private = True
                print('Private Grantee: {}'.format(private))

        if private:
            self._return(False, 'Bucket Access for {}: Public'.format(self.bucket_name))
            return False

        self._return(True, 'Bucket Access for {}: Private'.format(self.bucket_name))

        if self.auto_fix:
            self.set_private()

        return True

    def set_private(self):
        logger.info('Changed bucket access for {} to PRIVATE. [NOT IMPLEMENTED YET]')
