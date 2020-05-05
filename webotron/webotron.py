import click

from storage_manager import StorageManager
from compute_manager import ComputeManager

@click.group()
def cli():
    global storage, compute
    storage = StorageManager()
    compute = ComputeManager(project='dataiku-cluster', zone='us-central1-a')

@cli.command('list-instances')
def list_instances():
    """List all instances in current project"""
    for instance in compute.all_instances()['items']:
        print(instance['name'])


@cli.command('create-instance')
def create_instance():
    """create a new instance in current project"""
    print('here we will create a new instance later')


@cli.command('list-buckets')
def list_buckets():
    """list all buckets in GCP project"""
    for bucket in storage.all_buckets():
        print(bucket.name)


if __name__ == '__main__':
    cli()