# S3 File Upload Trigger with AWS Lambda

This project reacts to S3 file uploads by sending alerts and saving metadata.

## 🔧 How It Works
1. Upload a file to S3
2. Lambda gets triggered
3. It sends:
   - Slack message
   - SNS email
   - Stores file info in DynamoDB

## 🧱 Services Used
- S3 (triggers Lambda)
- Lambda (main logic)
- SNS (email notification)
- Slack Webhook (chat alert)
- DynamoDB (file metadata)

## 📑 DynamoDB Table
- Name: `s8ik-s3-upload-metadata`
- Partition Key: `fileName`

## 🛠 Setup Steps
1. Create an S3 bucket (enable versioning + encryption)
2. Create SNS topic and confirm email
3. Set up Slack webhook
4. Create DynamoDB table
5. Deploy Lambda with:
   - Environment vars:
     - `https://hooks.slack.com/services/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`
     - `arn:aws:sns:us-east-1:533267247980:s8ikoyi-s3-critical-upload-notifications`
     - `s8ik-s3-upload-metadata`
6. Add S3 trigger to Lambda for "PUT" events

## ✅ Test It
- Upload a file to S3
- Check Slack, email, and DynamoDB

