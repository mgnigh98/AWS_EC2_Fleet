To run this code the following steps will need to be done on AWS:
    Create Launch Template:
        I recommend naming them something you can use in every region with the same name
        The launch Template should specify the key being used for access
        (Recommend to have the name be consistent but with the region name in key file name ex: AWS_us-east-1.pem)
        In Network Settings you will need a security group with port 22 open
        Under Advanced details you will need the instance to have a include a IAM instance profile that has S3 Access (recommended: S3FullAccess)
    
    Create User:
        In IAM Dashboard click Users > Create User to create a User
        Provide Permissions in your preferred manner (Attach Policies Directly with EC2FullAccess will work best for this)
        Create User
        After that open the User and Create Access Key (Local Code) (IDE support may not work so this will work)
        Take the Access Key and Secret Access Key
        place them in the file USER/.aws/credentials (no file extension)
        File will look like:

        [default]
        aws_access_key_id=(ACCESS KEY from AWS)
        aws_secret_access_key=(SECRET ACCESS KEY from AWS)

        This will allow the code to interact with your AWS account to create EC2 Instances

The code is structured to send the files from cfg.dirs and retrieve based on cfg.rsync
It will also send startup, conda and python_ bash files with:
    startup.bash will run first and will be nonblocking calling conda.bash after
    python_.bash will be sourced and will run after the previous two finish
A tmux session is created which can be connected to using 'tmux a' once you ssh into the session
This will show you the progress and any outputs of the code
It is recommended you also create a log file which can be synced back to the local machine

Finally it is recommended you start your train script from a bash file that ends with 
    sleep 5m
    sudo shutdown
This prevents additional unneccesary costs but allows enough time to download everything you should need
