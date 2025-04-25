import boto3
from datetime import datetime, timedelta

# AWS Clients
rds = boto3.client('rds')
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')

# Configuration
DB_INSTANCE_ID = 'dynamicload-db'

# Storage Configuration
MIN_STORAGE = 50  # GB
MAX_STORAGE = 100  # GB
STORAGE_STEP = 10  # GB

# IOPS Configuration
MIN_IOPS = 3000
MAX_IOPS = 12000
IOPS_STEP = 1000

# SNS Topic ARN
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:311141522259:rds-scaling-alerts'

def send_notification(message):
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='RDS Auto Scaling Alert',
        Message=message
    )

def lambda_handler(event, context):
    # Fetch FreeStorageSpace
    metric_storage = cloudwatch.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName='FreeStorageSpace',
        Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': DB_INSTANCE_ID}],
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average'],
        Unit='Bytes'
    )

    # Fetch ReadIOPS and WriteIOPS
    metric_read_iops = cloudwatch.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName='ReadIOPS',
        Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': DB_INSTANCE_ID}],
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )

    metric_write_iops = cloudwatch.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName='WriteIOPS',
        Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': DB_INSTANCE_ID}],
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )

    # Check if data available
    if not metric_storage['Datapoints']:
        print("No storage metric data available.")
        return {'statusCode': 200, 'body': 'No metrics'}

    # Get Storage Metrics
    free_space_bytes = metric_storage['Datapoints'][0]['Average']
    free_space_gb = free_space_bytes / (1024 ** 3)
    print(f"Free storage space: {free_space_gb:.2f} GB")

    # Get IOPS Metrics
    avg_read_iops = metric_read_iops['Datapoints'][0]['Average'] if metric_read_iops['Datapoints'] else 0
    avg_write_iops = metric_write_iops['Datapoints'][0]['Average'] if metric_write_iops['Datapoints'] else 0
    total_avg_iops = avg_read_iops + avg_write_iops
    print(f"Total average IOPS: {total_avg_iops:.2f}")

    # Get current instance configuration
    db_info = rds.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_ID)
    current_allocated = db_info['DBInstances'][0]['AllocatedStorage']
    current_iops = db_info['DBInstances'][0].get('Iops', MIN_IOPS)  # default 3000 if not explicitly set

    print(f"Current allocated storage: {current_allocated} GB")
    print(f"Current provisioned IOPS: {current_iops}")

    # Calculate thresholds
    threshold_20 = current_allocated * 0.2
    threshold_80 = current_allocated * 0.8
    iops_threshold_high = current_iops * 0.7
    iops_threshold_low = current_iops * 0.3

    modify_needed = False
    modify_params = {'DBInstanceIdentifier': DB_INSTANCE_ID, 'ApplyImmediately': True}

    # Storage Scaling Logic
    if free_space_gb < threshold_20 and current_allocated < MAX_STORAGE:
        new_allocated = current_allocated + STORAGE_STEP
        modify_params['AllocatedStorage'] = new_allocated
        print(f"Will increase storage to {new_allocated} GB")
        send_notification(f"Scaling up RDS {DB_INSTANCE_ID} storage from {current_allocated} GB to {new_allocated} GB.")
        modify_needed = True

    elif free_space_gb > threshold_80 and current_allocated > MIN_STORAGE:
        new_allocated = max(MIN_STORAGE, current_allocated - STORAGE_STEP)
        if new_allocated != current_allocated:
            modify_params['AllocatedStorage'] = new_allocated
            print(f"Will decrease storage to {new_allocated} GB")
            send_notification(f"Scaling down RDS {DB_INSTANCE_ID} storage from {current_allocated} GB to {new_allocated} GB.")
            modify_needed = True

    # IOPS Scaling Logic
    if total_avg_iops > iops_threshold_high and current_iops < MAX_IOPS:
        new_iops = current_iops + IOPS_STEP
        modify_params['Iops'] = new_iops
        print(f"Will increase IOPS to {new_iops}")
        send_notification(f"Scaling up RDS {DB_INSTANCE_ID} IOPS from {current_iops} to {new_iops}.")
        modify_needed = True

    elif total_avg_iops < iops_threshold_low and current_iops > MIN_IOPS:
        new_iops = max(MIN_IOPS, current_iops - IOPS_STEP)
        if new_iops != current_iops:
            modify_params['Iops'] = new_iops
            print(f"Will decrease IOPS to {new_iops}")
            send_notification(f"Scaling down RDS {DB_INSTANCE_ID} IOPS from {current_iops} to {new_iops}.")
            modify_needed = True

    # Perform modification if needed
    if modify_needed:
        rds.modify_db_instance(**modify_params)
        print("Modification API call made.")
    else:
        print("No scaling action needed.")

    return {
        'statusCode': 200,
        'body': f'Free space: {free_space_gb:.2f} GB, Allocated Storage: {current_allocated} GB, Provisioned IOPS: {current_iops}'
    }
