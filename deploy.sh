#!/bin/bash

# ==============================================================================
# Antigravity Agent Spec-Driven Deployment Script
# Target: Google Cloud Platform (Enterprise Stack)
# Services: Cloud Run, Pub/Sub, Firestore, Vertex AI
# ==============================================================================

PROJECT_ID="your-google-cloud-project-id"
SERVICE_NAME="stadiumsense-ai"
REGION="us-central1"
TOPIC_NAME="stadium-telemetry"

echo "🚀 Initiating Antigravity Enterprise Deployment for $PROJECT_ID..."

# 1. Enable Required APIs
echo "Enabling GCP APIs (Pub/Sub, Firestore, Vertex AI, Cloud Run)..."
gcloud services enable \
  run.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  --project $PROJECT_ID

# 2. Provision Pub/Sub Topic
echo "Provisioning Pub/Sub topic: $TOPIC_NAME..."
gcloud pubsub topics create $TOPIC_NAME --project $PROJECT_ID || echo "Topic already exists."

# 3. Provision Firestore Database
echo "Provisioning Firestore native database..."
gcloud firestore databases create --location=$REGION --type=firestore-native --project $PROJECT_ID || echo "Database already exists."

# 4. Build and Deploy to Cloud Run
echo "Deploying to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --project $PROJECT_ID \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="API_BASE_URL=http://localhost:8000,PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
  --port 8501 \
  --memory 1Gi \
  --cpu 1

echo "✅ Enterprise Deployment completed successfully by Antigravity Agent."
