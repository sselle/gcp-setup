import os

import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

class ComputeManager:
    """Manages compute resources on GCP"""
    def __init__(self, project, zone):
        self.gce = googleapiclient.discovery.build('compute', 'v1')
        self.project = project
        self.zone = zone


    def all_instances(self):
        """Return list of all instances"""
        return self.gce.instances().list(project=self.project, zone=self.zone).execute()


    def get_image_for_os(self, os_flavour):
        """Get image for selected os-falvour"""
        os_selector = {
            'centos': self.gce.images().getFromFamily(project='centos-cloud',
                                                        family='centos-8').execute(),
            'debian': self.gce.images().getFromFamily(project='debian-cloud',
                                                        family='debian-9').execute()
        }
        return os_selector.get(os_flavour, 
                                'Invalid OS flavour {}. Currently centos and devian are supported '.format(os_flavour))


    def all_service_accounts(self):
        """List all service accounts in configured project"""
        credentials = service_account.Credentials.from_service_account_file(
            filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
            scopes=['https://www.googleapis.com/auth/cloud-platform'])

        service = googleapiclient.discovery.build(
            'iam', 'v1', credentials=credentials)
        
        service_accounts = service.projects().serviceAccounts().list(
            name='projects/' + self.project).execute()

        for account in service_accounts['accounts']:
            print('Name: ' + account['name'])
            print('Email: ' + account['email'])
            print(' ')
        
        return 'default'
    
    def create_service_account(self, sa_name):
        """create service account with needed permissions to run DSS"""
        #service-account-name@project-id.iam.gserviceaccount.com
        credentials = service_account.Credentials.from_service_account_file(
            filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
            scopes=['https://www.googleapis.com/auth/cloud-platform'])

        service = googleapiclient.discovery.build(
            'iam', 'v1', credentials=credentials)
        #TRY CATCH einfügen für SA Erstellung
        my_service_account = service.projects().serviceAccounts().create(
        name='projects/' + self.project,
        body={
            'accountId': sa_name,
            'serviceAccount': {
                'displayName': 'SA for DSS design node'
            }
        }).execute()

        print('Created service account: ' + my_service_account['email'])
        return my_service_account


    @staticmethod
    def create_instance_config(name, machine_type, source_disk_image, sa_email):
        config = {
            'name': name,
            'machineType': machine_type,

             # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                    }
                }
            ],
            # Specify a network interface with NAT to access the public internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],

            # Allow the instance to access cloud storage and logging.
            'serviceAccounts': [{
                'email': sa_email,
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write'
                ]
            }],
        } 
        return config
    
    def create_design_node(self, 
                            size='small', 
                            sa_name='sa-design-node', 
                            os_flavour='centos', 
                            name='design-node'):

        """Create GCE instance to run design node"""
        image_response = self.get_image_for_os(os_flavour)
        source_disk_image = image_response['selfLink']
        machine_type = 'zones/{0}/machineTypes/{1}'.format(self.zone, size)
        sa_email = self.create_service_account(sa_name)['email']
       
        config = self.create_instance_config(name=name, 
                                            machine_type=machine_type, 
                                            source_disk_image=source_disk_image, 
                                            sa_email=sa_email)

        #start the instance
        try:
            self.gce.instances().insert(project=self.project,
                                        zone=self.zone,
                                        body=config).execute()
        except HttpError as error:
            print(error)