# Configure a VPC to Deploy a Secure, Highly Available, and Scalable Architecture on AWS

In this guide, I will configure a Virtual Private Cloud (VPC) to deploy a Python-based web server and a MySQL database in a secure, highly available, and scalable architecture.

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)

## I'm going to deploy the next cloud architecture on AWS
![arquitectura aws](img/arq-hs-ha.gif)

<hr>
1. I'll build the network architecture using the AWS VPC service.

   - I'm going to create a VPC with the following IPv4 CIDR Block
     - 192.168.0.0/16
    
   - I will create the three subnets with the next names:
     - **PublicSubnetA**:
          - Availability Zone: a
          - CIDR: 192.168.1.0/24
            
      - **PublicSubnetB**:
          - Availability Zone: b
          - CIDR: 192.168.2.0/24
      
     - **PrivateSubnetA**:
          - Availability Zone: a
          - CIDR: 192.168.3.0/24
      
     - **PrivateSubnetB**:
          - Availability Zone: b
          - CIDR: 192.168.4.0/24
            
     - **PrivateSubnetAA**:
          - Availability Zone: a
          - CIDR: 192.168.5.0/24
      
     - **PrivateSubnetBB**:
          - Availability Zone: b
          - CIDR: 192.168.6.0/24

   I need the VPC to have an Internet connection so I need to configure an **Internet Gateway**.
   - When the Internet Gateway is created, I attach it to the VPC
   - I create a Route Table
   - In the Route Table associate with the two **Public Subnet** and I create a route for allow to connect to the Internet through the **Internet Gateway**  

<hr>
2. I'll use the AWS System Manager service to store the connection parameters that the web server will use to connect to the database configured on AWS RDS.

   - Using AWS System Manager with Parameter Store I create the following parameters:
      - /book/user: root
      - /book/password: *Test!2024* using the *SecureString* type
      - /book/database: books_db
      - /book/host: 192.168.1.23 *The IP address where the database is located. When creating the database on RDS I need to change this IP address to the endpoint provided by RDS*.
      
   - The web server will run in the EC2 instance and it needs to read the connection parameters to the database deployed on RDS, so I need to create an IAM role that has permission to EC2 to read the connection parameters from the System Manager service.
      - In the IAM service I create a role named *ec2RoleSSM*.
      - The Role has the following permission:
         - SSMFullAccess           

<hr>

3. I going to the AWS EC2 service and I create four security groups.

      - The first security group has the next parameters:
      
         - Name: alb-SG
         - Inboud rules:
            - Type: Custom TCP
            - Port Range: 80
            - Source: Anywhere
              
      - The second security group has the next parameters:
      
         - Name: web-server-SG
         - Inboud rules:
            - Type: Custom TCP
            - Port Range: 5000
            - Source: alb-SG *(The SG of the application load balancer)*
              
      - The third security group has the next parameters:
       
         - Name: database-SG
         - Inboud rules:
            - Type: MYSQL/Aurora
            - Port Range: 3306
            - Source: web-server-SG *(The SG of the web server)*

      - The four security group has the next parameters:
       
         - Name: bastionHost-SG
         - Inboud rules:
            - Type: ssh
            - Port Range: 22
            - Source: MyIP
<hr>

4. I going to the AWS EC2 service and I launch an EC2 instance in the **PublicSubnet** with the next configurations
     - AMI: *Amazon Linux 2023*
     - Instance Type: *t2.micro*
     - Key Pair: associate a key pair
     - Network settings:
        - VPC
        - Public Subnet: enable *Public IP*
        - Associate the web server security group
     - Advanced details:
        - IAM instance profile: Associate the role created previously
        - User data: *copy the next following lines to the user data*
           ```
           #!/bin/bash
           sudo dnf install -y python3.9-pip
           pip install virtualenv
           sudo dnf install -y mariadb105-server
           sudo service mariadb start
           sudo chkconfig mariadb on
           pip install flask
           pip install mysql-connector-python
           pip install boto3
            ```
      - When the instance launch is finished, I connect to the terminal, and I clone this project using the respective URL:
        
           ```
           git clone URL
           ```
        
      - To run the web server, I run the next command in the directory where the app.py is located. You need to make sure that the security group has the appropriate port enabled.

               python3 -m virtualenv venv
               source venv/bin/activate
               python app.py 
               
      - The database is not configured. I'm going to directory named db and I run the next commands
        
                sudo chmod +x set-root-user.sh createdb.sh
                sudo ./set-root-user.sh
                sudo ./createdb.sh
      - You can check if the database was created running the next command:
        
                sudo mysql 
                show databases;
                use books_db;
                show tables;
                SELECT * FROM Books; 
        
      - The database is not configured in AWS RDS but in AWS EC2. So in the next step, I'm going to configure AWS RDS.
      
<hr>
   
5. I'm going to the AWS RDS to configure the relational database service.
   
   - I create a subnet group for privateSubnetA and privateSubnetB.
   - I create AWS RDS with the next parameters:       
   
      - Engine Type: MariaDB or MySQL
      - Templates: Free tier
        
         - Master username: the same user that you created in AWS System Manager
         - Master Password: the same password that you created in AWS System Manager.
         - Virtual Private Cloud (VPC): the VPC that was created in the step one. 
         - DB subnet group: the db subnet group created. 
         - Existing VPC security groups: Associate the database security group create in the step three.

         - When AWS RDS is finally created, I copy the RDS endpoint. You can update the /book/host parameter in AWS System Manager.
<hr>

6. In this step, I'll be migrating the database on AWS EC2 to AWS RDS.
   
   - From the terminal of the AWS EC2 instance, I run the next commands:
   - I check the connection to AWS RDS from AWS EC2
     
             mysql -u root -p --host rds-endpoint
             show databases;
   
   
   - I begin with the migration with the next commands:
   
             mysqldump --databases books_db -u root -p > bookDB.sql
             mysql -u root -p --host *rds-endpoint* < bookDB.sql
   
   - You can check if the migration was successful
   
             mysql -u root -p --host *rds-endpoint*
             show databases;
             show tables;
             SELECT * FROM Books; 
   
<hr>

7. Finally, you can test whether the application connects to the database in AWS RDS.
   
