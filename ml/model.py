import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        
        # Размер после трёх MaxPool2d с stride=2: 224 -> 112 -> 56 -> 28
        # 64 канала * 28 * 28 = 50176
        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(50176, 128),  # Изменено с 16384 на 50176
            nn.ReLU(inplace=True),
            nn.Linear(128, 2)
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

class UNet(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        super(UNet, self).__init__()
        # Энкодер
        self.enc1 = nn.Sequential(
            nn.Conv2d(n_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True)
        )
        self.enc2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        self.enc3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        
        # Декодер
        self.dec2 = nn.Sequential(
            nn.Conv2d(128, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        self.dec1 = nn.Sequential(
            nn.Conv2d(64, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True)
        )
        
        # Выходной слой
        self.final = nn.Conv2d(32, n_classes, kernel_size=1)
        
        # Слои апсемплинга
        self.up1 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.up2 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)

    def forward(self, x):
        # Энкодер
        x1 = self.enc1(x)
        x2 = self.enc2(F.max_pool2d(x1, 2))
        x3 = self.enc3(F.max_pool2d(x2, 2))
        
        # Декодер
        x = self.up1(x3)
        x = self.dec2(x)
        x = self.up2(x)
        x = self.dec1(x)
        
        # Выходной слой
        x = self.final(x)
        return x

class BrainTumorModel:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Инициализация простой модели
        self.simple_model = SimpleCNN().to(self.device)
        self.simple_model.load_state_dict(torch.load('ml/brain_tumor_cnn.pth', map_location=self.device))
        self.simple_model.eval()
        
        # Инициализация UNet модели
        self.unet_model = UNet().to(self.device)
        self.unet_model.load_state_dict(torch.load('ml/unet_brain_segmentation.pth', map_location=self.device))
        self.unet_model.eval()
        
        # Трансформации для изображений
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Стандартные значения для ImageNet
        ])

    def preprocess_image(self, image_path):
        """Подготовка изображения для моделей"""
        image = Image.open(image_path).convert('RGB')  # Изменено с 'L' на 'RGB'
        image = self.transform(image)
        return image.unsqueeze(0).to(self.device)

    def predict_tumor(self, image_path):
        """Предсказание наличия опухоли"""
        image = self.preprocess_image(image_path)
        with torch.no_grad():
            output = self.simple_model(image)
            probabilities = F.softmax(output, dim=1)
            prediction = torch.argmax(probabilities, dim=1)
            confidence = probabilities[0][prediction].item()
        
        return {
            "has_tumor": bool(prediction.item()),
            "confidence": confidence
        }

    def segment_tumor(self, image_path):
        """Сегментация опухоли"""
        image = self.preprocess_image(image_path)
        with torch.no_grad():
            output = self.unet_model(image)
            mask = torch.sigmoid(output) > 0.5
            mask = mask.squeeze().cpu().numpy()
        
        return {
            "segmentation_mask": mask.tolist()
        }

    def analyze_image(self, image_path):
        """Полный анализ изображения"""
        tumor_prediction = self.predict_tumor(image_path)
        if tumor_prediction["has_tumor"]:
            segmentation = self.segment_tumor(image_path)
            return {
                "has_tumor": True,
                "confidence": tumor_prediction["confidence"],
                "segmentation_mask": segmentation["segmentation_mask"]
            }
        return tumor_prediction 