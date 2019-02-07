from boto3 import client
from botocore.exceptions import ClientError
from logging import getLogger, INFO

logger = getLogger()
logger.setLevel(INFO)


class Bucket(object):
    def __init__(self, bucket_name, auto_fix=False):
        self.s3 = client('s3')
        self.s3control = client('s3control')
        self.bucket_name = bucket_name
        self.auto_fix = auto_fix
        self.results = []
        self.messages = []
        self.account_id = client('sts').get_caller_identity().get('Account')
        self.public_access_checks = {
            'BlockPublicAcls': {
                'desc': 'Block new public ACLs and uploading public objects',
                'fail': False,
                'fix': True
            },
            'IgnorePublicAcls': {
                'desc': 'Remove public access granted through public ACLs',
                'fail': False,
                'fix': True
            },
            'BlockPublicPolicy': {
                'desc': 'Block new public bucket policies',
                'fail': False,
                'fix': True
            },
            'RestrictPublicBuckets': {
                'desc': 'Block public and cross-account access if bucket has public policies',
                'fail': False,
                'fix': True
            }
        }


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
        logger.info('Changed bucket encryption for {} to ENABLED. [NOT IMPLEMENTED YET]'.format(self.bucket_name))

    def is_private(self):
        logger.info('Checking if {} S3 Bucket is private.'.format(self.bucket_name))

        _is_public = False
        grantee = self.s3.get_bucket_acl(Bucket=self.bucket_name)['Grants']

        for grant in grantee:
            if 'URI' in grant['Grantee']:
                _is_public = True

        logger.info('Checking Public Access Block for Account {}'.format(self.account_id))
        try:
            public_policy = self.s3control.get_public_access_block(AccountId=self.account_id)['PublicAccessBlockConfiguration']
        except self.s3control.exceptions.NoSuchPublicAccessBlockConfiguration as e:
            if str(e).endswith('The public access block configuration was not found'):
                public_policy = {
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            else:
                raise e

        new_policy = dict()
        for key, value in self.public_access_checks.items():
            if public_policy[key] == value['fail']:
                self._return(False,
                             '{}: {} --> Changed to: {} for account {}'.format(value['desc'],
                                                                               value['fail'],
                                                                               value['fix'],
                                                                               self.account_id))
                _is_public = True
            else:
                self._return(True,
                             '{}: {}'.format(value['desc'], value['fail']))

            if self.auto_fix:
                new_policy[key] = value['fix']

        if _is_public:
            self._return(False, 'Bucket Access for {}: Public'.format(self.bucket_name))

            if self.auto_fix:
                self.set_private()
                self.set_public_policy(new_policy)

            return False

        self._return(True, 'Bucket Access for {}: Private'.format(self.bucket_name))

        return True

    def set_private(self):
        self.s3.put_bucket_acl(
            Bucket=self.bucket_name,
            ACL='private'
        )
        logger.info('Changed bucket access for {} to PRIVATE.'.format(self.bucket_name))

    def set_public_policy(self, policy):
        self.s3control.put_public_access_block(
            PublicAccessBlockConfiguration=policy,
            AccountId=self.account_id
        )
        logger.info('Changed Public Access Block Configuration for Account ID {} for restricted.'.format(self.account_id))
