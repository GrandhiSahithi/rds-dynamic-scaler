# RDS Multi-AZ Failover Testing Guide

This document outlines the manual procedure to simulate an Amazon RDS Multi-AZ failover event, monitor its impact, and validate automatic recovery.

---

## 🛠️ Pre-Requisites

- RDS instance must have **Multi-AZ deployment** enabled.
- Lambda scaling function should be actively monitoring metrics.
- CloudWatch Logs enabled for Lambda and RDS.

---

## 🧪 Failover Test Procedure

1. Go to **AWS Console → Amazon RDS → Databases**.
2. Select your RDS instance (`dynamicload-db`).
3. Click **Actions → Reboot → Reboot with Failover** (check the box).
4. Confirm reboot.

---

## 🎯 What to Monitor

- **Database Downtime**
  - Try connecting to DB — measure downtime.
- **Lambda Function Behavior**
  - Check if auto-scaling Lambda triggers correctly post-failover.
- **CloudWatch Logs**
  - Verify that no scaling errors or metric gaps occur during/after failover.
- **SNS Notifications**
  - Ensure email notifications are still working if any scaling happens.

---

## 📝 Expected Observations

- Short downtime (~1–2 minutes) during failover.
- Database promoted to standby instance.
- No data loss or corruption.
- Lambda auto-scaling resumes normal behavior after failover.
- CloudWatch logs capture minor service interruptions gracefully.

---

## 📋 Test Results Log (Example)

| Test Step                | Observation                             | Result |
|---------------------------|-----------------------------------------|--------|
| Initiated Reboot Failover  | Instance status changed as expected    | Pass   |
| Database Connectivity     | Recovered within 90 seconds            | Pass   |
| Lambda Auto-Scaling       | No failures, resumed after recovery    | Pass   |
| SNS Notifications         | Received email alerts post-failover    | Pass   |

---

## 🔥 Notes

- Failover can only be tested once every few hours (per RDS limits).
- Always monitor application behavior carefully.
- Best practice: Enable enhanced monitoring for RDS if not already done.

---

## ✅ Conclusion

Multi-AZ failover testing ensures your RDS instance and connected serverless architecture can recover automatically from Availability Zone failures without manual intervention.

