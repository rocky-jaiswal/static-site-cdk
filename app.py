#!/usr/bin/env python3

import os
from aws_cdk import core as cdk

from static_site.static_site_stack import StaticSiteStack

SITE_DOMAIN = "praywithus.site"

app = cdk.App()

StaticSiteStack(app, 
  "StaticSiteStack",
  env=cdk.Environment(account='750324395434', region='eu-central-1'),
  site_domain=SITE_DOMAIN)

app.synth()
