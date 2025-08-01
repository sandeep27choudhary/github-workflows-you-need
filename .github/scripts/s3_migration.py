#!/usr/bin/env python3
"""
S3 Bucket Migration Script
Migrates S3 buckets between AWS accounts while preserving ACLs and metadata.
"""

import os
import sys
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_logs/s3_migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class S3Migrator:
    def __init__(self):
        self.source_bucket = os.getenv('SOURCE_BUCKET')
        self.target_bucket = os.getenv('TARGET_BUCKET')
        self.source_profile = os.getenv('SOURCE_PROFILE')
        self.target_profile = os.getenv('TARGET_PROFILE')
        self.migrate_all = os.getenv('MIGRATE_ALL', 'false').lower() == 'true'
        self.preserve_acl = os.getenv('PRESERVE_ACL', 'true').lower() == 'true'
        self.preserve_metadata = os.getenv('PRESERVE_METADATA', 'true').lower() == 'true'
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        
        # Create logs directory
        os.makedirs('migration_logs', exist_ok=True)
        
        # Initialize AWS clients
        self.source_s3 = self._get_s3_client(self.source_profile)
        self.target_s3 = self._get_s3_client(self.target_profile)
        
    def _get_s3_client(self, profile_name):
        """Get S3 client with specified profile."""
        try:
            session = boto3.Session(profile_name=profile_name)
            return session.client('s3')
        except NoCredentialsError:
            logger.error(f"Could not load credentials for profile: {profile_name}")
            sys.exit(1)
    
    def list_buckets(self, s3_client):
        """List all buckets in the account."""
        try:
            response = s3_client.list_buckets()
            return [bucket['Name'] for bucket in response['Buckets']]
        except ClientError as e:
            logger.error(f"Error listing buckets: {e}")
            return []
    
    def list_objects(self, bucket_name, s3_client, prefix=''):
        """List all objects in a bucket with pagination."""
        objects = []
        paginator = s3_client.get_paginator('list_objects_v2')
        
        try:
            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    objects.extend(page['Contents'])
        except ClientError as e:
            logger.error(f"Error listing objects in bucket {bucket_name}: {e}")
        
        return objects
    
    def get_object_metadata(self, bucket_name, key, s3_client):
        """Get object metadata including ACL and user metadata."""
        metadata = {}
        
        try:
            # Get object metadata
            response = s3_client.head_object(Bucket=bucket_name, Key=key)
            metadata.update({
                'ContentType': response.get('ContentType'),
                'ContentEncoding': response.get('ContentEncoding'),
                'ContentLanguage': response.get('ContentLanguage'),
                'CacheControl': response.get('CacheControl'),
                'ContentDisposition': response.get('ContentDisposition'),
                'Expires': response.get('Expires'),
                'Metadata': response.get('Metadata', {})
            })
            
            # Get ACL if preserving ACLs
            if self.preserve_acl:
                try:
                    acl_response = s3_client.get_object_acl(Bucket=bucket_name, Key=key)
                    metadata['ACL'] = acl_response.get('Grants', [])
                except ClientError as e:
                    logger.warning(f"Could not get ACL for {key}: {e}")
                    
        except ClientError as e:
            logger.error(f"Error getting metadata for {key}: {e}")
        
        return metadata
    
    def copy_object(self, source_bucket, target_bucket, key, metadata):
        """Copy object from source to target bucket."""
        try:
            # Prepare copy parameters
            copy_source = {'Bucket': source_bucket, 'Key': key}
            extra_args = {}
            
            # Add metadata if preserving
            if self.preserve_metadata and metadata.get('Metadata'):
                extra_args['Metadata'] = metadata['Metadata']
                extra_args['MetadataDirective'] = 'REPLACE'
            
            # Add other metadata fields
            for field in ['ContentType', 'ContentEncoding', 'ContentLanguage', 
                         'CacheControl', 'ContentDisposition', 'Expires']:
                if metadata.get(field):
                    extra_args[field] = metadata[field]
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would copy: {source_bucket}/{key} -> {target_bucket}/{key}")
                return True
            
            # Perform the copy
            self.target_s3.copy_object(
                CopySource=copy_source,
                Bucket=target_bucket,
                Key=key,
                **extra_args
            )
            
            # Apply ACL if preserving
            if self.preserve_acl and metadata.get('ACL'):
                try:
                    grants = metadata['ACL']
                    acl = {'Grants': grants}
                    self.target_s3.put_object_acl(
                        Bucket=target_bucket,
                        Key=key,
                        AccessControlPolicy=acl
                    )
                except ClientError as e:
                    logger.warning(f"Could not apply ACL for {key}: {e}")
            
            logger.info(f"Copied: {source_bucket}/{key} -> {target_bucket}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error copying {key}: {e}")
            return False
    
    def migrate_bucket(self, source_bucket, target_bucket):
        """Migrate a single bucket."""
        logger.info(f"Starting migration: {source_bucket} -> {target_bucket}")
        
        # Check if target bucket exists, create if not
        try:
            self.target_s3.head_bucket(Bucket=target_bucket)
            logger.info(f"Target bucket {target_bucket} already exists")
        except ClientError:
            if not self.dry_run:
                try:
                    self.target_s3.create_bucket(Bucket=target_bucket)
                    logger.info(f"Created target bucket: {target_bucket}")
                except ClientError as e:
                    logger.error(f"Error creating target bucket {target_bucket}: {e}")
                    return False
            else:
                logger.info(f"[DRY RUN] Would create bucket: {target_bucket}")
        
        # List all objects in source bucket
        objects = self.list_objects(source_bucket, self.source_s3)
        logger.info(f"Found {len(objects)} objects in source bucket")
        
        # Copy objects
        successful_copies = 0
        failed_copies = 0
        
        for obj in objects:
            key = obj['Key']
            
            # Get object metadata
            metadata = self.get_object_metadata(source_bucket, key, self.source_s3)
            
            # Copy object
            if self.copy_object(source_bucket, target_bucket, key, metadata):
                successful_copies += 1
            else:
                failed_copies += 1
        
        logger.info(f"Migration completed: {successful_copies} successful, {failed_copies} failed")
        return failed_copies == 0
    
    def run(self):
        """Main migration process."""
        logger.info("Starting S3 migration process")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info(f"Preserve ACL: {self.preserve_acl}")
        logger.info(f"Preserve metadata: {self.preserve_metadata}")
        
        if self.migrate_all:
            # Migrate all buckets
            source_buckets = self.list_buckets(self.source_s3)
            logger.info(f"Found {len(source_buckets)} buckets in source account")
            
            for bucket in source_buckets:
                target_bucket = f"{bucket}-migrated"
                self.migrate_bucket(bucket, target_bucket)
        else:
            # Migrate specific bucket
            if not self.source_bucket or not self.target_bucket:
                logger.error("Source and target bucket names are required")
                sys.exit(1)
            
            self.migrate_bucket(self.source_bucket, self.target_bucket)
        
        logger.info("S3 migration process completed")

if __name__ == "__main__":
    migrator = S3Migrator()
    migrator.run() 