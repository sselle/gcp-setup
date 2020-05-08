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

        #Set the required permissions
        policy = self.get_policy(credentials=credentials)
        policy = self.modify_policy(policy=policy, 
                                    sa_email=sa_design_node['email'])
        self.set_policy(credentials=credentials,
                        policy=policy)
        return sa_design_node


    def get_policy(self, credentials):
        """Get IAM policy for the project"""
        service = googleapiclient.discovery.build(
            "cloudresourcemanager", "v1", credentials=credentials)

        policy = (
            service.projects()
            .getIamPolicy(
                resource=self.project,
                body={"options": {"requestedPolicyVersion": "1"}},
            )
            .execute()
        )
        return policy
    

    def modify_policy(self, policy, sa_email):
        """Adds a new member to a role binding."""
        # Add: required roles, if not exist
        role = 'roles/compute.admin'
        binding = next(b for b in policy["bindings"] if b["role"] == role)
        binding["members"].append('serviceAccount:'+sa_email)
        print(binding)
        return policy


    def set_policy(self, credentials, policy):
        service = googleapiclient.discovery.build(
            "cloudresourcemanager", "v1", credentials=credentials
        )
        # set new policy
        policy = (
            service.projects()
            .setIamPolicy(resource=self.project, body={"policy": policy})
            .execute()
        )

