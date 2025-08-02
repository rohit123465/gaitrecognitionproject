import torch
import numpy as np
import json
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from gait_database import insert_gait_signature
import matplotlib.pyplot as plt


torch.manual_seed(42)
np.random.seed(42)

# Define Autoencoder model
class GaitAutoencoder(torch.nn.Module):
    def __init__(self, input_dim):
        super(GaitAutoencoder, self).__init__()
        # Encoder
        self.fc1 = torch.nn.Linear(input_dim, 128)
        self.fc2 = torch.nn.Linear(128, 64)
        self.fc3 = torch.nn.Linear(64, 32)  # Bottleneck layer containing the gait signature

        # Decoder
        self.fc4 = torch.nn.Linear(32, 64)
        self.fc5 = torch.nn.Linear(64, 128)
        self.fc6 = torch.nn.Linear(128, input_dim)

    def encode(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)  # Bottleneck layer
        return x

    def forward(self, x):
        x = self.encode(x)
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        x = self.fc6(x)  # Decoded output
        return x

# Function to load input data (joint positions)
def load_input_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    frames = data.get("frames", [])
    if not frames:
        raise ValueError("No frame data found in JSON file.")

    all_features = []

    for frame in frames:
        # Extract all available features
        joints = frame.get("joints", [])
        betas = frame.get("betas", [])
        global_orient = frame.get("global_orient", [])
        body_pose = frame.get("body_pose", [])

        # Convert to numpy arrays and flatten
        feature_vector = np.concatenate([
            np.array(joints).flatten(),
            np.array(betas).flatten(),
            np.array(global_orient).flatten(),
            np.array(body_pose).flatten()
        ])

        all_features.append(feature_vector)

    return all_features

# Dataset class
class GaitDataset(Dataset):
    def __init__(self, features):
        self.features = features

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32)

# Function to train autoencoder to generate gait signature
def train_autoencoder(file_path, num_epochs=100, batch_size=32, learning_rate=0.001, test_split=0.2):
    features = load_input_data(file_path)

    # Ensure all feature vectors have the same dimension
    input_dim = len(features[0])

    # Split dataset
    train_features, test_features = train_test_split(features, test_size=test_split, random_state=42)

    # Create Datasets and DataLoaders
    train_dataset = GaitDataset(train_features)
    test_dataset = GaitDataset(test_features)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    model = GaitAutoencoder(input_dim)
    model.train()

    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        for batch_data in train_loader:
            batch_data = batch_data.to(device)

            reconstructed = model(batch_data)

            loss = criterion(reconstructed, batch_data)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)

        model.eval()
        test_loss = 0.0
        with torch.no_grad():
            for batch_data in test_loader:
                batch_data = batch_data.to(device)
                reconstructed = model(batch_data)
                loss = criterion(reconstructed, batch_data)
                test_loss += loss.item()

        avg_test_loss = test_loss / len(test_loader)

        print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.4f}, Test Loss: {avg_test_loss:.4f}')

    store_gait_signature(model, test_dataset, device)

def store_gait_signature(model, test_dataset, device):
    model.eval()
    with torch.no_grad():
        all_signatures = []
        for i in range(len(test_dataset)):
            sample_gait = test_dataset[i].unsqueeze(0).to(device)
            gait_signature = model.encode(sample_gait) 
            all_signatures.append(gait_signature.cpu().numpy().flatten())

        all_signatures = np.array(all_signatures)

        # Ensure full array is printed
        np.set_printoptions(threshold=np.inf)

        person_id = insert_gait_signature(all_signatures)
