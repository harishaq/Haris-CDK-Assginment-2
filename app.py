#!/usr/bin/env python3
import os

import aws_cdk as cdk

from haris_cdk.network_stack import NetworkStack
from haris_cdk.server_stack import ServerStack


app = cdk.App()
network = NetworkStack(app, "HarisNetworkStack")
ServerStack(app, "HarisServerStack", network.vpc )

app.synth()
