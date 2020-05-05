from google.cloud import storage
import click

from storage_manager import StorageManager

@click.group()
def cli():
    global storage_manager
    storage_manager = StorageManager()


@cli.command('list-instances')
def list_instances():
    """List all instances in current project"""
    print('look at all my instances!')


@cli.command('create-instance')
def create_instance():
    """create a new instance in current project"""
    print('here we will create a new instance later')


@cli.command('list-buckets')
def list_buckets():
    """list all buckets in GCP project"""
    for bucket in storage_manager.all_buckets():
        print(bucket.name)


if __name__ == '__main__':
    cli()