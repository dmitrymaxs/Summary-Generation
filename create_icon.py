#!/usr/bin/env python3
"""
Скрипт для создания иконки приложения
"""

try:
    from PIL import Image, ImageDraw
    
    def create_summarize_icon():
        """Создание иконки для приложения суммаризации"""
        # Создаем изображение 32x32 с прозрачным фоном
        size = (32, 32)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Цвет иконки (темно-серый)
        color = (31, 31, 31, 255)  # #1F1F1F
        
        # Рисуем простую иконку документа с линиями (символизирующими текст)
        # Контур документа
        draw.rectangle([6, 4, 26, 28], outline=color, width=2)
        
        # Загнутый угол
        draw.polygon([(20, 4), (26, 4), (26, 10), (20, 4)], fill=color)
        
        # Линии текста
        draw.rectangle([9, 10, 23, 11], fill=color)
        draw.rectangle([9, 13, 20, 14], fill=color)
        draw.rectangle([9, 16, 23, 17], fill=color)
        draw.rectangle([9, 19, 18, 20], fill=color)
        draw.rectangle([9, 22, 23, 23], fill=color)
        draw.rectangle([9, 25, 21, 26], fill=color)
        
        return img
    
    def main():
        """Основная функция"""
        # Создаем иконку
        icon = create_summarize_icon()
        
        # Сохраняем в разных форматах
        icon.save('summarize_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.png', 'PNG')
        
        # Создаем ICO файл с несколькими размерами
        sizes = [(16, 16), (24, 24), (32, 32), (48, 48)]
        icons = []
        
        for size in sizes:
            resized = icon.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # Сохраняем как ICO файл
        icons[0].save('summarize_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.ico', 
                     format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
        
        print("Иконки созданы:")
        print("- summarize_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.png")
        print("- summarize_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.ico")
    
    if __name__ == "__main__":
        main()
        
except ImportError:
    print("Для создания иконки необходимо установить Pillow:")
    print("pip install Pillow")
