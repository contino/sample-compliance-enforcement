from boto3 import client
from botocore.exceptions import ClientError
from logging import getLogger
from enforce.ssm import SSMParameterStore

logger = getLogger()


class Bucket(object):
    def __init__(self, bucket_name, auto_fix=False):
        self.s3 = client('s3')
        self.s3control = client('s3control')
        self.bucket_name = bucket_name
        self.bucket_exceptions = self._get_bucket_exceptions()
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
        self.auto_fix = True
        self.account_fix = True
        self.is_available_for_auto_fix(auto_fix)

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
                # self._return(False, '  -> Changed bucket encryption to ENABLED for {}\n'.format(self.bucket_name))
                self.set_encrypted()
                return False
            else:
                print('Exception: {}'.format(e))
                return False

    def set_encrypted(self):
        if self.auto_fix:
            logger.info('Changed bucket encryption for {} to ENABLED. [NOT IMPLEMENTED YET]'.format(self.bucket_name))

    def is_private(self):
        logger.info('is_private :: Invoked')
        logger.info('Checking if {} S3 Bucket is private.'.format(self.bucket_name))

        _is_public = False
        grantee = self.s3.get_bucket_acl(Bucket=self.bucket_name)['Grants']
        logger.info('is_private :: Grantee: {}'.format(grantee))

        for grant in grantee:
            if 'URI' in grant['Grantee']:
                logger.info('is_private :: Found URI within {}'.format(grant['Grantee']))
                _is_public = True

        # Don't even dive into any Account-wide public block access if there are any exceptions
        if not self.bucket_exceptions:
            _is_public, new_policy = self.compare_public_policies(self.check_public_access(account_id=self.account_id),
                                                                  self.public_access_checks,
                                                                  _is_public)

        if _is_public:
            logger.info('is_private :: _is_public:  {}'.format(_is_public))
            self._return(False, 'Bucket Access for {}: Public'.format(self.bucket_name))
            self.set_private()

            if not self.bucket_exceptions:
                self.set_public_policy(new_policy)

            return False

        self._return(True, 'Bucket Access for {}: Private'.format(self.bucket_name))

        return True

    def check_public_access(self, account_id):
        logger.info('check_public_access :: Invoked')
        logger.info('check_public_access :: Checking Public Access Block for Account {}'.format(self.account_id))
        try:
            public_policy = self.s3control.get_public_access_block(AccountId=account_id)['PublicAccessBlockConfiguration']
        except self.s3control.exceptions.NoSuchPublicAccessBlockConfiguration as e:
            if str(e).endswith('The public access block configuration was not found'):
                logger.info('check_public_access :: Public Access Block does not exist')
                public_policy = {
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            else:
                raise e

        logger.info('check_public_access :: Will apply : {}'.format(public_policy))
        return public_policy

    def compare_public_policies(self, public_policy, enforcement_policy, check_result):
        logger.info('check_public_policies :: Comparing public policies.')
        logger.info('check_public_policies :: Public Policy: '.format(public_policy))
        logger.info('check_public_policies :: Enforcement Policy: '.format(enforcement_policy))
        logger.info('check_public_policies :: Previous Result: '.format(check_result))
        new_policy = dict()
        for key, value in enforcement_policy.items():
            if public_policy[key] == value['fail']:
                self._return(False, '{}: {}'.format(value['desc'], value['fail']))
                check_result = True
                logger.info('check_public_policies :: Found a match: {}:{}'.format(key, public_policy[key]))

                if self.auto_fix:
                    logger.info('check_public_policies :: Initiating fix: {}:{}->{}'.format(key,
                                                                                             public_policy[key],
                                                                                             value['fix']))
                    self._return(None, '  -> Changed to: {} for account {}'.format(value['fix'], self.account_id))
                    new_policy[key] = value['fix']
            else:
                self._return(True, '{}: {}'.format(value['desc'], value['fail']))

        return check_result, new_policy

    def set_private(self):
        logger.info('set_private :: Invoked')
        if self.auto_fix:
            logger.info('set_private :: Fixing the bucket acl from public to private')
            self.s3.put_bucket_acl(
                Bucket=self.bucket_name,
                ACL='private'
            )
            self._return(None, '  -> Changed bucket public access to RESTRICTED for {}\n'.format(self.bucket_name))
            logger.info('Changed bucket access for {} to PRIVATE.'.format(self.bucket_name))

    def set_public_policy(self, policy):
        logger.info('set_public_policy :: Invoked')
        if self.account_fix:
            logger.info('set_public_policy :: Fixing the account public access block policy')
            self.s3control.put_public_access_block(
                PublicAccessBlockConfiguration=policy,
                AccountId=self.account_id
            )
            logger.info('Changed Public Access Block Configuration for Account '
                        'ID {} for restricted.'.format(self.account_id))
            self._return(None, '\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
                               '** WARNING: \nPublic Access Block for your Account is enabled.\n'
                               'Any attempt to create a public bucket will fail. If your terraform apply stucks,'
                               'this is the reason.\n'
                               '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')

    def is_available_for_auto_fix(self, auto_fix):
        logger.info('is_available_for_auto_fix :: Invoked')
        if auto_fix is False:
            logger.info('is_available_for_auto_fix :: Skipping auto-fix')
            self.auto_fix = False
            self.account_fix = False
            return False

        # If there are no exceptions defined within the account
        if not self.bucket_exceptions:
            logger.info('is_available_for_auto_fix :: No exceptions defined.')
            logger.error('No exceptions list defined for this account!')
            return True

        # If our bucket is within the exceptions, apply bucket exception
        if self.bucket_name in self.bucket_exceptions:
            logger.info('is_available_for_auto_fix :: Found {} bucket within exceptions.'.format(self.bucket_name))
            logger.info('Bucket {} is found in the exception list. '
                        'Skipping all auto_fixing checks for it.'.format(self.bucket_name))
            self._return(None, '\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
                               '** Due to having {} bucket within the exceptions list, '
                               'no remediation has occurred. **'
                               '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n'.format(self.bucket_name))
            self.auto_fix = False

        # If there are any bucket exceptions defined then disable account-wide exception
        if self.bucket_exceptions:
            logger.info('is_available_for_auto_fix :: There is at least a bucket within the exceptions.')
            logger.info('There are {} buckets defined in your account exceptions list.'
                        'Bucket enforcement will be applied but '
                        'there will be no account-wide enforcement.'.format(len(self.bucket_exceptions)))
            self._return(None, '\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
                               '** Due to having {} bucket defined within the exceptions list, '
                               'no account-wide remediation has occurred. **\n'
                               '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n'.format(len(self.bucket_exceptions)))
            self.account_fix = False

        logger.info('Can not find {} bucket in the exception list. '
                    'Enforcing remediation on it.'.format(self.bucket_name))

    def _get_bucket_exceptions(self):
        ssm_ps = SSMParameterStore(ssm_client=client('ssm'), prefix='/cf/security/s3-enforce/')
        if 'bucket_exceptions' not in ssm_ps.keys():
            return ['none']

        exceptions = [a.strip() for a in ssm_ps['bucket_exceptions'].split(',')]
        del exceptions[0]

        logger.info('_get_bucket_exceptions :: Exceptions: {}'.format(exceptions))

        return exceptions
