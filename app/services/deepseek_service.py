import requests
import json
import base64
from PIL import Image
from dotenv import load_dotenv
import os
from app.core.config import settings

class DeepSeekService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        self.api_url = settings.DEEPSEEK_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def encode_image(self, image_path: str) -> str:
        """Кодирует изображение в base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    def analyze_image(self, image_path: str) -> dict:
        """Анализирует изображение с помощью DeepSeek API"""
        try:
            # Кодируем изображение в base64
            image_base64 = self.encode_image(image_path)
            
            # Подготавливаем данные для запроса
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": "Analyze this brain MRI image for tumor detection. Provide the prediction result and confidence score."
                    }
                ],
                "images": [image_base64],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            print("Отправляем запрос к API с данными:", json.dumps(payload, indent=2))
            
            # Отправляем запрос к API
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            # Если получили ошибку, выводим детали ответа
            if response.status_code != 200:
                print("Ошибка API:", response.status_code)
                print("Ответ API:", response.text)
            
            # Проверяем ответ
            response.raise_for_status()
            result = response.json()
            
            print("Получен ответ от API:", json.dumps(result, indent=2))
            
            # Извлекаем результат из ответа API
            prediction_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Парсим результат для получения предсказания и уверенности
            # Предполагаем, что API возвращает результат в формате:
            # "Prediction: [result] (Confidence: [score]%)"
            prediction = "Unknown"
            confidence = 0.0
            
            if "Prediction:" in prediction_text:
                try:
                    prediction = prediction_text.split("Prediction:")[1].split("(")[0].strip()
                    confidence_str = prediction_text.split("Confidence:")[1].split("%")[0].strip()
                    confidence = float(confidence_str) / 100.0
                except:
                    pass
            
            return {
                "prediction_result": prediction,
                "confidence": confidence,
                "segmentation_mask": None  # DeepSeek API не предоставляет маску сегментации
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Ответ сервера: {e.response.text}")
            raise Exception(f"Ошибка при обращении к DeepSeek API: {str(e)}")
        except Exception as e:
            print(f"Общая ошибка: {str(e)}")
            raise Exception(f"Ошибка при обработке изображения: {str(e)}")

# Создаем экземпляр сервиса
deepseek_service = DeepSeekService() 