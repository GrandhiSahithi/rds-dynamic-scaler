
---

## 📦 Deployment Instructions

1. Deploy `lambda_function.py` to AWS Lambda.
2. Create an **SNS topic** (e.g., `rds-scaling-alerts`) and subscribe your email.
3. Create an **EventBridge rule** with a rate expression (`rate(5 minutes)`).
4. Attach IAM role to Lambda with:
   - `AmazonRDSFullAccess`
   - `CloudWatchReadOnlyAccess`
   - `AmazonSNSFullAccess` (or limited to your topic)
5. Monitor logs in CloudWatch and confirm email notifications.

---

## 🏆 Highlights

- 💡 **Serverless Automation**: No EC2, no containers — 100% managed infrastructure.
- 📊 **Cost Awareness**: Optimizes usage to reduce unnecessary AWS billing.
- 🔒 **Security First**: IAM roles follow least-privilege principles.
- 💬 **Event-Driven Architecture**: Based on metrics, not fixed logic.
- 📈 **Easily Extensible**: Can be enhanced with tagging, logging to S3, or alarm-based triggers.

---

## 👩‍💻 Author

**Sahithi Grandhi**  
Cloud | Data | DevOps Enthusiast  
[GitHub](https://github.com/yourusername) | [LinkedIn](https://www.linkedin.com/in/yourprofile)  

---

## 📢 Future Enhancements (Optional Ideas)

- Add **daily summary email report** (e.g., using a separate reporting Lambda).
- Use **AWS Systems Manager Parameter Store** for threshold configuration.
- Enable **multi-AZ deployment failover testing**.
- Integrate **CloudFormation** or **Terraform** for complete IaC provisioning.

---

## 📜 License

MIT License – You’re free to use, modify, and share this project. Just give credit 🙌
