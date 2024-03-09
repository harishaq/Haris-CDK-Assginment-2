import aws_cdk  as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
from constructs import Construct

class ServerStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **props):
        super().__init__(scope, id, **props)

        # Define a security group for the web servers that allows inbound traffic on port 80
        web_server_sg = ec2.SecurityGroup(self, 'WebServerSG', 
                                          vpc=vpc, 
                                          allow_all_outbound=True, 
                                          description='Allow port 80')
        web_server_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), 'Allow HTTP traffic')

        # Launch web servers
        ami = ec2.AmazonLinuxImage()
        for subnet in vpc.public_subnets:
            ec2.Instance(self, f'WebServer{subnet.node.id}',
                         vpc=vpc,
                         instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
                         machine_image=ami,
                         security_group=web_server_sg,
                         vpc_subnets=ec2.SubnetSelection(subnets=[subnet]))

        # RDS instance
        rds_sg = ec2.SecurityGroup(self, 'RDSSG', 
                                   vpc=vpc, 
                                   description='Allow MySQL access')
        rds_sg.add_ingress_rule(web_server_sg, ec2.Port.tcp(3306), 'Allow MySQL from web servers')

        rds.DatabaseInstance(self, 'RDSInstance',
                             engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0),
                             instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
                             vpc=vpc,
                             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                             security_groups=[rds_sg])
