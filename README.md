# gcp-permission-change-notification-to-google-chat
This project setup monitoring and notification system that sends notifications about permission change happens in GCP projects to Google Chat group.


## How to set up in your environment?

### Step 1: Clone the repository


`git clone https://github.com/sivakumar1409/gcp-permission-change-notification-to-google-chat.git`

### Step 2: Install gcloud and set it up

Check whether gcloud is installed:
`gcloud --version`

If you see error message, install gcloud using the instructions found here: 
https://cloud.google.com/sdk/docs/install

Run `gcloud auth login`


### Step 3: Run the below command
`sh scripts/deploy.sh`


## Note: Please make sure the user who runs the scripts have the below permissions.

Logging Admin
Pub/Sub Admin
Cloud Run Admin
Cloud Functions Admin
Service Account Admin
Pub/Sub Subscriber
