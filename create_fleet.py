import boto3
import paramiko
import subprocess
import os
import shutil
import time

from types import SimpleNamespace
cfg = SimpleNamespace(**{})

cfg.connection_attempts=600
# cfg.region = 'us-east-1'
cfg.min_instances=1
cfg.total_instances=1
cfg.onDemand_instances=0    #more expensive
cfg.spot_instances=1        #cheaper

cfg.MaxSpotPriceAsPercentageOfOptimalOnDemandPrice = 100

#dictionary of key(destination): item(list of sources) pairs
cfg.dirs = {
    'nvme/python':["C:/Users/K159658/tim/python/tim_utils", "C:/Users/K159658/tim/python/complextorch",
                   r"C:\Users\K159658\tim\python\NAFNet"],
    # 'nvme/python/files':[r"C:\Users\K159658\tim\python\CVNAFNN\files\sicd.zip"],
}

#dictionary of key(destination): item(list of sources) pairs
#the string 'INSTANCE_ID' can be used as a placeholder for the id of the instance and will be replaced at runtime
cfg.rsync = {
    "C:/Users/K159658/tim/python/CVNAFNN/files": ['nvme/python/NAFNet/experiments/'],
    "C:/Users/K159658/tim/python/CVNAFNN/files/INSTANCE_ID/NAFNet-SICD-width64": ['nvme/python/NAFNet/options/train/SICD/']

}

class CreateFleet():
    def __init__(self) -> None:
        self.username = 'ubuntu'
        self.region = 'us-east-2'
        self.key_file = f"keys/AWS_{self.region}.pem"


        self.ec2_client = boto3.client('ec2', region_name=self.region)
        self.waiter=self.ec2_client.get_waiter('instance_running')
        self.pClient = paramiko.SSHClient()
        self.pClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())       
        self.pkey = paramiko.Ed25519Key.from_private_key_file(self.key_file)

        self.allowed_instances=['g5.8xlarge']#['g5.12xlarge']#['g5.2xlarge', 'g5.4xlarge', 'g5.8xlarge']#['g5.12xlarge', 'g5.48xlarge','p4d.24xlarge']#['g5.2xlarge', 'g5.4xlarge', 'g5.8xlarge']#, 'g5.16xlarge']'g5.24xlarge',['g5.12xlarge',  'g5.48xlarge','p4d.24xlarge']#


        self.copied_python = False
        

    def create_fleet(self, instances=['g5.2xlarge', 'g5.4xlarge']):
        dryRun=False
        clientToken=''
        spotOptions={
            'AllocationStrategy': 'price-capacity-optimized', #'lowest-price'|'diversified'|'capacity-optimized'|'capacity-optimized-prioritized'|'price-capacity-optimized'
            'InstanceInterruptionBehavior': 'terminate', #'hibernate'|'stop'|'terminate'
            'SingleInstanceType': True,#True|False,
            'MinTargetCapacity': cfg.min_instances,
        }
        onDemandOptions={}
        launchTemplateConfigs=[
            {
                'LaunchTemplateSpecification': {
                    'LaunchTemplateName': 'python_launch',
                    'Version': '1'
                },
                'Overrides': [
                    {
                        'InstanceRequirements': {
                            'VCpuCount': {
                                'Min': 1,
                                'Max': 640000
                            },
                            'MemoryMiB': {
                                'Min': 1,
                                'Max': 640000000
                            },
                        'AllowedInstanceTypes': instances,
                        'MaxSpotPriceAsPercentageOfOptimalOnDemandPrice': cfg.MaxSpotPriceAsPercentageOfOptimalOnDemandPrice,
                        },
                    },
                ]
            },
        ]
        targetCapacitySpecification={
            'TotalTargetCapacity': cfg.total_instances,
            'OnDemandTargetCapacity': cfg.onDemand_instances,
            'SpotTargetCapacity': cfg.spot_instances,
            'DefaultTargetCapacityType': 'spot'
        }
        terminateInstancesWithExpiration=False
        tagSpecifications=[]
        context=''
        
        response = self.ec2_client.create_fleet(
            DryRun=dryRun, 
            ClientToken=clientToken,
            SpotOptions=spotOptions,
            OnDemandOptions=onDemandOptions,
            LaunchTemplateConfigs=launchTemplateConfigs,
            TargetCapacitySpecification=targetCapacitySpecification,
            TerminateInstancesWithExpiration=terminateInstancesWithExpiration,
            Type='instant',
            TagSpecifications=tagSpecifications,
            Context=context)
        
        return response


    def run_bash(self, script, tmux=False, print_out=False, print_err=False):
        if tmux:
            script = f'tmux send-keys -t aws "{script}" C-m'
        stdin, stdout, stderr = self.pClient.exec_command(script)
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        if print_out:
            print("=== STDOUT ===")
            print(output)
        if print_err:
            print("=== STDERR ===")
            print(errors)


    def scp_up(self, source_path,remote_path='/home/ubuntu/nvme'):
        if os.path.isfile(source_path):
            # print(f'scp -o StrictHostKeyChecking=no -i {self.key_file} {source_path} ubuntu@{self.ip}:{remote_path}')
            subprocess.run(f'scp -o StrictHostKeyChecking=no -i {self.key_file} {source_path} ubuntu@{self.ip}:{remote_path}')
        else:
            # print(f'scp -r -o StrictHostKeyChecking=no -i {self.key_file} {source_path} ubuntu@{self.ip}:{remote_path}')
            subprocess.run(f'scp -r -o StrictHostKeyChecking=no -i {self.key_file} {source_path} ubuntu@{self.ip}:{remote_path}')

    def export_conda(self):
        subprocess.run('conda env export -f aws.yml --from-history')

    def check_pulse(self):
        response = self.ec2_client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['InstanceId'] == self.inst_id[0]:
                    state = instance['State']['Name']
                    break
        if state == "stopped" or state == "terminated":
            print("STATE of INSTANCE: ", state)
            self.pulse = False
            return
        elif state != "running":
            print("STATE of INSTANCE: ", state)
        for local in cfg.rsync.keys():
            if 'INSTANCE_ID' in local:
                target_path = local.replace("INSTANCE_ID", self.inst_id[0])
            else:
                self.mkdir(local, self.inst_id[0])
                target_path = f"{local}/{self.inst_id[0]}"
            if not self.copied_python:
                for path in cfg.dirs['nvme/python']:
                    if os.path.isfile(path):
                        shutil.copy2(path, target_path)
                self.copied_python = True
            for remote in cfg.rsync[local]:
                self.rsync(source=remote, target=target_path, recursive=True)
    
    def rsync(self, source, target, recursive=False):
        import stat
        basename = os.path.basename(source)
        targ_dir = os.path.join(target,basename).replace('\\', '/')
        if basename:
            self.mkdir(target,basename)
        
        with self.pClient.open_sftp() as sftp:
            files = sftp.listdir_attr(source)
            for f in files:
                if stat.S_ISDIR(f.st_mode):
                    if recursive:
                        self.mkdir(targ_dir, f.filename)
                        self.rsync(source=f"{source}/{f.filename}/", target=f"{targ_dir}/{f.filename}", recursive=True)
                    else: continue
                else:
                    local_file_path = os.path.join(targ_dir, f.filename)
                    if ((not os.path.isfile(local_file_path)) or 
                        (f.st_mtime > os.path.getmtime(local_file_path))):
                        print("Syncing ", f.filename )
                        if os.path.isfile(local_file_path):
                            os.remove(local_file_path)
                        sftp.get(f"{source}/{f.filename}", local_file_path)
                # print(f)
    
    def mkdir(self, *args):
        if not os.path.exists(os.path.join(*args)):
            os.mkdir(os.path.join(*args))
    
    def close_clients(self, terminate_on_close=False):
        if terminate_on_close:
            self.ec2_client.terminate_instances(InstanceIds=self.inst_id)
        self.ec2_client.close()
        self.pClient.close()

    def start(self):

        for i in range(cfg.connection_attempts):
            fleet_response = self.create_fleet(self.allowed_instances)
            Errors = fleet_response['Errors']

            if fleet_response['Instances']:
                fleet_id = fleet_response['FleetId']
                self.inst_id = fleet_response['Instances'][0]['InstanceIds']
                self.waiter.wait(InstanceIds=self.inst_id)
                print("Instance Created")
                ips = [inst['PublicIpAddress'] for inst in self.ec2_client.describe_instances(InstanceIds=self.inst_id)['Reservations'][0]['Instances']]
                self.ip = ips[0]
                subprocess.run("clip", input=self.ip, text=True)
                time.sleep(10)
                for i in range(5):
                    try:
                        self.pClient.connect(self.ip, username=self.username, pkey=self.pkey)
                    except Exception as e: 
                        print(e)
                        print("trying to connect again")
                        time.sleep(5)
                    else: break
                
                script_wait=True 
                self.run_bash('sudo apt-get update') 
                self.run_bash('sudo apt install nvidia-driver-535 nvidia-utils-535 nvidia-fabricmanager-535 -y')
                self.run_bash('sudo reboot')
                time.sleep(20)
                while script_wait:
                    try:
                        pi = ["", '2'][0] #python index number
                        self.pClient.connect(self.ip, username=self.username, pkey=self.pkey)
                        self.scp_up('startup.bash', remote_path='/home/ubuntu')
                        self.scp_up('conda.bash', remote_path='/home/ubuntu')
                        self.scp_up(f'python{pi}.bash', remote_path='/home/ubuntu')
                        self.run_bash(script='nohup bash startup.bash &', print_err=False)
                        for dest, source in [(key, value)  for key, values in cfg.dirs.items() for value in values]:
                            self.scp_up(source, dest)
                        self.run_bash(script=f'source python{pi}.bash', tmux=True)
                        script_wait=False
                    except Exception as e:
                        print(e)
                        print("Waiting to run Script")
                        time.sleep(5)
                #run_scp(f'scp -i SpotInstances.pem {cfg.conda_yml} ubuntu@{ips[0]}:/home/ubuntu/nvme')              
                break
            else:
                break_out = False
                for Error in Errors:
                    if Error['ErrorCode'] !='UnfulfillableCapacity' and Error['ErrorCode'] != 'InsufficientInstanceCapacity':
                        print(Error['ErrorCode'])
                        print(Error['ErrorMessage'])
                        break_out=True
                if break_out:
                    return
            
            print("Waiting for Fleet Start")
            time.sleep(30)
        else:
            for Error in Errors:
                print(Error['ErrorMessage'])
            return
        print(fleet_id)
        print(ips)
        self.pulse_monitor()
    
    def reconnect(self, cold_start=True):
        if cold_start:
            self.inst_id = ["i-0f50aaede9bea6759"]
            ips = [inst['PublicIpAddress'] for inst in self.ec2_client.describe_instances(InstanceIds=self.inst_id)['Reservations'][0]['Instances']]
            self.ip = ips[0]
        self.pClient.connect(self.ip, username=self.username, pkey=self.pkey)

        self.pulse_monitor()

    def pulse_monitor(self):
        self.pulse = True
        while self.pulse:
            try:
                self.check_pulse()
                time.sleep(30)
            except Exception as e:
                print(e)
                time.sleep(300)
                if str(e) == "SSH session not active":
                    print("SSH Reconnection Attempt")
                    self.pClient.connect(self.ip, username=self.username, pkey=self.pkey)

        self.close_clients(True)

if __name__ == "__main__":
    import sys
    fleet = CreateFleet()
    if len(sys.argv) >1:
        fleet.reconnect()
    else:
        fleet.start()
