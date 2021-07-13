#!/usr/bin/env python3

import os
from argparse import ArgumentParser

from aws_cdk import core as cdk

from static_site_cdk.static_site_stack import StaticSiteStack


parser = ArgumentParser()
parser.add_argument("-d", "--domain", dest="domain", help="site domain")
parser.add_argument("-c", "--contents", dest="contents", help="site contents")
parser.add_argument("-a", "--accountid", dest="account_id", help="AWS account id")
parser.add_argument("-r", "--region", dest="region", help="main AWS region")

args = parser.parse_args()


def synth():
    SITE_DOMAIN = args.domain
    SITE_CONTENTS = args.contents
    ACCOUNT = args.content_id
    REGION = args.region

    app = cdk.App()

    StaticSiteStack(
        app,
        "StaticSiteStack",
        env=cdk.Environment(account=ACCOUNT, region=REGION),
        site_domain=SITE_DOMAIN,
        site_contents=SITE_CONTENTS,
    )

    app.synth()
