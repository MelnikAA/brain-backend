import requests
import json
import base64
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class QwenService:
    def __init__(self):
        self.api_key = os.getenv("API_QWEN_KEY")
        if not self.api_key:
            raise ValueError("API_QWEN_KEY environment variable is not set")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "brainCHECK"
        }
        
    def encode_image(self, image_path: str) -> str:
        """Кодирует изображение в base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    def analyze_image(self, image_path: str) -> dict:
        try:
            # Кодируем изображение в base64
            base64_image = self.encode_image(image_path)
            
            # Формируем запрос
            payload = {
                "model": "anthropic/claude-sonnet-4",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Ты - медицинский эксперт по анализу МРТ-изображений. Проанализируй это МРТ-изображение головного мозга и ответь в формате JSON. Используй следующую структуру:
{
  "has_tumor": true/false,
  "confidence": число от 0 до 1,
  "explanation": {
    "visual_description": "подробное описание того, что видно на изображении",
    "analysis": "детальный анализ обнаруженных признаков",
    "recommendations": "рекомендации по дальнейшим действиям",
    "medical_context": "медицинский контекст и важные замечания"
  }
}

Важно: 
1. Используй только русский язык
2. Не используй специальные символы и управляющие последовательности
3. Дай максимально подробное и профессиональное описание в каждом разделе explanation
4. Ответ должен быть валидным JSON
5. Не используй переносы строк внутри текстовых полей
6. Не используй кавычки внутри текстовых полей
7. Все текстовые поля должны быть в одну строку"""
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
            
            print("Sending request to API...")  # Отладочный вывод
            print(f"Image size: {len(base64_image)} bytes")  # Отладочный вывод
            
            # Отправляем запрос
            response = requests.post(
                url=self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )

            # Проверяем ответ
            if response.status_code == 200:
                result = response.json()
                print("API Response:", result)  # Отладочный вывод
                
                # Извлекаем ответ из JSON
                try:
                    # Получаем текст ответа из choices[0].message.content
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
                    print("Content:", content)  # Отладочный вывод
                    
                    # Очищаем ответ от markdown-разметки и лишних символов
                    content = content.replace('```json', '').replace('```', '').strip()
                    
                    # Пытаемся найти JSON в тексте
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx == -1 or end_idx == 0:
                        raise ValueError("No JSON found in response")
                        
                    json_str = content[start_idx:end_idx]
                    
                    # Очищаем строку от управляющих символов и форматируем JSON
                    json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
                    
                    # Исправляем отсутствующие запятые между полями
                    json_str = json_str.replace('}\n    "', '},\n    "')
                    json_str = json_str.replace('"\n    "', '",\n    "')
                    
                    # Очищаем от переносов строк внутри значений
                    json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                    
                    # Удаляем лишние пробелы
                    json_str = ' '.join(json_str.split())
                    
                    try:
                        # Парсим JSON для проверки валидности
                        analysis = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        print(f"Initial JSON parsing failed: {str(e)}")
                        # Пробуем исправить JSON вручную
                        json_str = json_str.replace('"supercritical"', '"supercritical",')
                        json_str = json_str.replace('"超临界丙酸钠"', '"超临界丙酸钠",')
                        # Удаляем все управляющие символы
                        json_str = ''.join(char for char in json_str if ord(char) >= 32)
                        analysis = json.loads(json_str)
                    
                    # Очищаем текстовые поля от переносов строк и лишних пробелов
                    for field in ["visual_description", "analysis", "recommendations", "medical_context"]:
                        if field in analysis["explanation"]:
                            text = analysis["explanation"][field]
                            # Заменяем переносы строк и множественные пробелы на один пробел
                            text = ' '.join(text.split())
                            # Удаляем кавычки внутри текста
                            text = text.replace('"', '').replace('"', '').replace('"', '')
                            # Удаляем все управляющие символы
                            text = ''.join(char for char in text if ord(char) >= 32)
                            analysis["explanation"][field] = text
                    
                    # Преобразуем в HTML
                    html_result = f"""
                    <div class="analysis-result">
                        <h2>Результат анализа МРТ</h2>
                        <div class="result-summary">
                            <p><strong>Наличие опухоли:</strong> {"Да" if analysis["has_tumor"] else "Нет"}</p>
                            <p><strong>Уверенность:</strong> {analysis["confidence"] * 100:.1f}%</p>
                        </div>
                        <div class="detailed-analysis">
                            <h3>Визуальное описание</h3>
                            <p>{analysis["explanation"]["visual_description"]}</p>
                            
                            <h3>Анализ</h3>
                            <p>{analysis["explanation"]["analysis"]}</p>
                            
                            <h3>Рекомендации</h3>
                            <p>{analysis["explanation"]["recommendations"]}</p>
                            
                            <h3>Медицинский контекст</h3>
                            <p>{analysis["explanation"]["medical_context"]}</p>
                        </div>
                    </div>
                    """
                    
                    return {
                        "description": analysis["explanation"]["visual_description"],
                        "conclusions": analysis["explanation"]["analysis"],
                        "recommendations": analysis["explanation"]["recommendations"],
                        "confidence": float(analysis["confidence"])
                    }
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    print(f"Error parsing response: {str(e)}")  # Отладочный вывод
                    raise Exception(f"Ошибка при разборе ответа API: {str(e)}")
            else:
                print(f"API Error: {response.status_code} - {response.text}")  # Отладочный вывод
                raise Exception(f"Ошибка API: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request Error: {str(e)}")  # Отладочный вывод
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            print(f"General Error: {str(e)}")  # Отладочный вывод
            raise Exception(f"Error analyzing image: {str(e)}")

# Создаем экземпляр сервиса
qwen_service = QwenService() 