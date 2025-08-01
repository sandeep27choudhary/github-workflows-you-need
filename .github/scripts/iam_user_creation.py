#!/usr/bin/env python3
"""
IAM User Creation Script
Creates IAM users with minimal permissions and enforces security best practices.
"""

import os
import sys
import boto3
import logging
import json
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iam_logs/iam_user_creation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class IAMUserCreator:
    def __init__(self):
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.access_level = os.getenv('ACCESS_LEVEL', 'readonly')
        self.force_password_change = os.getenv('FORCE_PASSWORD_CHANGE', 'true').lower() == 'true'
        self.create_access_keys = os.getenv('CREATE_ACCESS_KEYS', 'false').lower() == 'true'
        self.groups = os.getenv('GROUPS', '').split(',') if os.getenv('GROUPS') else []
        
        # Create logs directory
        os.makedirs('iam_logs', exist_ok=True)
        
        # Initialize AWS clients
        self.iam = boto3.client('iam')
        
        # Define access level policies
        self.policies = {
            'readonly': {
                'name': 'ReadOnlyAccess',
                'arn': 'arn:aws:iam::aws:policy/ReadOnlyAccess',
                'description': 'Provides read-only access to AWS services and resources'
            },
            'developer': {
                'name': 'DeveloperAccess',
                'arn': 'arn:aws:iam::aws:policy/PowerUserAccess',
                'description': 'Provides developer access with limited administrative permissions'
            },
            'admin': {
                'name': 'AdministratorAccess',
                'arn': 'arn:aws:iam::aws:policy/AdministratorAccess',
                'description': 'Provides full access to AWS services and resources'
            }
        }
    
    def check_password_policy(self):
        """Check if password meets AWS requirements."""
        if len(self.password) < 8:
            logger.error("Password must be at least 8 characters long")
            return False
        
        # Check for complexity requirements
        has_upper = any(c.isupper() for c in self.password)
        has_lower = any(c.islower() for c in self.password)
        has_digit = any(c.isdigit() for c in self.password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in self.password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            logger.error("Password must contain uppercase, lowercase, digit, and special character")
            return False
        
        return True
    
    def create_user(self):
        """Create the IAM user."""
        try:
            # Check if user already exists
            try:
                self.iam.get_user(UserName=self.username)
                logger.warning(f"User {self.username} already exists")
                return True
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchEntity':
                    pass  # User doesn't exist, continue with creation
                else:
                    raise
            
            # Create user
            response = self.iam.create_user(UserName=self.username)
            logger.info(f"Created IAM user: {self.username}")
            
            # Set initial password
            self.iam.create_login_profile(
                UserName=self.username,
                Password=self.password,
                PasswordResetRequired=self.force_password_change
            )
            logger.info(f"Set initial password for user: {self.username}")
            
            if self.force_password_change:
                logger.info("User will be required to change password on first login")
            
            return True
            
        except ClientError as e:
            logger.error(f"Error creating user {self.username}: {e}")
            return False
    
    def attach_policy(self):
        """Attach the appropriate policy based on access level."""
        try:
            policy = self.policies.get(self.access_level)
            if not policy:
                logger.error(f"Invalid access level: {self.access_level}")
                return False
            
            self.iam.attach_user_policy(
                UserName=self.username,
                PolicyArn=policy['arn']
            )
            logger.info(f"Attached {policy['name']} policy to user {self.username}")
            return True
            
        except ClientError as e:
            logger.error(f"Error attaching policy to user {self.username}: {e}")
            return False
    
    def add_user_to_groups(self):
        """Add user to specified groups."""
        if not self.groups:
            return True
        
        for group in self.groups:
            group = group.strip()
            if not group:
                continue
            
            try:
                # Check if group exists
                try:
                    self.iam.get_group(GroupName=group)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchEntity':
                        logger.warning(f"Group {group} does not exist, skipping")
                        continue
                    else:
                        raise
                
                # Add user to group
                self.iam.add_user_to_group(
                    GroupName=group,
                    UserName=self.username
                )
                logger.info(f"Added user {self.username} to group {group}")
                
            except ClientError as e:
                logger.error(f"Error adding user {self.username} to group {group}: {e}")
    
    def create_access_keys(self):
        """Create access keys for the user if requested."""
        if not self.create_access_keys:
            return True
        
        try:
            response = self.iam.create_access_key(UserName=self.username)
            access_key = response['AccessKey']
            
            logger.info(f"Created access key for user {self.username}")
            logger.info(f"Access Key ID: {access_key['AccessKeyId']}")
            logger.warning(f"Secret Access Key: {access_key['SecretAccessKey']}")
            logger.warning("IMPORTANT: Store the Secret Access Key securely and do not commit it to version control!")
            
            # Save access key details to file (for secure retrieval)
            key_info = {
                'username': self.username,
                'access_key_id': access_key['AccessKeyId'],
                'secret_access_key': access_key['SecretAccessKey'],
                'created_at': access_key['CreateDate'].isoformat()
            }
            
            with open(f'iam_logs/{self.username}_access_keys.json', 'w') as f:
                json.dump(key_info, f, indent=2)
            
            return True
            
        except ClientError as e:
            logger.error(f"Error creating access keys for user {self.username}: {e}")
            return False
    
    def apply_security_policies(self):
        """Apply additional security policies to the user."""
        try:
            # Enable MFA requirement
            self.iam.put_user_policy(
                UserName=self.username,
                PolicyName='MFAPolicy',
                PolicyDocument=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "DenyAllExceptListedIfNoMFA",
                            "Effect": "Deny",
                            "NotAction": [
                                "iam:CreateVirtualMFADevice",
                                "iam:EnableMFADevice",
                                "iam:GetUser",
                                "iam:ListMFADevices",
                                "iam:ListVirtualMFADevices",
                                "iam:ResyncMFADevice",
                                "sts:GetSessionToken"
                            ],
                            "Resource": "*",
                            "Condition": {
                                "BoolIfExists": {
                                    "aws:MultiFactorAuthPresent": "false"
                                }
                            }
                        }
                    ]
                })
            )
            logger.info(f"Applied MFA policy to user {self.username}")
            
            return True
            
        except ClientError as e:
            logger.error(f"Error applying security policies to user {self.username}: {e}")
            return False
    
    def run(self):
        """Main user creation process."""
        logger.info("Starting IAM user creation process")
        logger.info(f"Username: {self.username}")
        logger.info(f"Access level: {self.access_level}")
        logger.info(f"Force password change: {self.force_password_change}")
        logger.info(f"Create access keys: {self.create_access_keys}")
        logger.info(f"Groups: {self.groups}")
        
        # Validate inputs
        if not self.username or not self.password:
            logger.error("Username and password are required")
            sys.exit(1)
        
        if not self.check_password_policy():
            sys.exit(1)
        
        # Create user
        if not self.create_user():
            sys.exit(1)
        
        # Attach policy
        if not self.attach_policy():
            sys.exit(1)
        
        # Add to groups
        self.add_user_to_groups()
        
        # Create access keys if requested
        if not self.create_access_keys():
            sys.exit(1)
        
        # Apply security policies
        self.apply_security_policies()
        
        logger.info(f"IAM user {self.username} created successfully")
        logger.info("User creation process completed")

if __name__ == "__main__":
    creator = IAMUserCreator()
    creator.run() 