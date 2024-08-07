import subprocess
import json

class LambdaClient():
    def __init__(self, region) -> None:
        self.region = region
        self.instance_type = 
        self.api = 
        

    def launch_instances(self):

        subprocess.run(f"""curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/instance-operations/launch -d @request.json -H "Content-Type: application/json" | jq .""")
    def restart_instances(self):
        subprocess.run(f"""curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/instance-operations/restart -d @INSTANCE-IDS -H "Content-Type: application/json" | jq .""")

    def terminate_instances(self):
        subprocess.run(f"curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/instance-operations/terminate -d @INSTANCE-IDS -H 'Content-Type: application/json'")

    def describe_instances(self):
        subprocess.run(f"curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/instances")
    
    def describe_instance(self, instance_id):

        subprocess.run(f"curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/instances/{instance_id}")
    
    def describe_instance_types(self):

        subprocess.run(f"curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/instance-types")

    def add_ssh_key(self):
        
        subprocess.run(f'curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/ssh-keys -d @ssh-key.json -H "Content-Type: application/json"')
        
    def generate_ssh_key(self):
        '''fix later'''
        subprocess.run(f"""curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/ssh-keys -d '{ "name": "my-generated-key" }' -H "Content-Type: application/json" | jq -r ".data.private_key" > my-generated-private-key.pem""")

    def list_ssh_keys(self):
        subprocess.run(f"curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/ssh-keys")

    def delete_ssh_key(self, key_id):
        subprocess.run(f"curl -u {self.api}: -X DELETE https://cloud.lambdalabs.com/api/v1/ssh-keys/{key_id}")

    def list_file_systems(self):

        subprocess.run(f"curl -u {self.api}: https://cloud.lambdalabs.com/api/v1/file-systems")
