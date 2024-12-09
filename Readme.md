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

# System Requirements  
- Python 3.8 or later  
- Docker (for containerized deployment)  
- Google Cloud SDK (for deployment to Google Cloud Run)  
---
# Preparation and Prerequisites

1. **Google Cloud Project**  
   - Create or select an existing project in the [Google Cloud Console](https://console.cloud.google.com).  

2. **Google Cloud Secret Manager**  
   - Store sensitive data like `jwt_secret_key`, `database_url`, and `gcs_service_account_key` in Google Cloud Secret Manager.  

3. **Database Setup**  
   - Set up your database (SQLite, PostgreSQL, or MySQL) and note the connection string.  

4. **Environment Variables**  
   - Create a `.env` file in your project directory with the following variables:  
     ```dotenv  
     JWT_SECRET_KEY=your_secret_key  
     DATABASE_URL=your_database_url  
     GCS_SERVICE_ACCOUNT_KEY=path_to_your_service_account_key.json  
     ```  


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
3. Running the FastAPI Application
Update the run configuration in `main.py`:
``` python
port = int(os.environ.get('PORT', 8000))  # Use any desired port number
print(f"Listening to http://localhost:{port}")
uvicorn.run(app, host='localhost', port=port)
```
4. Start the local server using the following command:
``` python
uvicorn main:app --reload
```
5. Accessing the API
Visit [http://localhost:8000](http://localhost:8000) in your browser or use tools like Postman to interact with the API. 

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
