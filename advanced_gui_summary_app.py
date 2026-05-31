import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import json
import os
import time
import threading
from datetime import datetime

class AdvancedSummaryGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор резюме Pro - OpenRouter API")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Переменные
        self.api_key = tk.StringVar()
        self.site_url = tk.StringVar()
        self.site_name = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.temperature = tk.DoubleVar(value=0.7)
        self.max_tokens = tk.IntVar(value=2000)
        
        # Список доступных моделей
        self.AVAILABLE_MODELS = {
            "qwen/qwen3-coder:free": "Qwen 3 Coder (Free) - с ограничениями",
            "qwen/qwen3-coder": "Qwen 3 Coder (Paid) - без ограничений",
            "openai/gpt-3.5-turbo": "GPT-3.5 Turbo (OpenAI)",
            "openai/gpt-4": "GPT-4 (OpenAI)",
            "openai/gpt-4-turbo": "GPT-4 Turbo (OpenAI)",
            "anthropic/claude-3-haiku": "Claude 3 Haiku (Anthropic)",
            "anthropic/claude-3-sonnet": "Claude 3 Sonnet (Anthropic)",
            "anthropic/claude-3-opus": "Claude 3 Opus (Anthropic)",
            "google/gemini-pro": "Gemini Pro (Google)",
            "google/gemini-pro-1.5": "Gemini Pro 1.5 (Google)",
            "meta-llama/llama-3-8b-instruct": "Llama 3 8B Instruct (Meta)",
            "meta-llama/llama-3-70b-instruct": "Llama 3 70B Instruct (Meta)",
            "mistralai/mistral-7b-instruct": "Mistral 7B Instruct",
            "mistralai/mixtral-8x7b-instruct": "Mixtral 8x7B Instruct",
            "mistralai/mistral-large": "Mistral Large"
        }
        
        # Готовые шаблоны инструкций
        self.INSTRUCTION_TEMPLATES = {
            "Краткое содержание": "Сделай краткое содержание этого текста",
            "Детальный анализ": "Проведи детальный анализ этого текста, выдели основные идеи и выводы",
            "Ключевые моменты": "Выдели ключевые моменты из этого текста в виде списка",
            "Перевод на английский": "Переведи этот текст на английский язык",
            "Перевод на русский": "Переведи этот текст на русский язык",
            "Исправление ошибок": "Исправь грамматические и стилистические ошибки в этом тексте",
            "Переписывание": "Перепиши этот текст более простым и понятным языком",
            "Вопросы по тексту": "Составь 5-10 вопросов по содержанию этого текста",
            "Пользовательская": "Введите свою инструкцию..."
        }
        
        self.selected_model.set("qwen/qwen3-coder:free")  # По умолчанию
        self.history = []  # История запросов
        
        self.create_widgets()
        self.load_settings()
        
    def create_widgets(self):
        # Создаем notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Основная"
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Основная")
        
        # Вкладка "Настройки"
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Настройки")
        
        # Вкладка "История"
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="История")
        
        self.create_main_tab()
        self.create_settings_tab()
        self.create_history_tab()
        
    def create_main_tab(self):
        main_frame = ttk.Frame(self.main_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Секция API настроек (компактная)
        api_frame = ttk.LabelFrame(main_frame, text="API ключ", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(api_frame, text="OpenRouter API ключ:").pack(side=tk.LEFT, padx=(0, 10))
        api_entry = ttk.Entry(api_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(api_frame, text="Загрузить", command=self.load_api_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(api_frame, text="Сохранить", command=self.save_api_key).pack(side=tk.LEFT)
        
        # Секция модели и шаблонов
        model_frame = ttk.LabelFrame(main_frame, text="Модель и инструкция", padding="10")
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Выбор модели
        model_sub_frame = ttk.Frame(model_frame)
        model_sub_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(model_sub_frame, text="Модель:").pack(side=tk.LEFT, padx=(0, 10))
        self.model_combo = ttk.Combobox(model_sub_frame, textvariable=self.selected_model, width=40, state="readonly")
        self.model_combo['values'] = [f"{model} - {desc}" for model, desc in self.AVAILABLE_MODELS.items()]
        self.model_combo.set(f"{list(self.AVAILABLE_MODELS.keys())[0]} - {list(self.AVAILABLE_MODELS.values())[0]}")
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_select)
        
        # Шаблоны инструкций
        template_sub_frame = ttk.Frame(model_frame)
        template_sub_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(template_sub_frame, text="Шаблон:").pack(side=tk.LEFT, padx=(0, 10))
        self.template_combo = ttk.Combobox(template_sub_frame, width=40, state="readonly")
        self.template_combo['values'] = list(self.INSTRUCTION_TEMPLATES.keys())
        self.template_combo.set("Краткое содержание")
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_select)
        
        # Поле для инструкции
        ttk.Label(model_frame, text="Инструкция для модели:").pack(anchor=tk.W, pady=(0, 5))
        self.instruction_entry = ttk.Entry(model_frame, width=80)
        self.instruction_entry.pack(fill=tk.X, pady=(0, 10))
        self.instruction_entry.insert(0, "Сделай краткое содержание этого текста")
        
        # Секция ввода текста
        input_frame = ttk.LabelFrame(main_frame, text="Ввод текста", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Кнопки для работы с файлами
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Загрузить файл", command=self.load_from_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Очистить", command=self.clear_text).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Вставить из буфера", command=self.paste_from_clipboard).pack(side=tk.LEFT)
        
        # Текстовое поле для ввода
        self.text_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # Секция результата
        output_frame = ttk.LabelFrame(main_frame, text="Результат", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Кнопки управления
        control_frame = ttk.Frame(output_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.process_button = ttk.Button(control_frame, text="🚀 Обработать текст", command=self.process_text)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="💾 Сохранить", command=self.save_result).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="📋 Копировать", command=self.copy_result).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🗑️ Очистить", command=self.clear_result).pack(side=tk.LEFT)
        
        # Текстовое поле для результата
        self.result_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Прогресс бар и статус
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(status_frame, text="Готов к работе")
        self.status_label.pack(anchor=tk.W)
        
    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API настройки
        api_settings_frame = ttk.LabelFrame(settings_frame, text="Настройки API", padding="10")
        api_settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL сайта
        ttk.Label(api_settings_frame, text="URL сайта (опционально):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(api_settings_frame, textvariable=self.site_url, width=50).grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Название сайта
        ttk.Label(api_settings_frame, text="Название сайта (опционально):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(api_settings_frame, textvariable=self.site_name, width=50).grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        api_settings_frame.columnconfigure(1, weight=1)
        
        # Параметры модели
        model_settings_frame = ttk.LabelFrame(settings_frame, text="Параметры модели", padding="10")
        model_settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Temperature
        ttk.Label(model_settings_frame, text="Temperature (креативность):").grid(row=0, column=0, sticky=tk.W, pady=5)
        temp_frame = ttk.Frame(model_settings_frame)
        temp_frame.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        self.temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, variable=self.temperature, orient=tk.HORIZONTAL)
        self.temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.temp_label = ttk.Label(temp_frame, text="0.7")
        self.temp_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.temp_scale.bind("<Motion>", self.update_temp_label)
        
        # Max tokens
        ttk.Label(model_settings_frame, text="Максимум токенов:").grid(row=1, column=0, sticky=tk.W, pady=5)
        tokens_frame = ttk.Frame(model_settings_frame)
        tokens_frame.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        self.tokens_scale = ttk.Scale(tokens_frame, from_=100, to=4000, variable=self.max_tokens, orient=tk.HORIZONTAL)
        self.tokens_scale.pack(side=tk.Left, fill=tk.X, expand=True)
        
        self.tokens_label = ttk.Label(tokens_frame, text="2000")
        self.tokens_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.tokens_scale.bind("<Motion>", self.update_tokens_label)
        
        model_settings_frame.columnconfigure(1, weight=1)
        
        # Файловые настройки
        file_settings_frame = ttk.LabelFrame(settings_frame, text="Настройки файлов", padding="10")
        file_settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_settings_frame, text="Путь для сохранения по умолчанию:").grid(row=0, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(file_settings_frame)
        path_frame.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        ttk.Entry(path_frame, textvariable=self.output_file_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Выбрать", command=self.choose_output_file).pack(side=tk.LEFT, padx=(10, 0))
        
        self.output_file_path.set("result.txt")
        
        file_settings_frame.columnconfigure(1, weight=1)
        
        # Кнопки настроек
        settings_buttons_frame = ttk.Frame(settings_frame)
        settings_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(settings_buttons_frame, text="Сохранить настройки", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(settings_buttons_frame, text="Загрузить настройки", command=self.load_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(settings_buttons_frame, text="Сбросить настройки", command=self.reset_settings).pack(side=tk.LEFT)
        
    def create_history_tab(self):
        history_frame = ttk.Frame(self.history_tab)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления историей
        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(history_buttons_frame, text="Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(history_buttons_frame, text="Экспорт истории", command=self.export_history).pack(side=tk.LEFT)
        
        # Список истории
        self.history_tree = ttk.Treeview(history_frame, columns=("time", "model", "prompt", "result"), show="headings", height=20)
        self.history_tree.heading("time", text="Время")
        self.history_tree.heading("model", text="Модель")
        self.history_tree.heading("prompt", text="Запрос")
        self.history_tree.heading("result", text="Результат")
        
        self.history_tree.column("time", width=150)
        self.history_tree.column("model", width=200)
        self.history_tree.column("prompt", width=300)
        self.history_tree.column("result", width=300)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        self.history_tree.bind("<Double-1>", self.on_history_select)
        
        # Scrollbar для истории
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_temp_label(self, event=None):
        self.temp_label.config(text=f"{self.temperature.get():.1f}")
        
    def update_tokens_label(self, event=None):
        self.tokens_label.config(text=f"{self.max_tokens.get()}")
        
    def on_model_select(self, event=None):
        selected = self.model_combo.get()
        if " - " in selected:
            model_id = selected.split(" - ")[0]
            self.selected_model.set(model_id)
    
    def on_template_select(self, event=None):
        selected_template = self.template_combo.get()
        if selected_template in self.INSTRUCTION_TEMPLATES:
            instruction = self.INSTRUCTION_TEMPLATES[selected_template]
            if instruction != "Введите свою инструкцию...":
                self.instruction_entry.delete(0, tk.END)
                self.instruction_entry.insert(0, instruction)
    
    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл с текстом",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, content)
                self.status_label.config(text=f"Загружен файл: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")
    
    def paste_from_clipboard(self):
        try:
            clipboard_content = self.root.clipboard_get()
            self.text_input.insert(tk.INSERT, clipboard_content)
            self.status_label.config(text="Текст вставлен из буфера обмена")
        except:
            messagebox.showwarning("Предупреждение", "Буфер обмена пуст или недоступен")
    
    def copy_result(self):
        try:
            result_content = self.result_text.get(1.0, tk.END).strip()
            if result_content:
                self.root.clipboard_clear()
                self.root.clipboard_append(result_content)
                self.status_label.config(text="Результат скопирован в буфер обмена")
            else:
                messagebox.showwarning("Предупреждение", "Нет результата для копирования")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при копировании: {e}")
    
    def choose_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Выберите файл для сохранения",
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            self.output_file_path.set(file_path)
    
    def clear_text(self):
        self.text_input.delete(1.0, tk.END)
        self.status_label.config(text="Текст очищен")
    
    def clear_result(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.status_label.config(text="Результат очищен")
    
    def call_api(self, prompt, api_key, site_url="", site_name="", model="qwen/qwen3-coder:free"):
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
                    "temperature": self.temperature.get(),
                    "max_tokens": self.max_tokens.get()
                }),
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            elif response.status_code == 429:
                time.sleep(5)
                return self.call_api(prompt, api_key, site_url, site_name, model)
            else:
                return f"Ошибка API: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Ошибка при вызове API: {e}"
    
    def process_text_thread(self):
        try:
            api_key = self.api_key.get().strip()
            if not api_key:
                messagebox.showerror("Ошибка", "API ключ обязателен!")
                return
            
            text_content = self.text_input.get(1.0, tk.END).strip()
            if not text_content:
                messagebox.showerror("Ошибка", "Введите текст для обработки!")
                return
            
            instruction = self.instruction_entry.get().strip()
            if instruction:
                prompt = f"{instruction}\n\n{text_content}"
            else:
                prompt = text_content
            
            model = self.selected_model.get()
            site_url = self.site_url.get().strip()
            site_name = self.site_name.get().strip()
            
            # Обновляем статус
            self.status_label.config(text=f"Отправка запроса к модели {model}...")
            
            result = self.call_api(prompt, api_key, site_url, site_name, model)
            
            # Отображаем результат
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
            self.result_text.config(state=tk.DISABLED)
            
            # Добавляем в историю
            self.add_to_history(model, prompt[:100] + "..." if len(prompt) > 100 else prompt, 
                              result[:100] + "..." if len(result) > 100 else result)
            
            self.status_label.config(text="Обработка завершена успешно!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
            self.status_label.config(text="Ошибка при обработке")
        
        finally:
            self.progress.stop()
            self.process_button.config(state=tk.NORMAL, text="🚀 Обработать текст")
    
    def process_text(self):
        self.process_button.config(state=tk.DISABLED, text="Обработка...")
        self.progress.start()
        
        thread = threading.Thread(target=self.process_text_thread)
        thread.daemon = True
        thread.start()
    
    def save_result(self):
        try:
            result_content = self.result_text.get(1.0, tk.END).strip()
            if not result_content:
                messagebox.showwarning("Предупреждение", "Нет результата для сохранения!")
                return
            
            output_file = self.output_file_path.get().strip()
            if not output_file:
                output_file = filedialog.asksaveasfilename(
                    title="Сохранить результат",
                    defaultextension=".txt",
                    filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
                )
                if not output_file:
                    return
            
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_content)
            
            self.status_label.config(text=f"Результат сохранен: {os.path.basename(output_file)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {e}")
    
    def add_to_history(self, model, prompt, result):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "time": timestamp,
            "model": model,
            "prompt": prompt,
            "result": result
        })
        
        # Добавляем в дерево
        self.history_tree.insert("", 0, values=(timestamp, model, prompt, result))
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history.clear()
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            self.status_label.config(text="История очищена")
    
    def export_history(self):
        if not self.history:
            messagebox.showwarning("Предупреждение", "История пуста!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Экспорт истории",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, ensure_ascii=False, indent=2)
                self.status_label.config(text=f"История экспортирована: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {e}")
    
    def on_history_select(self, event):
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            values = item['values']
            if len(values) >= 4:
                # Показываем подробную информацию
                messagebox.showinfo("История", f"Время: {values[0]}\nМодель: {values[1]}\nЗапрос: {values[2]}\nРезультат: {values[3]}")
    
    def save_settings(self):
        settings = {
            "api_key": self.api_key.get(),
            "site_url": self.site_url.get(),
            "site_name": self.site_name.get(),
            "selected_model": self.selected_model.get(),
            "temperature": self.temperature.get(),
            "max_tokens": self.max_tokens.get(),
            "output_file_path": self.output_file_path.get()
        }
        
        try:
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.status_label.config(text="Настройки сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении настроек: {e}")
    
    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.api_key.set(settings.get("api_key", ""))
                self.site_url.set(settings.get("site_url", ""))
                self.site_name.set(settings.get("site_name", ""))
                self.selected_model.set(settings.get("selected_model", "qwen/qwen3-coder:free"))
                self.temperature.set(settings.get("temperature", 0.7))
                self.max_tokens.set(settings.get("max_tokens", 2000))
                self.output_file_path.set(settings.get("output_file_path", "result.txt"))
                
                self.status_label.config(text="Настройки загружены")
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
    
    def reset_settings(self):
        if messagebox.askyesno("Подтверждение", "Сбросить все настройки к значениям по умолчанию?"):
            self.api_key.set("")
            self.site_url.set("")
            self.site_name.set("")
            self.selected_model.set("qwen/qwen3-coder:free")
            self.temperature.set(0.7)
            self.max_tokens.set(2000)
            self.output_file_path.set("result.txt")
            self.status_label.config(text="Настройки сброшены")
    
    def save_api_key(self):
        try:
            with open("api_key.txt", 'w', encoding='utf-8') as f:
                f.write(self.api_key.get())
            self.status_label.config(text="API ключ сохранен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении API ключа: {e}")
    
    def load_api_key(self):
        try:
            if os.path.exists("api_key.txt"):
                with open("api_key.txt", 'r', encoding='utf-8') as f:
                    self.api_key.set(f.read().strip())
                self.status_label.config(text="API ключ загружен")
            else:
                messagebox.showwarning("Предупреждение", "Файл с API ключом не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке API ключа: {e}")

def main():
    root = tk.Tk()
    app = AdvancedSummaryGeneratorGUI(root)
    
    # Сохранение настроек при закрытии
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
