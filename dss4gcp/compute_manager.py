import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from service_account_manager import ServiceAccountManager

class ComputeManager:
    """Manages GCE resources on GCP"""
    def __init__(self, project, zone):
        self.gce = googleapiclient.discovery.build('compute', 'v1')
        self.project = project
        self.zone = zone

        self.sa_manager = ServiceAccountManager(self.project)


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
        sa_email = self.sa_manager.create_service_account(sa_name)['email']
        # UPDATE SA WITH NEEDED PERMISSIONS
       
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