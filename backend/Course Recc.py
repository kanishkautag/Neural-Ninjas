# train_and_save_model.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import NearestNeighbors
import joblib
import os

# Set file paths
file_path = r'C:\Kanishka\My Programs\NMIMS Hackathon\udemy_courses.csv'
model_dir = 'model'
os.makedirs(model_dir, exist_ok=True)

# Load the data
print(f"Loading data from {file_path}")
df = pd.read_csv(file_path)
print(f"Loaded {len(df)} courses")

# Clean data
print("Cleaning data...")
numeric_cols = ['price', 'num_subscribers', 'num_reviews', 'num_lectures', 'content_duration']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Fill missing values
df = df.fillna({
    'price': 0,
    'num_subscribers': 0,
    'num_reviews': 0,
    'num_lectures': 0,
    'content_duration': 0,
    'level': 'All Levels',
    'subject': 'Other'
})

# Prepare features
print("Preparing features...")
level_encoder = LabelEncoder()
subject_encoder = LabelEncoder()

# Fit encoders
df['level_encoded'] = level_encoder.fit_transform(df['level'])
df['subject_encoded'] = subject_encoder.fit_transform(df['subject'])

# Create feature matrix
features = df[['level_encoded', 'subject_encoded']].values

# Add popularity features
subscribers_normalized = df['num_subscribers'] / df['num_subscribers'].max()
reviews_normalized = df['num_reviews'] / df['num_reviews'].max()
features = np.column_stack((features, subscribers_normalized.values, reviews_normalized.values))

print(f"Feature preparation completed. Feature shape: {features.shape}")

# Build KNN model
print("Building ML model...")
knn_model = NearestNeighbors(
    n_neighbors=50,
    algorithm='auto',
    metric='cosine'
)
knn_model.fit(features)
print("ML model built successfully")

# Save all necessary components
print("Saving model and data...")
joblib.dump(knn_model, os.path.join(model_dir, 'knn_model.joblib'))
joblib.dump(level_encoder, os.path.join(model_dir, 'level_encoder.joblib'))
joblib.dump(subject_encoder, os.path.join(model_dir, 'subject_encoder.joblib'))
joblib.dump(features, os.path.join(model_dir, 'features.joblib'))

# Save the dataframe
df.to_csv(os.path.join(model_dir, 'processed_courses.csv'), index=False)

print("Model and data saved successfully!")
