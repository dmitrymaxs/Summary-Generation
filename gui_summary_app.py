import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import requests
import json
import os
import sys
import time
import threading

class SummaryGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор резюме - OpenRouter API")
        self.root.geometry("900x900")
        self.root.resizable(True, True)
        
        # Устанавливаем минимальный размер окна
        self.root.minsize(800, 800)
        
        # Устанавливаем иконку приложения
        self.set_app_icon()
        
        # Переменные
        self.api_key = tk.StringVar()
        self.site_url = tk.StringVar()
        self.site_name = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.custom_model = tk.StringVar()
        self.input_text = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.show_api_key = tk.BooleanVar()
        
        # Список доступных моделей
        self.AVAILABLE_MODELS = {
            "qwen/qwen3-coder:free": "Qwen 3 Coder (Free) - с ограничениями",
            "qwen/qwen3-coder": "Qwen 3 Coder (Paid) - без ограничений",
            "openai/gpt-3.5-turbo": "GPT-3.5 Turbo (OpenAI)",
            "openai/gpt-4": "GPT-4 (OpenAI)",
            "anthropic/claude-3-haiku": "Claude 3 Haiku (Anthropic)",
            "anthropic/claude-3-sonnet": "Claude 3 Sonnet (Anthropic)",
            "google/gemini-pro": "Gemini Pro (Google)",
            "meta-llama/llama-3-8b-instruct": "Llama 3 8B Instruct (Meta)",
            "meta-llama/llama-3-70b-instruct": "Llama 3 70B Instruct (Meta)",
            "mistralai/mistral-7b-instruct": "Mistral 7B Instruct",
            "mistralai/mixtral-8x7b-instruct": "Mixtral 8x7B Instruct",
            "custom": "🔧 Ввести вручную..."
        }
        
        self.selected_model.set("qwen/qwen3-coder:free")  # По умолчанию
        
        # Загружаем настройки после установки значений по умолчанию
        self.load_settings()
        
        self.create_widgets()
        
        # Привязываем автосохранение к изменениям настроек
        self.api_key.trace('w', lambda *args: self.save_settings())
        self.custom_model.trace('w', lambda *args: self.save_settings())
        self.selected_model.trace('w', lambda *args: self.save_settings())
        
    def set_app_icon(self):
        """Установка иконки приложения"""
        try:
            # Список возможных путей к иконке
            icon_paths = [
                "summarize_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.png",
                "summarize_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.ico",
                "icon.png",
                "icon.ico"
            ]
            
            # Получаем директорию приложения (работает и для EXE, и для скрипта)
            app_dir = self.get_app_directory()
            
            for icon_name in icon_paths:
                icon_path = os.path.join(app_dir, icon_name)
                if os.path.exists(icon_path):
                    try:
                        # Для .ico файлов
                        if icon_path.endswith('.ico'):
                            self.root.iconbitmap(icon_path)
                            print(f"Иконка установлена: {icon_path}")
                            return
                        # Для .png файлов
                        elif icon_path.endswith('.png'):
                            # Попытка использовать PNG как иконку (требует PIL)
                            try:
                                from PIL import Image, ImageTk
                                img = Image.open(icon_path)
                                # Изменяем размер до стандартного размера иконки
                                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                                photo = ImageTk.PhotoImage(img)
                                self.root.iconphoto(True, photo)
                                # Сохраняем ссылку на изображение
                                self.icon_photo = photo
                                print(f"Иконка установлена: {icon_path}")
                                return
                            except ImportError:
                                # Если PIL недоступен, пробуем установить как PhotoImage
                                try:
                                    photo = tk.PhotoImage(file=icon_path)
                                    self.root.iconphoto(True, photo)
                                    self.icon_photo = photo
                                    print(f"Иконка установлена: {icon_path}")
                                    return
                                except tk.TclError:
                                    continue
                    except Exception as e:
                        print(f"Ошибка при установке иконки {icon_path}: {e}")
                        continue
            
            print("Иконка не найдена, используется стандартная")
            
        except Exception as e:
            print(f"Ошибка при установке иконки: {e}")
        
    def create_widgets(self):
        # Главный контейнер с прокруткой
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Секция API настроек
        api_frame = ttk.LabelFrame(main_frame, text="Настройки API", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API ключ
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=(10, 0))
        
        ttk.Label(api_frame, text="OpenRouter API ключ:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.api_entry = ttk.Entry(api_key_frame, textvariable=self.api_key, width=50, show="*")
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Кнопка показать/скрыть пароль
        self.show_api_key = tk.BooleanVar()
        self.toggle_api_button = ttk.Button(api_key_frame, text="👁", width=3, command=self.toggle_api_visibility)
        self.toggle_api_button.pack(side=tk.LEFT)
        
        # URL сайта (опционально)
        ttk.Label(api_frame, text="URL сайта (опционально):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(api_frame, textvariable=self.site_url, width=60).grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=(10, 0))
        
        # Название сайта (опционально)
        ttk.Label(api_frame, text="Название сайта (опционально):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(api_frame, textvariable=self.site_name, width=60).grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=(10, 0))
        
        api_frame.columnconfigure(1, weight=1)
        
        # Секция выбора модели
        model_frame = ttk.LabelFrame(main_frame, text="Выбор модели", padding="10")
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(model_frame, text="Модель:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, width=50, state="readonly")
        self.model_combo['values'] = [f"{model} - {desc}" for model, desc in self.AVAILABLE_MODELS.items()]
        
        # Устанавливаем загруженную модель или по умолчанию
        current_model = self.selected_model.get()
        if current_model in self.AVAILABLE_MODELS:
            display_text = f"{current_model} - {self.AVAILABLE_MODELS[current_model]}"
            self.model_combo.set(display_text)
        else:
            default_model = list(self.AVAILABLE_MODELS.keys())[0]
            self.model_combo.set(f"{default_model} - {self.AVAILABLE_MODELS[default_model]}")
            self.selected_model.set(default_model)
            
        self.model_combo.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(10, 0))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_select)
        
        # Поле для ввода пользовательской модели
        ttk.Label(model_frame, text="Пользовательская модель:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        custom_frame = ttk.Frame(model_frame)
        custom_frame.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(10, 0))
        
        self.custom_model_entry = ttk.Entry(custom_frame, textvariable=self.custom_model, width=40, state=tk.DISABLED)
        self.custom_model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Добавляем контекстное меню для поля пользовательской модели
        self.create_context_menu(self.custom_model_entry)
        
        ttk.Button(custom_frame, text="📋 Примеры", command=self.show_model_examples).pack(side=tk.LEFT, padx=(5, 0))
        
        # Проверяем, нужно ли активировать поле пользовательской модели при загрузке
        if self.selected_model.get() == "custom" and self.custom_model.get():
            self.custom_model_entry.config(state=tk.NORMAL)
        
        model_frame.columnconfigure(1, weight=1)
        
        # Секция ввода текста
        input_frame = ttk.LabelFrame(main_frame, text="Ввод текста", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Кнопки для выбора типа ввода
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Загрузить из файла", command=self.load_from_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Очистить текст", command=self.clear_text).pack(side=tk.LEFT)
        
        # Поле для инструкции
        instruction_frame = ttk.Frame(input_frame)
        instruction_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(instruction_frame, text="Инструкция для модели:").pack(anchor=tk.W, pady=(0, 5))
        
        # Рамка для инструкции и кнопок
        instruction_controls = ttk.Frame(instruction_frame)
        instruction_controls.pack(fill=tk.X)
        
        # Многострочное поле для инструкций
        instruction_text_frame = ttk.Frame(instruction_controls)
        instruction_text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.instruction_text = tk.Text(instruction_text_frame, height=3, wrap=tk.WORD, font=("TkDefaultFont", 9))
        self.instruction_text.pack(fill=tk.BOTH, expand=True)
        
        # Загружаем сохраненную инструкцию или используем по умолчанию
        instruction_text = getattr(self, 'saved_instruction', "Сделай краткое содержание этого текста")
        self.instruction_text.insert(1.0, instruction_text)
        
        # Привязываем автосохранение к изменению инструкции
        self.instruction_text.bind('<KeyRelease>', lambda event: self.save_settings())
        self.instruction_text.bind('<FocusOut>', lambda event: self.save_settings())
        
        # Добавляем контекстное меню для поля инструкций
        self.create_text_context_menu(self.instruction_text)
        
        # Рамка для кнопок
        buttons_frame = ttk.Frame(instruction_controls)
        buttons_frame.pack(side=tk.LEFT)
        
        # Рамка для кнопок
        buttons_frame = ttk.Frame(instruction_controls)
        buttons_frame.pack(side=tk.LEFT)
        
        # Кнопки для быстрых инструкций (вертикально)
        ttk.Button(buttons_frame, text="📝 Краткое содержание", command=lambda: self.set_instruction("Сделай краткое содержание этого текста")).pack(pady=(0, 2))
        ttk.Button(buttons_frame, text="⏰ Тайм коды", command=lambda: self.set_instruction("Из текста передачи, создать краткое содержание передачи с тайм кодами, содержание сделать в виде заголовков не менее три четыре слова. Тайм коды в формате часы:минуты:секунды, таймкод начала эпизода ставится один перед заголовком.")).pack(pady=(0, 2))
        ttk.Button(buttons_frame, text="🌐 Перевод", command=lambda: self.set_instruction("Переведи этот текст на английский язык")).pack()
        
        # Текстовое поле для ввода/отображения текста
        ttk.Label(input_frame, text="Текст для обработки:").pack(anchor=tk.W, pady=(0, 5))
        self.text_input = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем контекстное меню для поля ввода текста
        self.create_text_context_menu(self.text_input)
        
        # Секция вывода результата
        output_frame = ttk.LabelFrame(main_frame, text="Результат", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Поле для пути сохранения
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="Файл для сохранения:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(path_frame, textvariable=self.output_file_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(path_frame, text="Выбрать", command=self.choose_output_file).pack(side=tk.LEFT)
        
        self.output_file_path.set("result.txt")
        
        # Текстовое поле для результата
        self.result_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Добавляем контекстное меню для поля результата
        self.create_text_context_menu(self.result_text)
        
        # Кнопки управления
        control_frame = ttk.Frame(output_frame)
        control_frame.pack(fill=tk.X)
        
        self.process_button = ttk.Button(control_frame, text="🚀 ОБРАБОТАТЬ ТЕКСТ", command=self.process_text)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="💾 Сохранить результат", command=self.save_result).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🗑️ Очистить результат", command=self.clear_result).pack(side=tk.LEFT)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
    def on_model_select(self, event=None):
        """Обработчик выбора модели"""
        selected = self.model_combo.get()
        if " - " in selected:
            model_id = selected.split(" - ")[0]
            self.selected_model.set(model_id)
            
            # Если выбрана пользовательская модель, активируем поле ввода
            if model_id == "custom":
                self.custom_model_entry.config(state=tk.NORMAL)
                self.custom_model_entry.focus()
                # Если поле пустое, предлагаем пример
                if not self.custom_model.get():
                    self.custom_model.set("openai/gpt-4-turbo")
            else:
                self.custom_model_entry.config(state=tk.DISABLED)
                self.custom_model.set("")
    
    def set_instruction(self, instruction):
        """Установка готовой инструкции"""
        self.instruction_text.delete(1.0, tk.END)
        self.instruction_text.insert(1.0, instruction)
    
    def toggle_api_visibility(self):
        """Переключение видимости API ключа"""
        if self.show_api_key.get():
            self.api_entry.config(show="")
            self.toggle_api_button.config(text="🙈")
            self.show_api_key.set(False)
        else:
            self.api_entry.config(show="*")
            self.toggle_api_button.config(text="👁")
            self.show_api_key.set(True)
    
    def get_app_directory(self):
        """Получение директории приложения (работает и для EXE, и для скрипта)"""
        if getattr(sys, 'frozen', False):
            # Если это EXE файл, созданный PyInstaller
            app_dir = os.path.dirname(sys.executable)
        else:
            # Если это Python скрипт
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        return app_dir
    
    def get_settings_file_path(self):
        """Получение пути к файлу настроек"""
        app_dir = self.get_app_directory()
        return os.path.join(app_dir, "app_settings.json")
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            settings = {
                "api_key": self.api_key.get(),
                "site_url": self.site_url.get(),
                "site_name": self.site_name.get(),
                "selected_model": self.selected_model.get(),
                "custom_model": self.custom_model.get(),
                "output_file_path": self.output_file_path.get(),
                "last_instruction": self.instruction_text.get(1.0, tk.END).strip()
            }
            
            settings_file = self.get_settings_file_path()
            print(f"Сохранение настроек в: {settings_file}")
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            settings_file = self.get_settings_file_path()
            print(f"Попытка загрузки настроек из: {settings_file}")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                print(f"Настройки успешно загружены из: {settings_file}")
                self.api_key.set(settings.get("api_key", ""))
                self.site_url.set(settings.get("site_url", ""))
                self.site_name.set(settings.get("site_name", ""))
                self.selected_model.set(settings.get("selected_model", "qwen/qwen3-coder:free"))
                self.custom_model.set(settings.get("custom_model", ""))
                self.output_file_path.set(settings.get("output_file_path", "result.txt"))
                
                # Сохраняем инструкцию для восстановления после создания виджетов
                self.saved_instruction = settings.get("last_instruction", "Сделай краткое содержание этого текста")
            else:
                print(f"Файл настроек не найден: {settings_file}")
                # Устанавливаем значения по умолчанию
                self.selected_model.set("qwen/qwen3-coder:free")
                self.output_file_path.set("result.txt")
                self.saved_instruction = "Сделай краткое содержание этого текста"
                
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            # Устанавливаем значения по умолчанию
            self.selected_model.set("qwen/qwen3-coder:free")
            self.output_file_path.set("result.txt")
            self.saved_instruction = "Сделай краткое содержание этого текста"
    
    def show_model_examples(self):
        """Показать примеры пользовательских моделей"""
        examples = [
            "openai/gpt-4-turbo-preview",
            "anthropic/claude-3-opus",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-70b-instruct",
            "mistralai/mistral-large-2402",
            "cohere/command-r-plus",
            "perplexity/llama-3-sonar-large-32k-online"
        ]
        
        example_text = "Примеры моделей:\n\n" + "\n".join(f"• {model}" for model in examples)
        example_text += "\n\nФормат: провайдер/название-модели"
        
        messagebox.showinfo("Примеры моделей", example_text)
    
    def create_context_menu(self, widget):
        """Создание контекстного меню для текстового поля"""
        context_menu = tk.Menu(self.root, tearoff=0)
        
        context_menu.add_command(label="✂️ Вырезать", command=lambda: self.cut_text(widget), accelerator="Ctrl+X")
        context_menu.add_command(label="📋 Копировать", command=lambda: self.copy_text(widget), accelerator="Ctrl+C")
        context_menu.add_command(label="📥 Вставить", command=lambda: self.paste_text(widget), accelerator="Ctrl+V")
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Удалить", command=lambda: self.delete_text(widget), accelerator="Delete")
        context_menu.add_command(label="📝 Выделить всё", command=lambda: self.select_all_text(widget), accelerator="Ctrl+A")
        context_menu.add_separator()
        context_menu.add_command(label="🔄 Отменить", command=lambda: self.undo_text(widget), accelerator="Ctrl+Z")
        
        def show_context_menu(event):
            try:
                context_menu.post(event.x_root, event.y_root)
            except:
                pass
        
        # Привязываем контекстное меню к правой кнопке мыши
        widget.bind("<Button-3>", show_context_menu)
        
        # Привязываем горячие клавиши
        widget.bind("<Control-x>", lambda e: self.cut_text(widget))
        widget.bind("<Control-c>", lambda e: self.copy_text(widget))
        widget.bind("<Control-v>", lambda e: self.paste_text(widget))
        widget.bind("<Control-a>", lambda e: self.select_all_text(widget))
        widget.bind("<Control-z>", lambda e: self.undo_text(widget))
        widget.bind("<Delete>", lambda e: self.delete_selected_text(widget))
    
    def cut_text(self, widget):
        """Вырезать текст"""
        try:
            if widget.selection_present():
                widget.event_generate("<<Cut>>")
        except:
            pass
    
    def copy_text(self, widget):
        """Копировать текст"""
        try:
            if widget.selection_present():
                widget.event_generate("<<Copy>>")
        except:
            pass
    
    def paste_text(self, widget):
        """Вставить текст"""
        try:
            widget.event_generate("<<Paste>>")
        except:
            pass
    
    def delete_text(self, widget):
        """Удалить весь текст"""
        try:
            widget.delete(0, tk.END)
        except:
            pass
    
    def delete_selected_text(self, widget):
        """Удалить выделенный текст"""
        try:
            if widget.selection_present():
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def select_all_text(self, widget):
        """Выделить весь текст"""
        try:
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)
        except:
            pass
    
    def undo_text(self, widget):
        """Отменить последнее действие"""
        try:
            widget.event_generate("<<Undo>>")
        except:
            pass
    
    def create_text_context_menu(self, text_widget):
        """Создание контекстного меню для многострочного текстового поля"""
        context_menu = tk.Menu(self.root, tearoff=0)
        
        context_menu.add_command(label="✂️ Вырезать", command=lambda: self.cut_text_widget(text_widget), accelerator="Ctrl+X")
        context_menu.add_command(label="📋 Копировать", command=lambda: self.copy_text_widget(text_widget), accelerator="Ctrl+C")
        context_menu.add_command(label="📥 Вставить", command=lambda: self.paste_text_widget(text_widget), accelerator="Ctrl+V")
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Удалить выделенное", command=lambda: self.delete_selected_text_widget(text_widget), accelerator="Delete")
        context_menu.add_command(label="🗑️ Очистить всё", command=lambda: self.clear_text_widget(text_widget))
        context_menu.add_command(label="📝 Выделить всё", command=lambda: self.select_all_text_widget(text_widget), accelerator="Ctrl+A")
        context_menu.add_separator()
        context_menu.add_command(label="🔍 Найти...", command=lambda: self.find_in_text(text_widget), accelerator="Ctrl+F")
        
        def show_context_menu(event):
            try:
                context_menu.post(event.x_root, event.y_root)
            except:
                pass
        
        # Привязываем контекстное меню к правой кнопке мыши
        text_widget.bind("<Button-3>", show_context_menu)
        
        # Привязываем горячие клавиши
        text_widget.bind("<Control-x>", lambda e: self.cut_text_widget(text_widget))
        text_widget.bind("<Control-c>", lambda e: self.copy_text_widget(text_widget))
        text_widget.bind("<Control-v>", lambda e: self.paste_text_widget(text_widget))
        text_widget.bind("<Control-a>", lambda e: self.select_all_text_widget(text_widget))
        text_widget.bind("<Control-f>", lambda e: self.find_in_text(text_widget))
        text_widget.bind("<Delete>", lambda e: self.delete_selected_text_widget(text_widget))
    
    def cut_text_widget(self, widget):
        """Вырезать текст из многострочного поля"""
        try:
            if widget.tag_ranges(tk.SEL):
                widget.event_generate("<<Cut>>")
        except:
            pass
    
    def copy_text_widget(self, widget):
        """Копировать текст из многострочного поля"""
        try:
            if widget.tag_ranges(tk.SEL):
                widget.event_generate("<<Copy>>")
        except:
            pass
    
    def paste_text_widget(self, widget):
        """Вставить текст в многострочное поле"""
        try:
            # Временно разблокируем поле если оно заблокировано
            was_disabled = str(widget['state']) == 'disabled'
            if was_disabled:
                widget.config(state=tk.NORMAL)
            
            widget.event_generate("<<Paste>>")
            
            # Возвращаем состояние
            if was_disabled:
                widget.config(state=tk.DISABLED)
        except:
            pass
    
    def delete_selected_text_widget(self, widget):
        """Удалить выделенный текст из многострочного поля"""
        try:
            if widget.tag_ranges(tk.SEL):
                was_disabled = str(widget['state']) == 'disabled'
                if was_disabled:
                    widget.config(state=tk.NORMAL)
                
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                
                if was_disabled:
                    widget.config(state=tk.DISABLED)
        except:
            pass
    
    def clear_text_widget(self, widget):
        """Очистить всё содержимое многострочного поля"""
        try:
            was_disabled = str(widget['state']) == 'disabled'
            if was_disabled:
                widget.config(state=tk.NORMAL)
            
            widget.delete(1.0, tk.END)
            
            if was_disabled:
                widget.config(state=tk.DISABLED)
        except:
            pass
    
    def select_all_text_widget(self, widget):
        """Выделить весь текст в многострочном поле"""
        try:
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        except:
            pass
    
    def find_in_text(self, widget):
        """Простой поиск в тексте"""
        try:
            search_term = simpledialog.askstring("Поиск", "Введите текст для поиска:")
            if search_term:
                # Убираем предыдущие выделения
                widget.tag_remove('found', '1.0', tk.END)
                
                # Ищем текст
                start_pos = '1.0'
                found_count = 0
                while True:
                    pos = widget.search(search_term, start_pos, tk.END)
                    if not pos:
                        break
                    
                    end_pos = f"{pos}+{len(search_term)}c"
                    widget.tag_add('found', pos, end_pos)
                    start_pos = end_pos
                    found_count += 1
                
                # Настраиваем выделение
                widget.tag_configure('found', background='yellow', foreground='black')
                
                # Переходим к первому найденному
                first_found = widget.tag_ranges('found')
                if first_found:
                    widget.see(first_found[0])
                    messagebox.showinfo("Поиск", f"Найдено совпадений: {found_count}")
                else:
                    messagebox.showinfo("Поиск", "Текст не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {e}")
    
    def load_from_file(self):
        """Загрузка текста из файла"""
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
                messagebox.showinfo("Успех", f"Файл загружен: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")
    
    def choose_output_file(self):
        """Выбор файла для сохранения результата"""
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
        """Очистка поля ввода"""
        self.text_input.delete(1.0, tk.END)
    
    def clear_result(self):
        """Очистка поля результата"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
    
    def call_api(self, prompt, api_key, site_url="", site_name="", model="qwen/qwen3-coder:free"):
        """Вызов API OpenRouter"""
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
                # Повторная попытка через 5 секунд
                time.sleep(5)
                return self.call_api(prompt, api_key, site_url, site_name, model)
            else:
                return f"Ошибка API: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Ошибка при вызове API: {e}"
    
    def process_text_thread(self):
        """Обработка текста в отдельном потоке"""
        try:
            # Получаем данные
            api_key = self.api_key.get().strip()
            if not api_key:
                messagebox.showerror("Ошибка", "API ключ обязателен!")
                return
            
            text_content = self.text_input.get(1.0, tk.END).strip()
            if not text_content:
                messagebox.showerror("Ошибка", "Введите текст для обработки!")
                return
            
            instruction = self.instruction_text.get(1.0, tk.END).strip()
            if instruction:
                prompt = f"{instruction}\n\n{text_content}"
            else:
                prompt = text_content
            
            # Определяем модель для использования
            selected_model = self.selected_model.get()
            if selected_model == "custom":
                model = self.custom_model.get().strip()
                if not model:
                    messagebox.showerror("Ошибка", "Введите название пользовательской модели!")
                    return
            else:
                model = selected_model
            
            site_url = self.site_url.get().strip()
            site_name = self.site_name.get().strip()
            
            # Вызываем API
            result = self.call_api(prompt, api_key, site_url, site_name, model)
            
            # Отображаем результат
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
            self.result_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("Успех", "Текст успешно обработан!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        
        finally:
            # Останавливаем прогресс бар и активируем кнопку
            self.progress.stop()
            self.process_button.config(state=tk.NORMAL, text="🚀 ОБРАБОТАТЬ ТЕКСТ")
    
    def process_text(self):
        """Запуск обработки текста"""
        # Деактивируем кнопку и запускаем прогресс бар
        self.process_button.config(state=tk.DISABLED, text="⏳ Обработка...")
        self.progress.start()
        
        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=self.process_text_thread)
        thread.daemon = True
        thread.start()
    
    def save_result(self):
        """Сохранение результата в файл"""
        try:
            result_content = self.result_text.get(1.0, tk.END).strip()
            if not result_content:
                messagebox.showwarning("Предупреждение", "Нет результата для сохранения!")
                return
            
            output_file = self.output_file_path.get().strip()
            if not output_file:
                output_file = "result.txt"
            
            # Создаем директорию если необходимо
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_content)
            
            messagebox.showinfo("Успех", f"Результат сохранен в файл: {output_file}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {e}")

def main():
    root = tk.Tk()
    app = SummaryGeneratorGUI(root)
    
    # Сохраняем настройки при закрытии окна
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
