import requests
import json
import base64
from PIL import Image
from dotenv import load_dotenv
import os
from app.core.config import settings

class OpenRouterService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        self.api_url = settings.OPENROUTER_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Brain Tumor Detection"
        }
        
    def encode_image(self, image_path: str) -> str:
        """Кодирует изображение в base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    def analyze_image(self, image_path: str) -> dict:
        """Анализирует изображение с помощью OpenRouter API"""
        try:
            # Кодируем изображение в base64
            image_base64 = self.encode_image(image_path)
            
            # Подготавливаем данные для запроса
            payload = {
                "model": "anthropic/claude-3-opus-20240229",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this brain MRI image for tumor detection. Provide the prediction result and confidence score in the following format: 'Prediction: [result] (Confidence: [score]%)'"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
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
                "segmentation_mask": None  # OpenRouter API не предоставляет маску сегментации
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Ответ сервера: {e.response.text}")
            raise Exception(f"Ошибка при обращении к OpenRouter API: {str(e)}")
        except Exception as e:
            print(f"Общая ошибка: {str(e)}")
            raise Exception(f"Ошибка при обработке изображения: {str(e)}")

# Создаем экземпляр сервиса
openrouter_service = OpenRouterService() 