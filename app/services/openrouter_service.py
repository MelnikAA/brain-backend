import requests
import json
import base64
from PIL import Image
from dotenv import load_dotenv
import os
from app.core.config import settings
import io
import logging
import re
from io import BytesIO
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class OpenRouterService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        
        # Используем фиксированный URL API
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        logger.debug(f"OpenRouterService initialized with API URL: {self.api_url}")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "brainCHECK"
        }

    def _encode_image(self, image_file: BytesIO) -> str:
        """Кодирует изображение в base64"""
        return base64.b64encode(image_file.getvalue()).decode('utf-8')

    def _clean_text(self, text: str) -> str:
        """Очищает текст от некорректных символов и форматирования"""
        # Заменяем все возможные переносы строк на пробелы
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Удаляем все символы, кроме русских букв, цифр и знаков препинания
        text = re.sub(r'[^\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F0-9\s.,!?;:()\-]', '', text)
        
        # Заменяем множественные пробелы на один
        text = ' '.join(text.split())
        
        # Удаляем пробелы в начале и конце
        text = text.strip()
        
        # Исправляем грамматические ошибки
        text = re.sub(r'([а-яА-Я])\1{2,}', r'\1', text)  # Удаляем повторяющиеся буквы
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # Убираем пробелы перед знаками препинания
        text = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1', text)  # Убираем повторяющиеся знаки препинания
        
        # Исправляем специфические ошибки
        text = text.replace('или реже, воспалительныеинфекционные', 'или реже, воспалительные/инфекционные')
        text = text.replace('Т2', 'Т2/FLAIR')
        text = text.replace('очевидно, с признаками', 'с признаками')
        text = text.replace('высоко подозрительно', 'вызывает подозрение')
        text = text.replace('требуется дальнейшее', 'необходимо дополнительное')
        text = text.replace('иили', 'и/или')
        text = text.replace('перитуморальный', 'перифокальный')
        text = text.replace('масс-эффект', 'объемный эффект')
        text = text.replace('высокоподозрительным', 'вызывает подозрение')
        
        # Удаляем лишние пробелы после знаков препинания
        text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
        
        # Удаляем пробелы перед знаками препинания
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Удаляем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем пробелы в начале и конце
        text = text.strip()
        
        # Исправляем некорректные последовательности
        text = text.replace('2,,', 'Т2/FLAIR,')
        text = text.replace('вероятно ', 'вероятно, ')
        
        return text

    def _validate_medical_terms(self, text: str) -> str:
        """Проверяет и исправляет медицинские термины"""
        # Словарь корректных медицинских терминов
        medical_terms = {
            "анизоглотсность": "анизотропия",
            "плевралное": "субарахноидальное",
            "волевые включения": "патологические включения",
            "тактическая энцефалопатия": "токсическая энцефалопатия",
            "остеволеврит": "остеомиелит",
            "гидроцефалии": "гидроцефалия",
            "субдуральная гемотома": "субдуральная гематома",
            "гиперплазику": "гиперплазию",
            "контуровой": "контурной",
            "перегной": "перегиб",
            "вентрально": "вниз",
            "главном мозге": "головном мозге",
            "ассимиляционного неживотного мозга": "серого вещества мозга",
            "просонометрический": "постоянный",
            "нейрорхентеролога": "невролога",
            "миксомплектлификация": "миелинизация",
            "межнейральных": "нейродегенеративных",
            "тромботическим изменением": "сосудистыми изменениями",
            "покрытыми кровью капиллями": "расширенными сосудами",
            "гиперинтенсивные участки": "гиперинтенсивные образования",
            "гиперинтенсивное образование": "гиперинтенсивное образование",
            "отек окружающих тканей": "перифокальный отек",
            "неоднородная структура": "неоднородная структура",
            "глиомы высоких степеней злокачественности": "глиомы высокой степени злокачественности",
            "объемное образование": "объемное образование",
            "дифференциальной диагностики": "дифференциальной диагностики",
            "контрастное усиление": "контрастное усиление",
            "некротических изменений": "некротических изменений",
            "метастаз солидной опухоли": "метастаз солидной опухоли",
            "центральной нервной системы": "центральной нервной системы",
            "внутримозговых объемных процессов": "внутримозговых объемных образований",
            "неоднородное накопление контраста": "неравномерное накопление контраста",
            "перитуморальный отек": "перифокальный отек",
            "масс-эффект": "объемный эффект"
        }
        
        # Заменяем некорректные термины
        for incorrect, correct in medical_terms.items():
            text = text.replace(incorrect, correct)
            
        return text

    def _validate_json_structure(self, data: Dict[str, Any]) -> None:
        """Проверяет структуру JSON на соответствие требованиям"""
        required_fields = {
            "has_tumor": bool,
            "confidence": (int, float),
            "explanation": dict
        }
        
        explanation_fields = {
            "visual_description": str,
            "analysis": str,
            "recommendations": str,
            "medical_context": str
        }
        
        # Проверяем основные поля
        for field, field_type in required_fields.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(data[field], field_type):
                raise ValueError(f"Invalid type for field {field}: expected {field_type}, got {type(data[field])}")
        
        # Проверяем поля в explanation
        for field, field_type in explanation_fields.items():
            if field not in data["explanation"]:
                raise ValueError(f"Missing required field in explanation: {field}")
            if not isinstance(data["explanation"][field], str):
                raise ValueError(f"Invalid type for explanation field {field}: expected str, got {type(data['explanation'][field])}")

    def _fix_json(self, content: str) -> str:
        """Исправляет некорректный JSON"""
        # Удаляем лишние фигурные скобки
        content = re.sub(r'}\s*{', ',', content)
        # Удаляем лишние запятые перед закрывающими скобками
        content = re.sub(r',\s*}', '}', content)
        # Удаляем лишние запятые перед закрывающими квадратными скобками
        content = re.sub(r',\s*]', ']', content)
        return content

    def analyze_image(self, image_file: BytesIO) -> Dict[str, Any]:
        """Анализирует изображение через OpenRouter API"""
        try:
            # Кодируем изображение
            base64_image = self._encode_image(image_file)
            logger.debug("Image encoded successfully")
            
            # Формируем запрос
            payload = {
                "model": "google/gemini-2.5-flash-preview-05-20",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Проанализируй это МРТ-изображение головного мозга. Определи, есть ли признаки опухоли или других патологий.

Верни ответ ТОЛЬКО в формате JSON со следующей структурой:
{
  "has_tumor": true/false,
  "confidence": число от 0 до 1,
  "explanation": {
    "visual_description": "описание того, что видно на изображении",
    "analysis": "анализ обнаруженных признаков",
    "recommendations": "рекомендации по дальнейшим действиям",
    "medical_context": "медицинский контекст"
  }
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }

            # Отправляем запрос
            logger.debug("Sending request to OpenRouter API")
            response = requests.post(
                url=self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            logger.debug(f"Response status code: {response.status_code}")
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Извлекаем контент из ответа
            response_data = response.json()
            if not response_data.get("choices"):
                raise ValueError("No choices in response")
                
            content = response_data["choices"][0]["message"]["content"]
            logger.debug(f"Raw content from API: {content}")
            
            # Очищаем контент от markdown-разметки
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            logger.debug(f"Content after markdown cleanup: {content}")
            
            # Исправляем JSON
            content = self._fix_json(content)
            logger.debug(f"Content after JSON fix: {content}")
            
            # Парсим JSON
            try:
                result = json.loads(content)
                logger.debug(f"Successfully parsed JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Content that failed to parse: {content}")
                raise ValueError(f"Invalid JSON in response: {str(e)}")
            
            # Валидируем структуру JSON
            try:
                self._validate_json_structure(result)
                logger.debug("JSON structure validation passed")
            except ValueError as e:
                logger.error(f"JSON structure validation failed: {str(e)}")
                raise ValueError(f"Invalid JSON structure: {str(e)}")
            
            # Очищаем текстовые поля
            if "explanation" in result:
                for key in result["explanation"]:
                    if isinstance(result["explanation"][key], str):
                        logger.debug(f"Cleaning text for field: {key}")
                        # Сначала очищаем от некорректных символов
                        text = self._clean_text(result["explanation"][key])
                        logger.debug(f"Text after cleaning: {text}")
                        # Затем проверяем медицинские термины
                        text = self._validate_medical_terms(text)
                        logger.debug(f"Text after medical terms validation: {text}")
                        result["explanation"][key] = text
            
            # Формируем финальный результат
            try:
                final_result = {
                    "description": result["explanation"]["visual_description"],
                    "conclusions": result["explanation"]["analysis"],
                    "recommendations": result["explanation"]["recommendations"],
                    "confidence": float(result["confidence"]),
                    "has_tumor": bool(result["has_tumor"]),
                    "medical_context": result["explanation"]["medical_context"]
                }
                logger.debug(f"Final result created successfully: {json.dumps(final_result, indent=2, ensure_ascii=False)}")
            except (KeyError, TypeError) as e:
                logger.error(f"Error creating final result: {str(e)}")
                raise ValueError(f"Error creating final result: {str(e)}")
            
            return final_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise ValueError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in analyze_image: {str(e)}")
            logger.exception("Full traceback:")
            raise ValueError(f"Error analyzing image: {str(e)}")

# Создаем экземпляр сервиса
openrouter_service = OpenRouterService() 