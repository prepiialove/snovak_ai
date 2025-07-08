import json
from typing import Optional
from openai import OpenAI
from app.core.config import settings
from app.web.schemas import ServiceData

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_service_data_from_text(text: str) -> Optional[ServiceData]:
    """
    Використовує OpenAI для вилучення структурованих даних про послуги з необробленого тексту.
    """
    prompt = f"""
    Проаналізуй наступний текст і витягни з нього структуровану інформацію про послугу.
    Текст: "{text}"

    Поверни відповідь у форматі JSON з такими ключами:
    - name: Назва послуги/компанії
    - category: Одна з наступних категорій: "Послуги краси", "Автомобільний сервіс", "Ремонт та обслуговування", "Розклад транспорту"
    - address: Адреса
    - phone: Номер телефону
    - schedule: Графік роботи
    - social_media: Посилання на соціальні мережі або веб-сайт
    - description: Короткий опис

    Якщо якась інформація відсутня, залиш для відповідного ключа значення null.
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

def get_search_query_from_text(text: str) -> Optional[str]:
    """
    Використовує OpenAI для вилучення пошукового запиту з необробленого тексту.
    """
    prompt = f"""
    Проаналізуй наступний запит користувача та поверни ключові слова для пошуку в базі даних послуг.
    Запит: "{text}"

    Поверни лише ключові слова, без зайвих пояснень. Наприклад, якщо користувач шукає "де підстригтися", поверни "стрижка" або "перукарня".
    Якщо користувач шукає "ремонт колеса", поверни "шиномонтаж" або "ремонт коліс".
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
def translate_to_ukrainian(text: str) -> str:
    """
    Translates text from Russian to Ukrainian using OpenAI.
    If the text is already in Ukrainian, it returns the original text.
    """
    prompt = f"""
    Переклади наступний текст на українську мову. Якщо текст вже написаний українською, поверни його без змін.
    Текст: "{text}"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text from Russian to Ukrainian."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error translating text with OpenAI: {e}")
        return text
import speech_recognition as sr
from pydub import AudioSegment
import io

def recognize_speech_from_bytes(audio_bytes: bytes) -> Optional[str]:
    """
    Recognizes speech from audio bytes and returns the text.
    """
    recognizer = sr.Recognizer()
    
    try:
        # Convert OGG to WAV
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="ogg")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        
        # Recognize speech using Google Web Speech API
        text = recognizer.recognize_google(audio_data, language="uk-UA")
        return text

    except sr.UnknownValueError:
        print("Google Web Speech API could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
        return None
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None