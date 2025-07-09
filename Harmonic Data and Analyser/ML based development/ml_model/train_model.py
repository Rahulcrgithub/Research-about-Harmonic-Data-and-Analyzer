import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# Load the labeled dataset
df = pd.read_csv("harmonic_labeled_dataset.csv")

# Extract features and labels
X = df.iloc[:, 0:1000]  # Va_0 to Va_999
y = df["THD_class"]

# Encode class labels (Low=0, Medium=1, High=2)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Accuracy
acc = model.score(X_test, y_test)
print(f"Validation Accuracy: {acc * 100:.2f}%")

# Save model
with open("harmonic_model.pkl", "wb") as f:
    pickle.dump((model, label_encoder), f)

print("Model saved as harmonic_model.pkl")
