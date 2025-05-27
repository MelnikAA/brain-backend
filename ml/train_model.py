import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import glob

# Пути к данным
train_yes_dir = 'data/yes'
train_no_dir = 'data/no'

# Трансформации для изображений
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

class BrainTumorDataset(Dataset):
    def __init__(self, yes_dir, no_dir, transform=None):
        self.yes_images = glob.glob(os.path.join(yes_dir, '*.jpg')) + glob.glob(os.path.join(yes_dir, '*.png'))
        self.no_images = glob.glob(os.path.join(no_dir, '*.jpg')) + glob.glob(os.path.join(no_dir, '*.png'))
        self.images = self.yes_images + self.no_images
        self.labels = [1] * len(self.yes_images) + [0] * len(self.no_images)
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

# Загрузка датасета
train_dataset = BrainTumorDataset(train_yes_dir, train_no_dir, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Простая CNN
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 16 * 16, 128),
            nn.ReLU(),
            nn.Linear(128, 2)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Обучение
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {running_loss/len(train_loader):.4f}")

# Сохранение модели
os.makedirs('ml', exist_ok=True)
torch.save(model.state_dict(), "ml/brain_tumor_cnn.pth")
print("Модель сохранена в ml/brain_tumor_cnn.pth") 