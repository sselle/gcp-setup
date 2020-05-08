import os
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

class ServiceAccountManager:
    def __init__(self, project):
        self.project = project

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
        sa_design_node = service.projects().serviceAccounts().create(
        name='projects/' + self.project,
        body={
            'accountId': sa_name,
            'serviceAccount': {
                'displayName': 'SA for DSS design node'
            }
        }).execute()

        print('Created service account: ' + sa_design_node['email'])
        return sa_design_node


