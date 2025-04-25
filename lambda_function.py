import boto3
from datetime import datetime, timedelta

# AWS Clients
rds = boto3.client('rds')
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')
ssm = boto3.client('ssm')

# Constants
DB_INSTANCE_ID = 'dynamicload-db'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:311141522259:rds-scaling-alerts'

# Fetch parameter from Systems Manager Parameter Store
def get_parameter(name):
    return int(ssm.get_parameter(Name=name)['Parameter']['Value'])

# Send SNS Notification
def send_notification(message):
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='RDS Auto Scaling Alert',
        Message=message
    )

def lambda_handler(event, context):
    try:
        # Read thresholds from Parameter Store
        min_storage = get_parameter('/rds-scaler/min-storage')
        max_storage = get_parameter('/rds-scaler/max-storage')
        storage_step = get_parameter('/rds-scaler/storage-step')
        min_iops = get_parameter('/rds-scaler/min-iops')
        max_iops = get_parameter('/rds-scaler/max-iops')
        iops_step = get_parameter('/rds-scaler/iops-step')

        print("Fetched thresholds successfully from SSM Parameter Store.")

        # Get FreeStorageSpace metric
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

        # Get ReadIOPS and WriteIOPS metrics
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

        if not metric_storage['Datapoints']:
            print("No storage metric data available.")
            return {'statusCode': 200, 'body': 'No metrics'}

        # Parse Metrics
        free_space_bytes = metric_storage['Datapoints'][0]['Average']
        free_space_gb = free_space_bytes / (1024 ** 3)

        avg_read_iops = metric_read_iops['Datapoints'][0]['Average'] if metric_read_iops['Datapoints'] else 0
        avg_write_iops = metric_write_iops['Datapoints'][0]['Average'] if metric_write_iops['Datapoints'] else 0
        total_avg_iops = avg_read_iops + avg_write_iops

        print(f"Free storage space: {free_space_gb:.2f} GB")
        print(f"Total average IOPS: {total_avg_iops:.2f}")

        # Get current DB config
        db_info = rds.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_ID)
        current_allocated = db_info['DBInstances'][0]['AllocatedStorage']
        current_iops = db_info['DBInstances'][0].get('Iops', min_iops)

        print(f"Current allocated storage: {current_allocated} GB")
        print(f"Current provisioned IOPS: {current_iops}")

        # Threshold calculations
        threshold_20 = current_allocated * 0.2
        threshold_80 = current_allocated * 0.8
        iops_threshold_high = current_iops * 0.7
        iops_threshold_low = current_iops * 0.3

        modify_needed = False
        modify_params = {'DBInstanceIdentifier': DB_INSTANCE_ID, 'ApplyImmediately': True}

        # Storage Scaling Logic
        if free_space_gb < threshold_20 and current_allocated < max_storage:
            new_allocated = current_allocated + storage_step
            modify_params['AllocatedStorage'] = new_allocated
            print(f"Will increase storage to {new_allocated} GB")
            send_notification(f"Scaling up RDS {DB_INSTANCE_ID} storage from {current_allocated} GB to {new_allocated} GB.")
            modify_needed = True

        elif free_space_gb > threshold_80 and current_allocated > min_storage:
            new_allocated = max(min_storage, current_allocated - storage_step)
            if new_allocated != current_allocated:
                modify_params['AllocatedStorage'] = new_allocated
                print(f"Will decrease storage to {new_allocated} GB")
                send_notification(f"Scaling down RDS {DB_INSTANCE_ID} storage from {current_allocated} GB to {new_allocated} GB.")
                modify_needed = True

        # IOPS Scaling Logic
        if total_avg_iops > iops_threshold_high and current_iops < max_iops:
            new_iops = current_iops + iops_step
            modify_params['Iops'] = new_iops
            print(f"Will increase IOPS to {new_iops}")
            send_notification(f"Scaling up RDS {DB_INSTANCE_ID} IOPS from {current_iops} to {new_iops}.")
            modify_needed = True

        elif total_avg_iops < iops_threshold_low and current_iops > min_iops:
            new_iops = max(min_iops, current_iops - iops_step)
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

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        send_notification(f"RDS Scaler Error: {str(e)}")
        return {'statusCode': 500, 'body': str(e)}
