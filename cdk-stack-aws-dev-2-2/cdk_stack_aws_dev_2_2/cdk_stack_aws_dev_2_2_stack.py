import warnings
warnings.filterwarnings('ignore', module='aws_cdk')

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
    Tags,
    Duration
)
from constructs import Construct

class CdkStackAwsDev22Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template_options.description = "Task #5: Frontend Stack with Import service"

        bucket_name = "aws-dev-shymanouski"
        tags = {
            "task": "5",
            "owner": "ashymanouski"
        }

        def apply_tags(resource):
            for key, value in tags.items():
                Tags.of(resource).add(key, value)

        website_bucket = s3.Bucket(
            self, "WebsiteBucket",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            bucket_key_enabled=True
        )
        apply_tags(website_bucket)

        origin_access_identity = cloudfront.OriginAccessIdentity(
            self, "WebsiteOAI",
            comment="OAI for website bucket"
        )
        apply_tags(origin_access_identity)

        # # Grant read permissions to the OAI
        # website_bucket.grant_read(origin_access_identity)

        # # Add bucket policy
        # website_bucket.add_to_resource_policy(
        #     iam.PolicyStatement(
        #         actions=["s3:GetObject"],
        #         resources=[website_bucket.arn_for_objects("*")],
        #         principals=[iam.CanonicalUserPrincipal(
        #             origin_access_identity.cloud_front_origin_access_identity_s3_canonical_user_id
        #         )]
        #     )
        # )

        distribution = cloudfront.Distribution(
            self, "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    website_bucket,
                    origin_access_identity=origin_access_identity
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            comment="aws-dev-2-2: automated deployment",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(0)
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(0)
                )
            ]
        )
        apply_tags(distribution)

        deployment = s3deploy.BucketDeployment(
            self, "WebsiteDeployment",
            sources=[s3deploy.Source.asset("../dist")],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )
        apply_tags(deployment)

        apply_tags(self)

        CfnOutput(
            self, "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="CloudFront Distribution URL"
        )

        CfnOutput(
            self, "BucketName",
            value=website_bucket.bucket_regional_domain_name,
            description="S3 Bucket URL"
        )
