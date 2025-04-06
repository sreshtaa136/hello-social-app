# 🌐 Hello Social

**Hello Social** is a lightweight, scalable social media platform built using **Python Flask** and **AWS**. It allows users to create, delete, and share notes and images with customizable visibility (public/private). 

The project is designed for performance and scalability, leveraging key AWS services like:
- **Amazon DynamoDB** – NoSQL database for storing user data.
- **Amazon S3** – For image storage and retrieval.
- **AWS Lambda** – For serverless logic like scheduled cleanups or media processing.
- **Amazon CloudFront** – To deliver content via a CDN for fast global access.
- **AWS Elastic Beanstalk** – To deploy and manage the Flask app.
- **Amazon EC2** – For compute resources.
- **AWS CodePipeline** – For CI/CD automation.

---

## 🚀 Features

- User authentication and session management
- Create, delete, and share notes
- Upload and manage images
- Public or private visibility settings
- Scalable backend using AWS services
- Fully automated CI/CD with AWS CodePipeline

---

## ⚙️ Environment Setup

This project uses environment variables to manage AWS credentials and region. **Do not hardcode credentials into your source code.**

### 🔐 Add a `.env` file in your project root:
```bash
AWS_ACCESS_KEY_ID=your_access_key_id 
AWS_SECRET_ACCESS_KEY=your_secret_access_key 
AWS_DEFAULT_REGION=ap-southeast-2
```

---

## 🧪 Running Locally

Clone the repository:

```bash
git clone https://github.com/your-username/hello-social.git
cd hello-social
```

Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

Load the .env file:
```bash
from dotenv import load_dotenv
load_dotenv()
```

Start the Flask app:
```bash
export FLASK_APP=application.py
flask run
```
