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

        self.site_domain = kwargs["site_domain"]

        zone = route53.HostedZone.from_lookup(
            self,
            "Zone",
            domain_name=self.site_domain,
        )
        cdk.CfnOutput(self, "Site", value=f"https://{self.site_domain}")

        bucket = s3.Bucket(
            self,
            "SiteBucket",
            bucket_name=self.site_domain,
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=True,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        cdk.CfnOutput(self, "Bucket", value=bucket.bucket_name)

        # TLS certificate
        certificate_arn = acm.DnsValidatedCertificate(
            self,
            "SiteCertificate",
            domain_name=self.site_domain,
            hosted_zone=zone,
            region="us-east-1",  # Cloudfront only checks this region for certificates.
        ).certificate_arn

        cdk.CfnOutput(self, "Certificate", value=certificate_arn)

        # CloudFront distribution that provides HTTPS
        distribution = cloudfront.CloudFrontWebDistribution(
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

        cdk.CfnOutput(self, "Distribution-Id", value=distribution.distribution_id)

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

        # Deploy site contents to S3 bucket
        s3_deployment.BucketDeployment(
            self,
            "Deploy-With-Invalidation",
            sources=[s3_deployment.Source.asset("./site-contents/v1")],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )
