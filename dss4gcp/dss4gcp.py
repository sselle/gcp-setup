import click

from storage_manager import StorageManager
from compute_manager import ComputeManager

@click.group()
def cli():
    """dss4gcp supports the setup of gcp infrastrucutre"""
    global storage, compute
    storage = StorageManager()
    compute = ComputeManager(project='dataiku-cluster', zone='us-central1-a')

@cli.command('list-instances')
def list_instances():
    """List all instances in current project"""
    for instance in compute.all_instances()['items']:
        print(instance['name'])

@cli.command('create-instance')
@click.argument('instance-name')
@click.option('--os-flavour', default='centos', help='centos or debian')
@click.option('--machine-type', default='f1-micro', help='enter valid GCE machine type')
def create_instance(instance_name, os_flavour, machine_type):
    """create a new instance to run DSS"""
    compute.create_design_node( size = machine_type, 
                                sa_name = 'sa-design-node',
                                name=instance_name,
                                os_flavour=os_flavour
                                )

@cli.command('list-service-accounts')
def list_service_accounts():
    compute.all_service_accounts()

@cli.command('list-buckets')
def list_buckets():
    """list all buckets in GCP project"""
    for bucket in storage.all_buckets():
        print(bucket.name)


if __name__ == '__main__':
    cli()