# Authentication API

This API is designed to make it easier to implement login and registration features in your application without starting from scratch. It’s built with JWT (JSON Web Token) authentication, ensuring security and modern standards. The API is modular and can be easily customized according to your application's needs. In addition to user authentication, it also includes endpoints for managing products and searching ingredients, making it a versatile solution for various use cases.

---

## Features 
- User registration and login functionality.
- JWT-based authentication.
- Secure database handling with SQLAlchemy.
- Easy-to-use API endpoints.
- Dockerized for smooth deployment.

---

# API Documentation

The complete API documentation can be accessed through the following [this link](https://drive.google.com/file/d/1j-jXamL1wMGLNgorz5kuiBMXJwhCryzu/view?usp=sharing).

---

# Preparation and Prerequisites

 Create Google Cloud Project
- Open [Google Cloud Console](https://console.cloud.google.com) and create a new project or use an existing one for Firebase.

 Firebase Service Account
- **Generate Service Account**: In Firebase Console, go to Project Settings > Service Accounts, create a service account, and store the key in Secret Manager as `firebase_sak`.

 Firebase Configuration
- **Web App Configuration**: In Firebase Console, create a web app, then copy the `firebaseConfig` and modify it to include `"databaseURL": ""`.
- Save the modified config in Secret Manager as `firebase_config`.

 Cloud Storage Service Account
- Create a service account for Cloud Storage and store the key in Secret Manager as `skinsift-user-profile_bucket_sak`.

 Create Storage Bucket
- Set up a public bucket and grant the service account the **Storage Admin** role.

## Code Setup (Local Development)

## Google Cloud SDK
- **Install and authenticate**:
   Install Google Cloud SDK:  
     ```bash
     curl https://sdk.cloud.google.com | bash
     ```
   Initialize the SDK:  
     ```bash
     gcloud init
     ```
   Authenticate:  
     ```bash
     gcloud auth application-default login
     ```

# Local Development Setup without Secret Manager

If you prefer not to use a secret manager for local development, follow these steps:

 1: Adding Firebase Service Account

  1. Download the Firebase Service Account Key (JSON file) and place it in the same directory as your main Python file.
  2. Define the path to the Firebase Service Account file in your code:
   ```python
   firebase_sak_path = 'your_firebase_sak_file.json'  # Replace with your actual file name
 2. Updating Firebase Configuration
Replace the firebaseConfig variable with the Firebase configuration values directly in your code:
```python
firebaseConfig = {
    "apiKey": "yourAPIkey",
    "authDomain": "XXXX.firebaseapp.com",
    "projectId": "xxxxxxxxx",
    "storageBucket": "xxxxxxxx",
    "messagingSenderId": "xxxxxxxxxx",
    "appId": "xxxxxxxxxx",
    "databaseURL": ""
}
```
---
 3. Adding Cloud Storage Service Account
Place the Cloud Storage Service Account Key (JSON file) in the same folder as the main Python file.
Define the path to the Cloud Storage Service Account file in your code:
```python
key = 'your_bucket_service_account_key.json'  # Update with the actual file name
```

 4. Code Adjustments
- Update your code to use the defined firebaseSak and key variables for Firebase and Cloud Storage interactions.

Important Notes
Security Risk: This approach is not secure because it stores sensitive keys and configurations directly in the code. Avoid using this method in production environments.
Best Practices: Always use secure methods like Google Cloud Secret Manager or environment variables for managing sensitive data.

# Running the Application Locally
---
1. Cloning the Repository

Follow these steps to clone the repository and navigate to the project folder:

```bash
git clone <repository_url>
cd <project_folder>
```
2. Installing Requirements
Install the required dependencies using pip:
```
pip install -r requirements.txt
```
3. Modifying Access to Secret Manager
- Open the `main.py` file
- Locate the following sections:
``` python
firebaseSak = access_secret_version('YOUR_PROJECT_ID', 'firebase_sak', '1')
firebaseConfig = access_secret_version('YOUR_PROJECT_ID', 'firebase_config', '1')
key = access_secret_version('YOUR_PROJECT_ID', 'scancare-user-profile_bucket_sak', '1')
Replace YOUR_PROJECT_ID with your Google Cloud project ID.
```
4. Running the FastAPI Application
Update the run configuration in `main.py`:
``` python
port = int(os.environ.get('PORT', 8000))  # Use any desired port number
print(f"Listening to http://localhost:{port}")
uvicorn.run(app, host='localhost', port=port)
```
5. Start the local server using the following command:
``` python
uvicorn main:app --reload
```
6. Accessing the API
Use the provided API endpoints as documented earlier to interact with the application.

Ensure you have the appropriate permissions and credentials set up for accessing Google Cloud resources.
Refer to the project documentation for additional details or troubleshooting steps.

# Deploying the Application to Cloud Run
``` bash # Cloning the Repository
git clone <repository_url>

# Change to the destined directory
cd <project_folder>

# Create a Docker Artifact Repository in a specified region
gcloud artifacts repositories create YOUR_REPOSITORY_NAME --repository-format=docker --location=YOUR_REGION

# Build Docker image for the ML API
docker buildx build --platform linux/amd64 -t YOUR_IMAGE_PATH:YOUR_TAG --build-arg PORT=8080 .

# Push the Docker image to the Artifact Repository
docker push YOUR_IMAGE_PATH:YOUR_TAG

# Deploy the Docker image to Cloud Run with allocated memory
gcloud run deploy --image YOUR_IMAGE_PATH:YOUR_TAG --memory 3Gi

# Fetching the service account associated with the newly deployed Cloud Run service
SERVICE_ACCOUNT=$(gcloud run services describe YOUR_SERVICE_NAME --platform=managed --region=YOUR_REGION --format="value(serviceAccountEmail)")

# Grant necessary IAM roles to the service account linked to the Cloud Run service
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member=serviceAccount:${SERVICE_ACCOUNT} --role=roles/secretmanager.secretAccessor

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member=serviceAccount:${SERVICE_ACCOUNT} --role=roles/cloudsql.client
``` 
