import requests
import json
import os
import time

# Список доступных моделей
AVAILABLE_MODELS = {
    "1": ("qwen/qwen3-coder:free", "Qwen 3 Coder (Free) - с ограничениями"),
    "2": ("qwen/qwen3-coder", "Qwen 3 Coder (Paid) - без ограничений"),
    "3": ("openai/gpt-3.5-turbo", "GPT-3.5 Turbo (OpenAI)"),
    "4": ("openai/gpt-4", "GPT-4 (OpenAI)"),
    "5": ("anthropic/claude-3-haiku", "Claude 3 Haiku (Anthropic)"),
    "6": ("anthropic/claude-3-sonnet", "Claude 3 Sonnet (Anthropic)"),
    "7": ("google/gemini-pro", "Gemini Pro (Google)"),
    "8": ("meta-llama/llama-3-8b-instruct", "Llama 3 8B Instruct (Meta)"),
    "9": ("meta-llama/llama-3-70b-instruct", "Llama 3 70B Instruct (Meta)"),
    "10": ("mistralai/mistral-7b-instruct", "Mistral 7B Instruct"),
    "11": ("mistralai/mixtral-8x7b-instruct", "Mixtral 8x7B Instruct"),
    "0": ("custom", "Другая модель (ввести вручную)")
}

# Функция для вызова API
def call_qwen_api(prompt, api_key, site_url="", site_name="", model="qwen/qwen3-coder:free"):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": site_url,
                "X-Title": site_name,
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }),
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        elif response.status_code == 429:
            print("⚠ Превышен лимит запросов. Повторная попытка через 5 секунд...")
            time.sleep(5)
            return call_qwen_api(prompt, api_key, site_url, site_name, model)
        else:
            print(f"Ошибка API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Ошибка при вызове API: {e}")
        return None

# Функция для чтения содержимого файла
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла '{file_path}': {e}")
        return None

# Функция для сохранения результата в файл
def save_result_to_file(content, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Результат успешно сохранен в файл: {output_file}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        return False

# Функция для выбора модели
def select_model():
    print("\nДоступные модели:")
    for key, (model_id, description) in AVAILABLE_MODELS.items():
        print(f"{key}. {description}")
    
    while True:
        choice = input("\nВыберите модель (введите номер): ").strip()
        if choice in AVAILABLE_MODELS:
            if choice == "0":
                # Пользовательская модель
                custom_model = input("Введите название модели: ").strip()
                if custom_model:
                    return custom_model
                else:
                    print("Название модели не может быть пустым!")
                    continue
            else:
                return AVAILABLE_MODELS[choice][0]
        else:
            print("Неверный выбор. Пожалуйста, выберите номер из списка.")

# Функция для смены текущей модели
def change_model(current_model):
    print(f"\nТекущая модель: {current_model}")
    new_model = select_model()
    print(f"Модель изменена на: {new_model}")
    return new_model

def main():
    print("=== Скрипт для работы с API OpenRouter ===")
    
    # Запрашиваем API ключ
    api_key = input("Введите ваш OPENROUTER API ключ: ").strip()
    if not api_key:
        print("API ключ обязателен для работы!")
        return
    
    # Опциональные параметры для заголовков API
    site_url = input("Введите URL вашего сайта (опционально): ").strip()
    site_name = input("Введите название вашего сайта (опционально): ").strip()
    
    # Выбор начальной модели
    model = select_model()
    
    while True:
        print("\n" + "="*50)
        print("Выберите действие:")
        print("1. Отправить запрос")
        print("2. Сменить модель")
        print("3. Выйти")
        
        action_choice = input("Выберите действие (1-3): ").strip()
        
        if action_choice == "3":
            break
        elif action_choice == "2":
            model = change_model(model)
            continue
        elif action_choice != "1":
            print("Неверный выбор!")
            continue
            
        print("\nВыберите тип ввода:")
        print("1. Ввести текст вручную")
        print("2. Загрузить текст из файла")
        
        input_choice = input("Выберите вариант (1 или 2): ").strip()
        
        prompt = ""
        if input_choice == "2":
            # Загрузка из файла
            input_file = input("Введите путь к файлу с текстом: ").strip().strip('"')
            input_file = os.path.normpath(input_file)
            
            file_content = read_file_content(input_file)
            if file_content is None:
                continue
                
            # Спрашиваем, нужно ли добавить инструкцию
            add_instruction = input("Добавить инструкцию для обработки текста? (да/нет, по умолчанию да): ").strip().lower()
            if add_instruction in ['да', 'д', 'yes', 'y', '']:
                instruction = input("Введите инструкцию (например, 'Сделай краткое содержание этого текста'): ").strip()
                if instruction:
                    prompt = f"{instruction}\n\n{file_content}"
                else:
                    prompt = file_content
            else:
                prompt = file_content
                
        else:
            # Ручной ввод текста
            prompt = input("Введите ваш запрос (промт) для модели: ").strip()
            
        if not prompt:
            print("Текст/промт не может быть пустым!")
            continue
        
        # Запрашиваем путь для сохранения результата
        output_file = input("Введите путь для сохранения результата (например, result.txt): ").strip().strip('"')
        if not output_file:
            output_file = "result.txt"
        
        output_file = os.path.normpath(output_file)
        
        # Создаем директорию если она не существует
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Создана директория: {output_dir}")
            except Exception as e:
                print(f"Ошибка при создании директории: {e}")
                continue
        
        print(f"\nОтправка запроса к API (модель: {model})...")
        print("Ожидайте ответа...")
        
        # Отправляем запрос к API
        result = call_qwen_api(prompt, api_key, site_url, site_name, model)
        
        if result:
            print("\n" + "="*50)
            print("Ответ от модели:")
            print("="*50)
            print(result)
            print("="*50)
            
            # Сохраняем результат в файл
            if save_result_to_file(result, output_file):
                print(f"\n✅ Запрос выполнен успешно!")
                print(f"✅ Результат сохранен в: {output_file}")
            else:
                print(f"\n⚠ Запрос выполнен, но файл не сохранен!")
                print("⚠ Результат отображен выше ⚠")
        else:
            print("\n❌ Не удалось получить ответ от API")

    print("\nСпасибо за использование скрипта!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {e}")