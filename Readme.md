# Secure File OPS

## Overview
**Secure File OPS** is a highly secure file-sharing system developed using FastAPI and MongoDB. It is built to manage and share files with strict role-based access control, ensuring that only authorized users can perform specific actions. The system supports two primary user roles:

- **Ops Users**: Authorized to upload specific file types.
- **Client Users**: Can register, verify their accounts, and securely download files.

## Routes
![image](https://github.com/user-attachments/assets/63694885-2d91-448a-b6e1-ce20e9683e2c)


## Technology Stack
- **FastAPI**: For building the high-performance API server.
- **MongoDB**: Used as the database for user and file information storage. It is deployed separately for better scalability.
- **JWT**: Utilized for secure user authentication and role-based access control.
- **File.io**: Used for secure cloud storage in this project. In a real production environment, services like AWS S3 or Google Cloud Storage can be used as per requirements.
- **Brevo**: Integrated for sending actual verification emails with a verification link. This setup is also production-ready, though AWS SES could be an alternative.
- **Dockerized**: The application is containerized for easy deployment and scalability.
- **Deployment**: The web service is deployed at the following URL: [Secure-File-Ops](https://secure-file-ops.onrender.com/docs)


## Security Highlights
- **JWT Authentication**: Ensures secure, role-based access to the system.
- **Encrypted Download Links**: Time-limited and encrypted URLs prevent unauthorized file access.
- **File Type Restrictions**: Only specified file types can be uploaded to prevent malicious content.

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB instance
- Docker (if you plan to use the Dockerized version)
- Install dependencies from `requirements/base.txt` and `requirements/prod.txt` for production setups

### Installation

- Clone the repository:

    ```bash
    git clone https://github.com/Addy-codes/secure-file-ops.git
    cd secure-file-ops
    ```
    
### Docker Setup

1. Build the Docker image:

    ```bash
    docker build -t secure-file-ops .
    ```

2. Run the Docker container:

    ```bash
    docker run -d -p 8000:8000 secure-file-ops
    ```

### Local Setup

2. Install dependencies:

    ```bash
    pip install -r ./requirements/base.txt
    ```

3. Set up your .env file according to the example.env file present in the root of the project

4. Run the FastAPI server:

    ```bash
    uvicorn main:app --reload
    ```

## Testing
Comprehensive test files are located in the `tests` module. You can run the test suite using:

```bash
pytest test/test_auth.py
pytest test/test_file.py
```

## Dependency Management
- Dependencies for base and production environments are kept separate for better environment control. Install production dependencies using:

    ```bash
    pip install -r requirements-prod.txt
    ```

---

This project prioritizes security at every step, ensuring files are uploaded, stored, and accessed with strict authorization and encryption measures. The system is scalable and adaptable to production environments with cloud-based solutions such as AWS S3 or GCP, and email services like AWS SES.
