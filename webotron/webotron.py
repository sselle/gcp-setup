from google.cloud import storage
import click

@click.group()
def cli():
    global storage_client
    storage_client = storage.Client()

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
    buckets = list(storage_client.list_buckets())
    print(buckets)


if __name__ == '__main__':
    cli()