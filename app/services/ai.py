import json
from openai import OpenAI
from app.core.config import settings
from app.web.schemas import ServiceData

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_service_data_from_text(text: str) -> ServiceData | None:
    """
    Uses OpenAI to extract structured service data from raw text.
    """
    prompt = f"""
    Проанализируй следующий текст и извлеки из него структурированную информацию об услуге.
    Текст: "{text}"

    Верни ответ в формате JSON со следующими ключами:
    - name: Название услуги/компании
    - category: Одна из следующих категорий: "Послуги краси", "Автомобільний сервіс", "Ремонт та обслуговування", "Розклад транспорту"
    - address: Адрес
    - phone: Номер телефона
    - schedule: График работы
    - social_media: Ссылка на социальные сети или веб-сайт
    - description: Краткое описание

    Если какая-то информация отсутствует, оставь для соответствующего ключа значение null.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from text and returns it as JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        return ServiceData(**data)

    except Exception as e:
        print(f"Error processing text with OpenAI: {e}")
        return None

def get_search_query_from_text(text: str) -> str | None:
    """
    Uses OpenAI to extract a search query from raw text.
    """
    prompt = f"""
    Проанализируй следующий запрос пользователя и верни ключевые слова для поиска по базе данных услуг.
    Запрос: "{text}"

    Верни только ключевые слова, без лишних объяснений. Например, если пользователь ищет "где подстричься", верни "стрижка" или "парикмахерская".
    Если пользователь ищет "ремонт колеса", верни "шиномонтаж" или "ремонт колес".
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts keywords for a database search from user queries."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error processing search query with OpenAI: {e}")
        return None