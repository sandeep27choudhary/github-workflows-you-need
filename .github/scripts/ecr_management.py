#!/usr/bin/env python3
"""
ECR Repository Management Script
Manages Amazon ECR repositories including creation, updates, cleanup, and listing.
"""

import os
import sys
import json
import boto3
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ecr_logs/ecr_management.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ECRManager:
    def __init__(self):
        self.action = os.getenv('ACTION')
        self.repository_name = os.getenv('REPOSITORY_NAME')
        self.image_tag_mutability = os.getenv('IMAGE_TAG_MUTABILITY', 'MUTABLE')
        self.scan_on_push = os.getenv('SCAN_ON_PUSH', 'true').lower() == 'true'
        self.encryption_type = os.getenv('ENCRYPTION_TYPE', 'AES256')
        self.kms_key = os.getenv('KMS_KEY')
        self.lifecycle_policy = os.getenv('LIFECYCLE_POLICY', '{}')
        self.retention_days = int(os.getenv('RETENTION_DAYS', '30'))
        
        # Create logs directory
        os.makedirs('ecr_logs', exist_ok=True)
        
        # Initialize AWS clients
        self.ecr = boto3.client('ecr')
        
    def create_repository(self):
        """Create a new ECR repository."""
        try:
            # Prepare encryption configuration
            encryption_config = {
                'encryptionType': self.encryption_type
            }
            
            if self.encryption_type == 'KMS' and self.kms_key:
                encryption_config['kmsKey'] = self.kms_key
            
            # Create repository
            response = self.ecr.create_repository(
                repositoryName=self.repository_name,
                imageTagMutability=self.image_tag_mutability,
                imageScanningConfiguration={
                    'scanOnPush': self.scan_on_push
                },
                encryptionConfiguration=encryption_config
            )
            
            logger.info(f"✅ Created ECR repository: {self.repository_name}")
            logger.info(f"Repository URI: {response['repository']['repositoryUri']}")
            
            # Apply lifecycle policy if provided
            if self.lifecycle_policy and self.lifecycle_policy != '{}':
                self.apply_lifecycle_policy()
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
                logger.warning(f"Repository {self.repository_name} already exists")
                return True
            else:
                logger.error(f"Error creating repository: {e}")
                return False
    
    def update_repository(self):
        """Update an existing ECR repository."""
        try:
            # Update image scanning configuration
            self.ecr.put_image_scanning_configuration(
                repositoryName=self.repository_name,
                imageScanningConfiguration={
                    'scanOnPush': self.scan_on_push
                }
            )
            
            # Update image tag mutability
            self.ecr.put_image_tag_mutability(
                repositoryName=self.repository_name,
                imageTagMutability=self.image_tag_mutability
            )
            
            logger.info(f"✅ Updated ECR repository: {self.repository_name}")
            
            # Apply lifecycle policy if provided
            if self.lifecycle_policy and self.lifecycle_policy != '{}':
                self.apply_lifecycle_policy()
            
            return True
            
        except ClientError as e:
            logger.error(f"Error updating repository: {e}")
            return False
    
    def apply_lifecycle_policy(self):
        """Apply lifecycle policy to the repository."""
        try:
            policy_text = json.dumps(json.loads(self.lifecycle_policy))
            
            self.ecr.put_lifecycle_policy(
                repositoryName=self.repository_name,
                lifecyclePolicyText=policy_text
            )
            
            logger.info(f"✅ Applied lifecycle policy to repository: {self.repository_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Error applying lifecycle policy: {e}")
            return False
    
    def cleanup_old_images(self):
        """Clean up old images from the repository."""
        try:
            # Get all images in the repository
            paginator = self.ecr.get_paginator('describe_images')
            images = []
            
            for page in paginator.paginate(repositoryName=self.repository_name):
                images.extend(page['imageDetails'])
            
            if not images:
                logger.info(f"No images found in repository: {self.repository_name}")
                return True
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Find images to delete
            images_to_delete = []
            for image in images:
                if 'imagePushedAt' in image:
                    pushed_at = image['imagePushedAt'].replace(tzinfo=None)
                    if pushed_at < cutoff_date:
                        images_to_delete.append(image)
            
            if not images_to_delete:
                logger.info(f"No images older than {self.retention_days} days found")
                return True
            
            # Delete old images
            image_identifiers = []
            for image in images_to_delete:
                identifier = {}
                if 'imageDigest' in image:
                    identifier['imageDigest'] = image['imageDigest']
                if 'imageTag' in image:
                    identifier['imageTag'] = image['imageTag']
                
                if identifier:
                    image_identifiers.append(identifier)
            
            if image_identifiers:
                response = self.ecr.batch_delete_image(
                    repositoryName=self.repository_name,
                    imageIds=image_identifiers
                )
                
                logger.info(f"✅ Deleted {len(image_identifiers)} old images from repository: {self.repository_name}")
                
                if 'imageIds' in response:
                    logger.info(f"Successfully deleted: {len(response['imageIds'])} images")
                
                if 'failures' in response and response['failures']:
                    logger.warning(f"Failed to delete: {len(response['failures'])} images")
                    for failure in response['failures']:
                        logger.warning(f"  - {failure}")
            
            return True
            
        except ClientError as e:
            logger.error(f"Error cleaning up images: {e}")
            return False
    
    def list_repositories(self):
        """List all ECR repositories."""
        try:
            paginator = self.ecr.get_paginator('describe_repositories')
            
            logger.info("📋 ECR Repositories:")
            logger.info("-" * 80)
            
            for page in paginator.paginate():
                for repo in page['repositories']:
                    logger.info(f"Name: {repo['repositoryName']}")
                    logger.info(f"URI: {repo['repositoryUri']}")
                    logger.info(f"Created: {repo['createdAt']}")
                    logger.info(f"Tag Mutability: {repo['imageTagMutability']}")
                    
                    # Get image count
                    try:
                        images = self.ecr.describe_images(repositoryName=repo['repositoryName'])
                        image_count = len(images['imageDetails'])
                        logger.info(f"Images: {image_count}")
                    except:
                        logger.info("Images: Unable to retrieve count")
                    
                    logger.info("-" * 80)
            
            return True
            
        except ClientError as e:
            logger.error(f"Error listing repositories: {e}")
            return False
    
    def get_repository_info(self):
        """Get detailed information about a specific repository."""
        try:
            response = self.ecr.describe_repositories(
                repositoryNames=[self.repository_name]
            )
            
            if not response['repositories']:
                logger.error(f"Repository {self.repository_name} not found")
                return False
            
            repo = response['repositories'][0]
            
            logger.info(f"📋 Repository Information: {self.repository_name}")
            logger.info("-" * 50)
            logger.info(f"Name: {repo['repositoryName']}")
            logger.info(f"URI: {repo['repositoryUri']}")
            logger.info(f"Created: {repo['createdAt']}")
            logger.info(f"Tag Mutability: {repo['imageTagMutability']}")
            
            # Get lifecycle policy
            try:
                lifecycle_response = self.ecr.get_lifecycle_policy(
                    repositoryName=self.repository_name
                )
                logger.info(f"Lifecycle Policy: {lifecycle_response['lifecyclePolicyText']}")
            except ClientError:
                logger.info("Lifecycle Policy: None")
            
            # Get image scanning configuration
            try:
                scan_response = self.ecr.get_image_scanning_configuration(
                    repositoryName=self.repository_name
                )
                logger.info(f"Scan on Push: {scan_response['imageScanningConfiguration']['scanOnPush']}")
            except ClientError:
                logger.info("Scan on Push: Unable to retrieve")
            
            # Get recent images
            try:
                images_response = self.ecr.describe_images(
                    repositoryName=self.repository_name,
                    maxResults=10
                )
                
                logger.info(f"\nRecent Images ({len(images_response['imageDetails'])}):")
                for image in images_response['imageDetails']:
                    tags = image.get('imageTags', ['<untagged>'])
                    pushed_at = image.get('imagePushedAt', 'Unknown')
                    size = image.get('imageSizeInBytes', 0)
                    
                    for tag in tags:
                        logger.info(f"  - {tag} (pushed: {pushed_at}, size: {size} bytes)")
                
            except ClientError as e:
                logger.info(f"Recent Images: Unable to retrieve ({e})")
            
            return True
            
        except ClientError as e:
            logger.error(f"Error getting repository info: {e}")
            return False
    
    def run(self):
        """Main execution method."""
        logger.info("Starting ECR repository management")
        logger.info(f"Action: {self.action}")
        logger.info(f"Repository: {self.repository_name}")
        
        if self.action == 'create':
            success = self.create_repository()
        elif self.action == 'update':
            success = self.update_repository()
        elif self.action == 'cleanup':
            success = self.cleanup_old_images()
        elif self.action == 'list':
            success = self.list_repositories()
        else:
            logger.error(f"Unknown action: {self.action}")
            sys.exit(1)
        
        if success:
            logger.info("ECR management completed successfully")
        else:
            logger.error("ECR management failed")
            sys.exit(1)

if __name__ == "__main__":
    manager = ECRManager()
    manager.run() 