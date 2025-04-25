# 📈 Dynamic Auto-Scaling of RDS Storage and IOPS Using AWS Serverless Architecture

This project implements a fully serverless, event-driven solution on AWS to automatically monitor, evaluate, and dynamically scale Amazon RDS storage and provisioned IOPS based on real-time CloudWatch metrics, using Systems Manager Parameter Store for dynamic configurations.

Built for high-availability, cost-efficiency, and full automation, the system also supports disaster recovery testing with Multi-AZ failover and Infrastructure as Code provisioning using AWS CloudFormation.

---

## 🚀 Features

- ✅ **Real-Time Monitoring**: Continuously monitors `FreeStorageSpace`, `ReadIOPS`, and `WriteIOPS` via CloudWatch.
- ✅ **Dynamic Scaling**:
  - Storage scales up/down based on free space thresholds.
  - IOPS scales up/down based on workload activity.
- ✅ **Parameter Store Configuration**: Thresholds for storage and IOPS are read dynamically from AWS Systems Manager Parameter Store.
- ✅ **Proactive Alerts**: Sends detailed SNS email notifications for every scaling action.
- ✅ **High Availability Testing**: Supports Multi-AZ failover simulation and recovery validation.
- ✅ **Infrastructure as Code**: Starter CloudFormation template provided for quick deployment.

---

## 🛠️ Technology Stack

- **AWS Lambda** (Python 3.12)
- **Amazon RDS (SQL Server, gp3)**
- **Amazon CloudWatch Metrics**
- **Amazon Systems Manager Parameter Store**
- **Amazon SNS (Simple Notification Service)**
- **Amazon EventBridge Scheduler**
- **AWS IAM (Access control)**
- **AWS CloudFormation (Infrastructure as Code)**

---

## 🧠 Architecture Diagram

![Architecture](architecture/architecture-diagram.png)

---

## 📦 Deployment Instructions

1. Deploy `lambda_function/lambda_function.py` to AWS Lambda.
2. Create required **Parameters** in AWS Systems Manager Parameter Store using `parameter-store-setup/parameter-setup-commands.txt`.
3. Create an **SNS topic** (e.g., `rds-scaling-alerts`) and subscribe your email.
4. Create an **EventBridge rule** with a rate expression (`rate(5 minutes)`) to trigger Lambda.
5. Attach the necessary IAM policies to Lambda:
   - `AmazonRDSFullAccess`
   - `CloudWatchReadOnlyAccess`
   - `AmazonSNSFullAccess`
   - `AmazonSSMReadOnlyAccess`
6. (Optional) Deploy RDS and SNS via CloudFormation using `infrastructure/cloudformation-template.yaml`.
7. Monitor CloudWatch Logs and confirm SNS notifications.

---

## 📋 Project Structure

```
rds-dynamic-scaler/
├── README.md
├── lambda_function/
│   └── lambda_function.py
├── architecture/
│   └── architecture-diagram.png
├── parameter-store-setup/
│   └── parameter-setup-commands.txt
├── multi-az-testing/
│   └── failover-testing-guide.md
├── infrastructure/
│   └── cloudformation-template.yaml
├── sns-topic-example/
│   └── sns-topic-setup.txt
├── .gitignore
└── LICENSE
```

---

## 🏆 Highlights

- 💡 **Dynamic, Serverless Automation**: Fully cloud-native using only AWS managed services.
- 📊 **Cost Awareness**: Automatically adjusts resources to reduce AWS billing during low usage.
- 🔒 **Secure Architecture**: Fine-grained IAM policies; SSM Parameter Store for secrets/thresholds.
- 🌍 **High Availability Ready**: Includes Multi-AZ failover recovery validation.
- 🛠️ **Infrastructure as Code (IaC)**: Starter CloudFormation template provided for deployment.

---

## 📢 Future Enhancements (Optional Ideas)

- Add **daily summarized email reports** (automated Lambda reporting to SNS).
- Implement **dynamic EventBridge rules** for smarter scheduling.
- Extend CloudFormation template to fully automate Lambda, IAM, EventBridge setup.
- Build **CloudWatch Alarms and dashboards** for visual monitoring.

---

## 👩‍💻 Author

**Sahithi Grandhi**  
Cloud | Data | DevOps Enthusiast  

---

## 📜 License

MIT License – Feel free to use, modify, and share this project. Just give credit 🙌
