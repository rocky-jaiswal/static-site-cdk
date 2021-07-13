from aws_cdk import (
    core as cdk,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_s3_deployment as s3_deployment,
)


class StaticSiteStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, env=kwargs["env"])

        # Configuration
        self.site_domain = kwargs["site_domain"]
        self.site_contents = kwargs["site_contents"]

        # Create Zone
        zone = self.create_zone()
        cdk.CfnOutput(self, "Site", value=f"https://{self.site_domain}")

        # Create Bucket
        bucket = self.create_bucket()
        cdk.CfnOutput(self, "Bucket", value=bucket.bucket_name)

        # Create Certificate
        certificate_arn = self.create_certificate(zone)
        cdk.CfnOutput(self, "Certificate", value=certificate_arn)

        # Create CF Distribution
        distribution = self.create_distribution(bucket, certificate_arn)
        cdk.CfnOutput(self, "Distribution-Id", value=distribution.distribution_id)

        # Create DNS A record
        self.create_a_record(zone, distribution)

        # Deploy site contents to S3 bucket
        self.deploy_contents(bucket, distribution)

    def create_zone(self):
        return route53.HostedZone.from_lookup(
            self,
            "Zone",
            domain_name=self.site_domain,
        )

    def create_bucket(self):
        return s3.Bucket(
            self,
            "SiteBucket",
            bucket_name=self.site_domain,
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=True,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

    def create_certificate(self, zone):
        # TLS certificate
        return acm.DnsValidatedCertificate(
            self,
            "SiteCertificate",
            domain_name=self.site_domain,
            hosted_zone=zone,
            region="us-east-1",  # Cloudfront only checks this region for certificates.
        ).certificate_arn

    def create_distribution(self, bucket, certificate_arn):
        # CloudFront distribution that provides HTTPS
        return cloudfront.CloudFrontWebDistribution(
            self,
            "SiteDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    custom_origin_source=cloudfront.CustomOriginConfig(
                        domain_name=bucket.bucket_website_domain_name,
                        origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                    ),
                    behaviors=[cloudfront.Behavior(is_default_behavior=True)],
                )
            ],
            alias_configuration=cloudfront.AliasConfiguration(
                acm_cert_ref=certificate_arn,
                names=[self.site_domain],
                ssl_method=cloudfront.SSLMethod.SNI,
                security_policy=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2019,
            ),
        )

    def create_a_record(self, zone, distribution):
        # Route53 alias record for the CloudFront distribution
        route53.ARecord(
            self,
            "Site-Alias-Record",
            zone=zone,
            record_name=self.site_domain,
            target=route53.RecordTarget(
                alias_target=route53_targets.CloudFrontTarget(distribution)
            ),
        )

    def deploy_contents(self, bucket, distribution):
        s3_deployment.BucketDeployment(
            self,
            "Deploy-With-Invalidation",
            sources=[s3_deployment.Source.asset(self.site_contents)],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )
