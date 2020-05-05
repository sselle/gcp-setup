import googleapiclient.discovery

class ComputeManager:
    """Manages compute resources on GCP"""
    def __init__(self, project, zone):
        self.gcs = googleapiclient.discovery.build('compute', 'v1')
        self.project = project
        self.zone = zone

    def all_instances(self):
        """Return list of all instances"""
        return self.gcs.instances().list(project=self.project, zone=self.zone).execute()