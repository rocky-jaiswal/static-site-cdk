#!/usr/bin/env python3

import os
from argparse import ArgumentParser

from aws_cdk import core as cdk

from static_site_cdk.static_site_stack import StaticSiteStack


def synth(domain, contents, account, region):
    app = cdk.App()

    StaticSiteStack(
        app,
        "StaticSiteStack",
        env=cdk.Environment(account=account, region=region),
        site_domain=domain,
        site_contents=contents,
    )

    app.synth()


parser = ArgumentParser()
parser.add_argument("-d", "--domain", dest="domain", help="site domain")
parser.add_argument("-c", "--contents", dest="contents", help="site contents")
parser.add_argument("-a", "--accountid", dest="account_id", help="AWS account id")
parser.add_argument("-r", "--region", dest="region", help="main AWS region")

args = parser.parse_args()
synth(args.domain, args.contents, args.account_id, args.region)
