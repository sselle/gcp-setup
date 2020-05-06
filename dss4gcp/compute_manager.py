import googleapiclient.discovery
from googleapiclient.errors import HttpError

class ComputeManager:
    """Manages compute resources on GCP"""
    def __init__(self, project, zone):
        self.gce = googleapiclient.discovery.build('compute', 'v1')
        self.project = project
        self.zone = zone

    def all_instances(self):
        """Return list of all instances"""
        return self.gce.instances().list(project=self.project, zone=self.zone).execute()

    @staticmethod
    def get_image_for_os(os_flavour):
        pass

    def create_design_node(self, 
                            size='small', 
                            service_account='default', 
                            os_flavour='centos', 
                            name='design-node'):

        """Create GCE instance to run design node"""
        # not implemented: instance size, os_flavour selection
        # get latest image - CentOS static for now
        image_response = self.gce.images().getFromFamily(
            project='centos-cloud', 
            family='centos-8').execute()
        
        source_disk_image = image_response['selfLink']
        machine_type = 'zones/{}/machineTypes/n1-standard-1'.format(self.zone)

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
                'email': service_account,
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write'
                ]
            }],
        }

        #start the instance
        try:
            self.gce.instances().insert(project=self.project,
                                        zone=self.zone,
                                        body=config).execute()
        except HttpError as error:
            print(error)

        print(image_response)