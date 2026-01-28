"""
Школьные конспекты - 1 класс
Полная версия приложения в одном файле
Для запуска установите: pip install PyQt5 Pillow
"""

import sys
import os
import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageQt

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ============================================
# КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
# ============================================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('school_notes.db', check_same_thread=False)
        self.create_tables()
        self.insert_default_data()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Таблица предметов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                color TEXT
            )
        ''')
        
        # Таблица готовых конспектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                title TEXT,
                content TEXT,
                grade INTEGER,
                created_at TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        # Таблица пользовательских конспектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                title TEXT,
                content TEXT,
                images TEXT,
                grade INTEGER DEFAULT 1,
                created_at TIMESTAMP
            )
        ''')
        
        # Таблица изображений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                image_data BLOB,
                FOREIGN KEY (note_id) REFERENCES notes (id)
            )
        ''')
        
        self.conn.commit()
    
    def insert_default_data(self):
        cursor = self.conn.cursor()
        
        # Добавляем предметы с цветами
        subjects = [
            ('Математика', '#3498db'),
            ('Русский язык', '#e74c3c'),
            ('Чтение', '#2ecc71'),
            ('Письмо', '#f39c12'),
            ('Окружающий мир', '#9b59b6'),
            ('Технология', '#1abc9c'),
            ('Физкультура', '#e67e22'),
            ('Музыка', '#34495e')
        ]
        
        for name, color in subjects:
            cursor.execute('INSERT OR IGNORE INTO subjects (name, color) VALUES (?, ?)', (name, color))
        
        # Примерные конспекты для 1 класса
        default_notes = [
            (1, 'Сложение и вычитание до 10', 
             '''📌 СЛОЖЕНИЕ:
• Объединение двух чисел
• Знак: + (плюс)
• Пример: 3 + 2 = 5

📌 ВЫЧИТАНИЕ:
• Удаление части
• Знак: - (минус)
• Пример: 5 - 2 = 3

📌 ПРАВИЛА:
1. От перестановки слагаемых сумма не меняется
2. Прибавить 0 - число не изменится
3. Вычесть 0 - число не изменится''', 1),
            
            (1, 'Цифры от 0 до 9',
             '''0 - ноль (ничего)
1 - один (точка)
2 - два (пара)
3 - три (треугольник)
4 - четыре (квадрат)
5 - пять (звезда)
6 - шесть
7 - семь
8 - восемь
9 - девять

🔢 Число - количество предметов
🔢 Цифра - знак для записи числа''', 1),
            
            (2, 'Гласные и согласные',
             '''🎵 ГЛАСНЫЕ ЗВУКИ (6):
А, О, У, Ы, И, Э
• Можно петь
• Образуют слог

🎵 СОГЛАСНЫЕ ЗВУКИ:
• Твердые: Б, В, Г, Д, З, К, Л, М, Н, П, Р, С, Т, Ф, Х
• Мягкие: Бь, Вь, Гь, Дь, Зь, Ль, Мь, Нь, Пь, Рь, Сь, Ть, Фь, Хь

❗ Й, Ч, Щ - всегда мягкие
❗ Ж, Ш, Ц - всегда твердые''', 1),
            
            (2, 'Алфавит',
             '''А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я

Всего 33 буквы:
• 10 гласных (А, Е, Ё, И, О, У, Ы, Э, Ю, Я)
• 21 согласная
• 2 знака (Ъ, Ь)''', 1),
            
            (5, 'Времена года',
             '''❄️ ЗИМА (декабрь, январь, февраль):
• Снег, лед, мороз
• Новый год, Рождество
• Зимние забавы

🌸 ВЕСНА (март, апрель, май):
• Таяние снега, ледоход
• Первые цветы, почки
• Возвращение птиц

☀️ ЛЕТО (июнь, июль, август):
• Тепло, солнце, дожди
• Ягоды, фрукты, овощи
• Каникулы, отдых

🍂 ОСЕНЬ (сентябрь, октябрь, ноябрь):
• Листопад, дожди, заморозки
• Уборка урожая
• Птицы улетают на юг''', 1),
            
            (5, 'Дни недели',
             '''📅 ПОРЯДОК ДНЕЙ:
1. Понедельник
2. Вторник
3. Среда
4. Четверг
5. Пятница
6. Суббота
7. Воскресенье

🎯 ЗАПОМИНАЛКА:
"Пошел Вторник за Средой,
В Четверг встретился с Пятницей,
Суббота с Воскресеньем
Гуляли целую неделю"''', 1),
            
            (3, 'Сказки для чтения',
             '''📖 РУССКИЕ НАРОДНЫЕ СКАЗКИ:
• "Колобок"
• "Репка"
• "Теремок"
• "Курочка Ряба"

📖 АВТОРСКИЕ СКАЗКИ:
• А.С. Пушкин - "Сказка о рыбаке и рыбке"
• К.И. Чуковский - "Мойдодыр", "Айболит"
• С.Я. Маршак - "Вот какой рассеянный"

🎯 КАК ЧИТАТЬ:
1. Читай вслух
2. Следи за пальцем
3. Делай паузы на точках
4. Выражай голосом эмоции''', 1),
            
            (4, 'Прописи букв',
             '''✏️ ПРАВИЛА ПИСЬМА:
1. Сиди прямо
2. Держи ручку правильно
3. Тетрадь под наклоном
4. Соблюдай наклон букв

🔤 ЭЛЕМЕНТЫ БУКВ:
│ - палочка
○ - овал
∩ - полуовал
∼ - крючок

📝 ПРИМЕРЫ:
А - две палочки и перекладина
О - овал
Л - треугольник
М - две палочки и две перекладины''', 1),
            
            (6, 'Аппликация из бумаги',
             '''✂️ МАТЕРИАЛЫ:
• Цветная бумага
• Ножницы (безопасные)
• Клей-карандаш
• Лист-основа

🎨 ПРОСТЫЕ ПОДЕЛКИ:
1. Гусеница (кружочки)
2. Домик (геометрические фигуры)
3. Цветок (лепестки и серединка)
4. Рыбка (треугольники)

⚠️ ПРАВИЛА БЕЗОПАСНОСТИ:
• Ножницы передавай кольцами вперед
• Не бери клей в рот
• Работай на клеенке''', 1)
        ]
        
        for subject_id, title, content, grade in default_notes:
            cursor.execute('SELECT 1 FROM notes WHERE title = ?', (title,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO notes (subject_id, title, content, grade, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (subject_id, title, content, grade, datetime.now()))
        
        self.conn.commit()
    
    def get_subjects(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM subjects ORDER BY id')
        return cursor.fetchall()
    
    def get_notes_by_subject(self, subject_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT n.*, s.name as subject_name, s.color
            FROM notes n 
            JOIN subjects s ON n.subject_id = s.id 
            WHERE n.subject_id = ? AND n.grade = 1
            ORDER BY n.title
        ''', (subject_id,))
        return cursor.fetchall()
    
    def search_notes(self, keyword):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT n.*, s.name as subject_name, s.color
            FROM notes n 
            JOIN subjects s ON n.subject_id = s.id 
            WHERE (n.title LIKE ? OR n.content LIKE ?) AND n.grade = 1
            ORDER BY n.title
        ''', (f'%{keyword}%', f'%{keyword}%'))
        return cursor.fetchall()
    
    def get_all_notes(self, subject_filter=None):
        """Получить все конспекты с возможностью фильтрации по предмету"""
        cursor = self.conn.cursor()
        
        if subject_filter:
            # Фильтр по конкретному предмету
            cursor.execute('''
                SELECT n.*, s.name as subject_name, s.color
                FROM notes n 
                JOIN subjects s ON n.subject_id = s.id 
                WHERE n.grade = 1 AND s.name = ?
                ORDER BY s.name, n.title
            ''', (subject_filter,))
        else:
            # Все конспекты без фильтра
            cursor.execute('''
                SELECT n.*, s.name as subject_name, s.color
                FROM notes n 
                JOIN subjects s ON n.subject_id = s.id 
                WHERE n.grade = 1
                ORDER BY s.name, n.title
            ''')
        
        return cursor.fetchall()
    
    def add_user_note(self, subject, title, content, images, grade=1):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO user_notes (subject, title, content, images, grade, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (subject, title, content, json.dumps(images), grade, datetime.now()))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_notes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM user_notes ORDER BY created_at DESC')
        return cursor.fetchall()
    
    def delete_user_note(self, note_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM user_notes WHERE id = ?', (note_id,))
        self.conn.commit()
    
    def update_user_note(self, note_id, subject, title, content, images):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE user_notes 
            SET subject = ?, title = ?, content = ?, images = ?
            WHERE id = ?
        ''', (subject, title, content, json.dumps(images), note_id))
        self.conn.commit()
    
    def get_statistics(self):
        cursor = self.conn.cursor()
        
        # Общее количество конспектов
        cursor.execute('SELECT COUNT(*) FROM notes WHERE grade = 1')
        default_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM user_notes')
        user_count = cursor.fetchone()[0]
        
        # Конспекты по предметам
        cursor.execute('''
            SELECT s.name, COUNT(n.id) 
            FROM notes n 
            JOIN subjects s ON n.subject_id = s.id 
            WHERE n.grade = 1
            GROUP BY s.name
        ''')
        by_subject = cursor.fetchall()
        
        return {
            'default_notes': default_count,
            'user_notes': user_count,
            'by_subject': by_subject
        }
    
    def close(self):
        self.conn.close()


# ============================================
# ВИДЖЕТ ДЛЯ ПРОСМОТРА КОНСПЕКТА С ПОДСВЕТКОЙ ПОИСКА
# ============================================
class NoteViewer(QDialog):
    def __init__(self, note_data, parent=None, search_word=None):
        super().__init__(parent)
        self.note_data = note_data
        self.images = note_data.get('images', [])
        self.current_image_index = 0
        self.search_word = search_word.lower() if search_word else None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.note_data['title'])
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel(self.note_data['title'])
        title_label.setStyleSheet('''
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            border-bottom: 2px solid #3498db;
            background-color: #f8f9fa;
        ''')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Информация о предмете
        info_layout = QHBoxLayout()
        
        subject_label = QLabel(f"📚 {self.note_data.get('subject', '')}")
        subject_label.setStyleSheet('font-size: 14px; color: #7f8c8d; padding: 5px;')
        
        grade_label = QLabel(f"1 класс")
        grade_label.setStyleSheet('''
            font-size: 12px;
            color: white;
            background-color: #3498db;
            padding: 3px 10px;
            border-radius: 10px;
        ''')
        
        info_layout.addWidget(subject_label)
        info_layout.addStretch()
        info_layout.addWidget(grade_label)
        layout.addLayout(info_layout)
        
        # Контент с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Текст конспекта с подсветкой поиска
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        
        # Форматируем контент с подсветкой поиска
        formatted_content = self.format_content_with_highlight(
            self.note_data['content'], 
            self.search_word
        )
        content_text.setHtml(formatted_content)
        content_text.setStyleSheet('''
            QTextEdit {
                font-size: 14px;
                line-height: 1.6;
                padding: 15px;
                border: none;
                background-color: white;
            }
        ''')
        content_layout.addWidget(content_text)
        
        # Изображения
        if self.images:
            images_group = QGroupBox("📷 Изображения")
            images_group.setStyleSheet('''
                QGroupBox {
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            ''')
            
            images_layout = QVBoxLayout()
            
            # Просмотрщик изображений
            self.image_label = QLabel()
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setMinimumHeight(300)
            self.image_label.setStyleSheet('border: 1px solid #ddd; background-color: #f5f5f5;')
            images_layout.addWidget(self.image_label)
            
            # Кнопки навигации по изображениям
            if len(self.images) > 1:
                nav_layout = QHBoxLayout()
                nav_layout.addStretch()
                
                self.prev_btn = QPushButton("◀ Назад")
                self.prev_btn.clicked.connect(self.show_prev_image)
                self.prev_btn.setEnabled(False)
                
                self.image_counter = QLabel(f"1 / {len(self.images)}")
                self.image_counter.setStyleSheet('font-weight: bold;')
                
                self.next_btn = QPushButton("Вперед ▶")
                self.next_btn.clicked.connect(self.show_next_image)
                if len(self.images) == 1:
                    self.next_btn.setEnabled(False)
                
                nav_layout.addWidget(self.prev_btn)
                nav_layout.addWidget(self.image_counter)
                nav_layout.addWidget(self.next_btn)
                nav_layout.addStretch()
                
                images_layout.addLayout(nav_layout)
            
            images_group.setLayout(images_layout)
            content_layout.addWidget(images_group)
            
            # Загружаем первое изображение
            self.load_current_image()
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ Печать")
        print_btn.clicked.connect(self.print_note)
        
        export_btn = QPushButton("💾 Сохранить")
        export_btn.clicked.connect(self.export_note)
        
        close_btn = QPushButton("✕ Закрыть")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet('background-color: #e74c3c; color: white; font-weight: bold;')
        
        button_layout.addWidget(print_btn)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def format_content_with_highlight(self, content, search_word):
        """Форматирует текст с подсветкой найденных слов"""
        if not search_word:
            return self.format_content(content)
        
        # Преобразуем маркеры списка
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            # Подсвечиваем искомые слова (без учета регистра)
            if search_word:
                line_lower = line.lower()
                start_pos = 0
                result_line = ""
                
                while True:
                    pos = line_lower.find(search_word, start_pos)
                    if pos == -1:
                        result_line += line[start_pos:]
                        break
                    
                    # Добавляем часть до найденного слова
                    result_line += line[start_pos:pos]
                    
                    # Добавляем подсвеченное слово
                    result_line += f'<span style="background-color: #FFD700; font-weight: bold;">{line[pos:pos+len(search_word)]}</span>'
                    
                    start_pos = pos + len(search_word)
                
                line = result_line
            
            # Применяем остальное форматирование
            if line.strip().startswith('•'):
                html_lines.append(f'<li>{line.strip()[1:].strip()}</li>')
            elif line.strip().startswith('📌') or line.strip().startswith('🎵') or line.strip().startswith('❗'):
                html_lines.append(f'<p style="font-weight: bold; color: #2c3e50; margin-top: 10px;">{line}</p>')
            elif line.strip().startswith('🔢') or line.strip().startswith('🎯'):
                html_lines.append(f'<p style="color: #3498db; margin-left: 20px;">{line}</p>')
            elif line.strip().startswith('📅') or line.strip().startswith('📝'):
                html_lines.append(f'<p style="background-color: #f8f9fa; padding: 8px; border-radius: 5px;">{line}</p>')
            elif line.strip():
                html_lines.append(f'<p>{line}</p>')
            else:
                html_lines.append('<br>')
        
        html_content = ''.join(html_lines)
        return f'''
        <html>
        <head>
            <style>
                .highlight {{
                    background-color: #FFD700;
                    font-weight: bold;
                    padding: 1px 3px;
                    border-radius: 3px;
                }}
            </style>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            {html_content}
        </body>
        </html>
        '''
    
    def format_content(self, content):
        """Форматирует текст для отображения в HTML"""
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            if line.strip().startswith('•'):
                html_lines.append(f'<li>{line.strip()[1:].strip()}</li>')
            elif line.strip().startswith('📌') or line.strip().startswith('🎵') or line.strip().startswith('❗'):
                html_lines.append(f'<p style="font-weight: bold; color: #2c3e50; margin-top: 10px;">{line}</p>')
            elif line.strip().startswith('🔢') or line.strip().startswith('🎯'):
                html_lines.append(f'<p style="color: #3498db; margin-left: 20px;">{line}</p>')
            elif line.strip().startswith('📅') or line.strip().startswith('📝'):
                html_lines.append(f'<p style="background-color: #f8f9fa; padding: 8px; border-radius: 5px;">{line}</p>')
            elif line.strip():
                html_lines.append(f'<p>{line}</p>')
            else:
                html_lines.append('<br>')
        
        html_content = ''.join(html_lines)
        return f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            {html_content}
        </body>
        </html>
        '''
    
    def load_current_image(self):
        if self.images and self.current_image_index < len(self.images):
            image_path = self.images[self.current_image_index]
            try:
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # Масштабируем изображение
                        scaled_pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.image_label.setPixmap(scaled_pixmap)
                        
                        # Обновляем счетчик
                        self.image_counter.setText(f"{self.current_image_index + 1} / {len(self.images)}")
                        
                        # Обновляем состояние кнопок
                        self.prev_btn.setEnabled(self.current_image_index > 0)
                        self.next_btn.setEnabled(self.current_image_index < len(self.images) - 1)
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
    
    def show_next_image(self):
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.load_current_image()
    
    def show_prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_current_image()
    
    def print_note(self):
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        
        if print_dialog.exec_() == QPrintDialog.Accepted:
            # Создаем документ для печати
            document = QTextDocument()
            html = f'''
            <h1>{self.note_data['title']}</h1>
            <h3>Предмет: {self.note_data.get('subject', '')} | 1 класс</h3>
            <hr>
            <div style="white-space: pre-wrap;">{self.note_data['content']}</div>
            '''
            document.setHtml(html)
            document.print_(printer)
    
    def export_note(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конспект",
            f"{self.note_data['title']}.txt",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Конспект: {self.note_data['title']}\n")
                    f.write(f"Предмет: {self.note_data.get('subject', '')}\n")
                    f.write(f"Класс: 1\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.note_data['content'])
                
                QMessageBox.information(self, "Успех", f"Конспект сохранен в файл:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


# ============================================
# РЕДАКТОР КОНСПЕКТОВ
# ============================================
class NoteEditor(QDialog):
    def __init__(self, parent=None, note_data=None, mode='create'):
        super().__init__(parent)
        self.note_data = note_data or {}
        self.mode = mode
        self.images = self.note_data.get('images', [])
        self.initUI()
        
        if mode == 'edit' and note_data:
            self.load_existing_data()
    
    def initUI(self):
        self.setWindowTitle("Редактор конспекта" if self.mode == 'edit' else "Создать конспект")
        self.setMinimumSize(700, 600)
        
        main_layout = QVBoxLayout()
        
        # Заголовок редактора
        title_label = QLabel("📝 Редактор конспекта")
        title_label.setStyleSheet('''
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
        ''')
        main_layout.addWidget(title_label)
        
        # Форма
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Предмет
        self.subject_combo = QComboBox()
        self.subject_combo.addItems([
            "Математика", "Русский язык", "Чтение", 
            "Письмо", "Окружающий мир", "Технология",
            "Физкультура", "Музыка"
        ])
        form_layout.addRow("Предмет:", self.subject_combo)
        
        # Заголовок
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Введите название конспекта")
        form_layout.addRow("Заголовок:", self.title_edit)
        
        # Контент
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Введите текст конспекта...\n\nИспользуйте:\n• для списков\n📌 для важных пунктов\n🎯 для правил")
        self.content_edit.setMinimumHeight(200)
        
        # Панель форматирования
        format_toolbar = QToolBar()
        
        bold_btn = QAction("Ж", self)
        bold_btn.triggered.connect(lambda: self.format_text('bold'))
        bold_btn.setToolTip("Жирный текст")
        
        italic_btn = QAction("К", self)
        italic_btn.triggered.connect(lambda: self.format_text('italic'))
        italic_btn.setToolTip("Курсив")
        
        bullet_btn = QAction("•", self)
        bullet_btn.triggered.connect(lambda: self.format_text('bullet'))
        bullet_btn.setToolTip("Маркированный список")
        
        format_toolbar.addAction(bold_btn)
        format_toolbar.addAction(italic_btn)
        format_toolbar.addAction(bullet_btn)
        
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Содержание:"))
        content_layout.addWidget(format_toolbar)
        content_layout.addWidget(self.content_edit)
        
        main_layout.addLayout(form_layout)
        main_layout.addLayout(content_layout)
        
        # Загрузка изображений
        images_group = QGroupBox("📷 Изображения")
        images_layout = QVBoxLayout()
        
        # Кнопки загрузки
        upload_layout = QHBoxLayout()
        self.upload_btn = QPushButton("📁 Загрузить изображение")
        self.upload_btn.clicked.connect(self.upload_image)
        
        self.capture_btn = QPushButton("📷 Сделать фото (если есть камера)")
        self.capture_btn.clicked.connect(self.capture_photo)
        self.capture_btn.setEnabled(False)  # Отключаем, пока не реализовано
        
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addWidget(self.capture_btn)
        upload_layout.addStretch()
        
        # Список изображений
        self.image_list = QListWidget()
        self.image_list.setMaximumHeight(100)
        
        # Кнопки управления изображениями
        image_buttons_layout = QHBoxLayout()
        self.remove_image_btn = QPushButton("Удалить выбранное")
        self.remove_image_btn.clicked.connect(self.remove_image)
        self.remove_image_btn.setEnabled(False)
        
        self.image_list.itemSelectionChanged.connect(
            lambda: self.remove_image_btn.setEnabled(bool(self.image_list.selectedItems()))
        )
        
        image_buttons_layout.addWidget(self.remove_image_btn)
        image_buttons_layout.addStretch()
        
        images_layout.addLayout(upload_layout)
        images_layout.addWidget(self.image_list)
        images_layout.addLayout(image_buttons_layout)
        images_group.setLayout(images_layout)
        
        main_layout.addWidget(images_group)
        
        # Шаблоны
        templates_group = QGroupBox("📋 Шаблоны")
        templates_layout = QHBoxLayout()
        
        math_template_btn = QPushButton("Математика")
        math_template_btn.clicked.connect(lambda: self.insert_template('math'))
        
        reading_template_btn = QPushButton("Чтение")
        reading_template_btn.clicked.connect(lambda: self.insert_template('reading'))
        
        world_template_btn = QPushButton("Окружающий мир")
        world_template_btn.clicked.connect(lambda: self.insert_template('world'))
        
        templates_layout.addWidget(math_template_btn)
        templates_layout.addWidget(reading_template_btn)
        templates_layout.addWidget(world_template_btn)
        templates_group.setLayout(templates_layout)
        
        main_layout.addWidget(templates_group)
        
        # Кнопки сохранения/отмены
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.save_note)
        save_btn.setStyleSheet('background-color: #2ecc71; color: white; font-weight: bold; padding: 8px;')
        
        cancel_btn = QPushButton("✕ Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 8px;')
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def load_existing_data(self):
        if 'subject' in self.note_data:
            index = self.subject_combo.findText(self.note_data['subject'])
            if index >= 0:
                self.subject_combo.setCurrentIndex(index)
        
        if 'title' in self.note_data:
            self.title_edit.setText(self.note_data['title'])
        
        if 'content' in self.note_data:
            self.content_edit.setPlainText(self.note_data['content'])
        
        if 'images' in self.note_data:
            self.images = self.note_data['images']
            for img in self.images:
                self.image_list.addItem(os.path.basename(img))
    
    def format_text(self, style):
        cursor = self.content_edit.textCursor()
        
        if style == 'bold':
            format = QTextCharFormat()
            format.setFontWeight(QFont.Bold)
            cursor.mergeCharFormat(format)
        elif style == 'italic':
            format = QTextCharFormat()
            format.setFontItalic(True)
            cursor.mergeCharFormat(format)
        elif style == 'bullet':
            self.content_edit.insertPlainText('• ')
    
    def insert_template(self, template_type):
        templates = {
            'math': '''📌 ТЕМА:
• Правило 1
• Правило 2
• Правило 3

🎯 ПРИМЕРЫ:
1) Пример 1
2) Пример 2
3) Пример 3

❗ ЗАПОМНИ:
Важное правило''',
            
            'reading': '''📖 ПРОИЗВЕДЕНИЕ:
Автор: 
Жанр: 

👥 ГЕРОИ:
• Персонаж 1
• Персонаж 2

🎯 ГЛАВНАЯ МЫСЛЬ:
Текст главной мысли''',
            
            'world': '''🌍 ТЕМА:
📅 Время года/период:
📍 Место:

📌 ОСОБЕННОСТИ:
• Особенность 1
• Особенность 2
• Особенность 3

🖼️ ИЛЛЮСТРАЦИИ:
[описание изображения]'''
        }
        
        if template_type in templates:
            self.content_edit.insertPlainText(templates[template_type])
    
    def upload_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Изображения (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            for filename in filenames:
                # Копируем изображение в папку приложения
                app_images_dir = "user_images"
                os.makedirs(app_images_dir, exist_ok=True)
                
                dest_filename = f"{int(datetime.now().timestamp())}_{os.path.basename(filename)}"
                dest_path = os.path.join(app_images_dir, dest_filename)
                
                try:
                    shutil.copy2(filename, dest_path)
                    self.images.append(dest_path)
                    self.image_list.addItem(dest_filename)
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
    
    def capture_photo(self):
        # Заглушка для функции фото
        QMessageBox.information(self, "Информация", "Функция фото будет добавлена в будущей версии")
    
    def remove_image(self):
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            row = self.image_list.row(item)
            self.image_list.takeItem(row)
            
            # Удаляем файл
            if row < len(self.images):
                try:
                    if os.path.exists(self.images[row]):
                        os.remove(self.images[row])
                except:
                    pass
                self.images.pop(row)
    
    def save_note(self):
        subject = self.subject_combo.currentText().strip()
        title = self.title_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        # Валидация
        errors = []
        
        if not subject:
            errors.append("Выберите предмет")
        
        if not title:
            errors.append("Введите название конспекта")
        
        if not content:
            errors.append("Введите содержание конспекта")
        
        if errors:
            QMessageBox.warning(self, "Ошибка", "Исправьте следующие ошибки:\n• " + "\n• ".join(errors))
            return
        
        self.note_data = {
            'subject': subject,
            'title': title,
            'content': content,
            'images': self.images,
            'grade': 1
        }
        
        self.accept()
    
    def get_note_data(self):
        return self.note_data


# ============================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ============================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_notes = []
        self.current_search_word = None  # Сохраняем текущее слово поиска
        self.current_subject_filter = None  # Сохраняем текущий фильтр предмета
        self.initUI()
        self.load_initial_data()
        
        # Создаем необходимые папки
        self.create_folders()
    
    def create_folders(self):
        folders = ['user_images', 'exports', 'backups']
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    def initUI(self):
        self.setWindowTitle('Школьные конспекты - 1 класс')
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель (сайдбар)
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Логотип и заголовок
        logo_label = QLabel("📚 ШКОЛЬНЫЕ\nКОНСПЕКТЫ")
        logo_label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 10px;
            text-align: center;
        ''')
        logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_label)
        
        sidebar_layout.addSpacing(10)
        
        # Поиск
        search_group = QGroupBox("🔍 Поиск")
        search_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите слово для поиска...")
        self.search_input.returnPressed.connect(self.on_search_advanced)
        
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.on_search_advanced)
        search_btn.setStyleSheet('background-color: #3498db; color: white; padding: 5px;')
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_group.setLayout(search_layout)
        sidebar_layout.addWidget(search_group)
        
        sidebar_layout.addSpacing(10)
        
        # Предметы
        subjects_group = QGroupBox("📖 Предметы")
        subjects_layout = QVBoxLayout()
        
        self.all_notes_btn = QPushButton("📚 Все конспекты")
        self.all_notes_btn.clicked.connect(self.show_all_notes)
        self.all_notes_btn.setStyleSheet('''
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        ''')
        subjects_layout.addWidget(self.all_notes_btn)
        
        subjects_layout.addWidget(QLabel(" "))
        
        # Кнопки предметов будут добавлены динамически
        self.subject_buttons = []
        subjects_group.setLayout(subjects_layout)
        sidebar_layout.addWidget(subjects_group)
        
        sidebar_layout.addSpacing(10)
        
        # Мои конспекты
        my_notes_group = QGroupBox("💼 Мои конспекты")
        my_notes_layout = QVBoxLayout()
        
        self.my_notes_btn = QPushButton("📓 Мои записи")
        self.my_notes_btn.clicked.connect(self.show_user_notes)
        self.my_notes_btn.setStyleSheet('''
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                background-color: #f39c12;
                color: white;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        ''')
        my_notes_layout.addWidget(self.my_notes_btn)
        
        create_note_btn = QPushButton("✏️ Создать конспект")
        create_note_btn.clicked.connect(self.create_user_note)
        create_note_btn.setStyleSheet('''
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                background-color: #2ecc71;
                color: white;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        ''')
        my_notes_layout.addWidget(create_note_btn)
        
        import_note_btn = QPushButton("📥 Импорт из файла")
        import_note_btn.clicked.connect(self.import_note)
        import_note_btn.setStyleSheet('''
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                background-color: #9b59b6;
                color: white;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        ''')
        my_notes_layout.addWidget(import_note_btn)
        
        my_notes_group.setLayout(my_notes_layout)
        sidebar_layout.addWidget(my_notes_group)
        
        sidebar_layout.addSpacing(10)
        
        # Статистика
        stats_group = QGroupBox("📊 Статистика")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Загрузка...")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet('font-size: 12px; color: #7f8c8d;')
        stats_layout.addWidget(self.stats_label)
        
        refresh_stats_btn = QPushButton("🔄 Обновить")
        refresh_stats_btn.clicked.connect(self.update_statistics)
        refresh_stats_btn.setStyleSheet('padding: 5px;')
        stats_layout.addWidget(refresh_stats_btn)
        
        stats_group.setLayout(stats_layout)
        sidebar_layout.addWidget(stats_group)
        
        sidebar_layout.addStretch()
        
        main_layout.addWidget(self.sidebar)
        
        # Основная область
        self.main_area = QStackedWidget()
        main_layout.addWidget(self.main_area)
        
        # Создаем начальный экран
        self.create_welcome_screen()
        
        # Создаем меню
        self.create_menu()
        
        # Создаем статус бар
        self.statusBar().showMessage("Готово к работе")
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        
        new_note_action = QAction('Новый конспект', self)
        new_note_action.triggered.connect(self.create_user_note)
        file_menu.addAction(new_note_action)
        
        import_action = QAction('Импорт...', self)
        import_action.triggered.connect(self.import_note)
        file_menu.addAction(import_action)
        
        export_action = QAction('Экспорт всех...', self)
        export_action.triggered.connect(self.export_all_notes)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Правка
        edit_menu = menubar.addMenu('Правка')
        
        search_action = QAction('Поиск', self)
        search_action.setShortcut('Ctrl+F')
        search_action.triggered.connect(lambda: self.search_input.setFocus())
        edit_menu.addAction(search_action)
        
        # Меню Вид
        view_menu = menubar.addMenu('Вид')
        
        refresh_action = QAction('Обновить', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_view)
        view_menu.addAction(refresh_action)
        
        # Меню Справка
        help_menu = menubar.addMenu('Справка')
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction('Помощь', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def create_welcome_screen(self):
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Заголовок
        title = QLabel("Добро пожаловать!")
        title.setStyleSheet('font-size: 32px; font-weight: bold; color: #2c3e50;')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Школьные конспекты - 1 класс")
        subtitle.setStyleSheet('font-size: 18px; color: #7f8c8d; margin-bottom: 30px;')
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Карточки предметов
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        subjects = [
            ("Математика", "#3498db", "Счет, сложение, вычитание"),
            ("Русский язык", "#e74c3c", "Буквы, звуки, алфавит"),
            ("Чтение", "#2ecc71", "Сказки, рассказы, стихи"),
            ("Окружающий мир", "#9b59b6", "Природа, времена года"),
            ("Письмо", "#f39c12", "Прописи, элементы букв"),
            ("Технология", "#1abc9c", "Поделки, аппликации")
        ]
        
        for i, (name, color, desc) in enumerate(subjects):
            card = QFrame()
            card.setMinimumSize(200, 150)
            card.setStyleSheet(f'''
                QFrame {{
                    background-color: {color};
                    border-radius: 10px;
                    padding: 15px;
                }}
                QLabel {{
                    color: white;
                }}
            ''')
            
            card_layout = QVBoxLayout(card)
            
            icon_label = QLabel("📘" if name == "Математика" else "📗")
            icon_label.setStyleSheet('font-size: 24px;')
            icon_label.setAlignment(Qt.AlignCenter)
            
            name_label = QLabel(name)
            name_label.setStyleSheet('font-size: 16px; font-weight: bold;')
            name_label.setAlignment(Qt.AlignCenter)
            
            desc_label = QLabel(desc)
            desc_label.setStyleSheet('font-size: 12px;')
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            
            card_layout.addWidget(icon_label)
            card_layout.addWidget(name_label)
            card_layout.addWidget(desc_label)
            
            # Делаем карточку кликабельной
            card.mousePressEvent = lambda e, n=name: self.on_subject_click(n)
            
            row, col = divmod(i, 3)
            grid_layout.addWidget(card, row, col)
        
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        # Кнопка быстрого старта
        quick_start_btn = QPushButton("🚀 Начать использование")
        quick_start_btn.clicked.connect(self.show_all_notes)
        quick_start_btn.setStyleSheet('''
            QPushButton {
                font-size: 16px;
                padding: 15px;
                background-color: #2c3e50;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        ''')
        quick_start_btn.setFixedWidth(300)
        
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()
        btn_layout.addWidget(quick_start_btn)
        btn_layout.addStretch()
        
        layout.addWidget(btn_container)
        layout.addStretch()
        
        self.main_area.addWidget(welcome_widget)
    
    def on_subject_click(self, subject_name):
        # Находим ID предмета по имени
        subjects = self.db.get_subjects()
        for subject_id, name, color in subjects:
            if name == subject_name:
                self.show_subject_notes(subject_id)
                break
    
    def load_initial_data(self):
        # Загружаем предметы
        subjects = self.db.get_subjects()
        
        # Находим layout предметов
        subjects_group = self.sidebar.findChild(QGroupBox, "📖 Предметы")
        if subjects_group:
            subjects_layout = subjects_group.layout()
            
            # Удаляем существующие кнопки (кроме первых двух виджетов)
            while subjects_layout.count() > 2:
                item = subjects_layout.takeAt(2)
                if item.widget():
                    item.widget().deleteLater()
            
            self.subject_buttons = []
            
            # Добавляем кнопки предметов
            for subject_id, name, color in subjects:
                btn = QPushButton(f"📘 {name}")
                btn.setProperty('subject_id', subject_id)
                btn.setProperty('color', color)
                btn.setStyleSheet(f'''
                    QPushButton {{
                        text-align: left;
                        padding: 10px;
                        font-size: 14px;
                        border: none;
                        border-radius: 5px;
                        background-color: {color}20;
                        color: {color};
                    }}
                    QPushButton:hover {{
                        background-color: {color};
                        color: white;
                    }}
                ''')
                btn.clicked.connect(lambda checked, sid=subject_id: self.show_subject_notes(sid))
                subjects_layout.addWidget(btn)
                self.subject_buttons.append(btn)
        
        # Обновляем статистику
        self.update_statistics()
    
    def update_statistics(self):
        stats = self.db.get_statistics()
        
        stats_text = f"""📊 Статистика:

Готовых конспектов: {stats['default_notes']}
Мои конспекты: {stats['user_notes']}

По предметам:
"""
        for subject, count in stats['by_subject']:
            stats_text += f"  {subject}: {count}\n"
        
        self.stats_label.setText(stats_text)
    
    def show_subject_notes(self, subject_id):
        self.current_subject_filter = None  # Сбрасываем фильтр предмета
        self.current_search_word = None  # Сбрасываем слово поиска
        self.current_notes = self.db.get_notes_by_subject(subject_id)
        self.show_notes_list("конспекты")
    
    def show_all_notes(self):
        self.current_subject_filter = None  # Сбрасываем фильтр предмета
        self.current_search_word = None  # Сбрасываем слово поиска
        self.current_notes = self.db.get_all_notes()
        self.show_notes_list("все конспекты")
    
    def show_user_notes(self):
        self.current_subject_filter = None  # Сбрасываем фильтр предмета
        self.current_search_word = None  # Сбрасываем слово поиска
        self.current_notes = self.db.get_user_notes()
        self.show_notes_list("мои конспекты", is_user_notes=True)
    
    def show_notes_list(self, title, is_user_notes=False):
        # Создаем виджет со списком
        notes_widget = QWidget()
        layout = QVBoxLayout(notes_widget)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        
        # Заголовок
        title_label = QLabel(f"📚 {title.title()}")
        title_label.setStyleSheet('''
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        ''')
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        # Если это "Все конспекты", добавляем фильтр по предметам
        if "все конспекты" in title.lower() and not self.current_search_word:
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(QLabel("Фильтр по предмету:"))
            
            self.subject_filter_combo = QComboBox()
            self.subject_filter_combo.addItem("Все предметы")
            subjects = self.db.get_subjects()
            for subject_id, name, color in subjects:
                self.subject_filter_combo.addItem(name)
            
            # Устанавливаем текущий выбранный предмет, если фильтр активен
            if self.current_subject_filter:
                index = self.subject_filter_combo.findText(self.current_subject_filter)
                if index >= 0:
                    self.subject_filter_combo.setCurrentIndex(index)
            
            self.subject_filter_combo.currentTextChanged.connect(self.apply_subject_filter)
            
            # Кнопка сброса фильтра
            reset_filter_btn = QPushButton("Сбросить фильтр")
            reset_filter_btn.clicked.connect(self.reset_subject_filter)
            reset_filter_btn.setStyleSheet('padding: 5px; background-color: #95a5a6; color: white;')
            
            filter_layout.addWidget(self.subject_filter_combo)
            filter_layout.addWidget(reset_filter_btn)
            toolbar_layout.addLayout(filter_layout)
        
        # Показываем текущий фильтр поиска, если он активен
        if self.current_search_word:
            search_info = QLabel(f"🔍 Поиск: '{self.current_search_word}'")
            search_info.setStyleSheet('''
                background-color: #FFD70030;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            ''')
            
            clear_search_btn = QPushButton("✕ Очистить поиск")
            clear_search_btn.clicked.connect(self.clear_search)
            clear_search_btn.setStyleSheet('padding: 5px; background-color: #e74c3c; color: white;')
            
            toolbar_layout.addWidget(search_info)
            toolbar_layout.addWidget(clear_search_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet('background-color: #3498db;')
        layout.addWidget(separator)
        
        if not self.current_notes:
            # Сообщение, если конспектов нет
            no_notes_label = QLabel("Конспектов не найдено")
            no_notes_label.setStyleSheet('font-size: 16px; color: #7f8c8d; padding: 50px;')
            no_notes_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_notes_label)
        else:
            # Создаем scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            
            container = QWidget()
            container_layout = QVBoxLayout(container)
            
            # Группируем по предметам, если это не пользовательские заметки
            if not is_user_notes:
                notes_by_subject = {}
                for note in self.current_notes:
                    subject_name = note[7]  # subject_name из запроса
                    if subject_name not in notes_by_subject:
                        notes_by_subject[subject_name] = []
                    notes_by_subject[subject_name].append(note)
                
                for subject_name, notes in notes_by_subject.items():
                    # Заголовок предмета
                    subject_header = QLabel(subject_name)
                    subject_header.setStyleSheet('''
                        font-size: 16px;
                        font-weight: bold;
                        color: #34495e;
                        background-color: #ecf0f1;
                        padding: 10px;
                        border-radius: 5px;
                        margin-top: 20px;
                    ''')
                    container_layout.addWidget(subject_header)
                    
                    # Конспекты этого предмета
                    for note in notes:
                        container_layout.addWidget(self.create_note_card(note, is_user_notes))
            else:
                # Для пользовательских заметок - просто список
                for note in self.current_notes:
                    container_layout.addWidget(self.create_note_card(note, is_user_notes))
            
            container_layout.addStretch()
            scroll_area.setWidget(container)
            layout.addWidget(scroll_area)
        
        # Добавляем виджет в стек
        self.main_area.addWidget(notes_widget)
        self.main_area.setCurrentWidget(notes_widget)
    
    def apply_subject_filter(self, subject_name):
        """Применяет фильтр по предмету"""
        if subject_name == "Все предметы":
            self.current_subject_filter = None
            self.current_notes = self.db.get_all_notes()
        else:
            self.current_subject_filter = subject_name
            self.current_notes = self.db.get_all_notes(subject_filter=subject_name)
        
        self.show_notes_list("все конспекты")
    
    def reset_subject_filter(self):
        """Сбрасывает фильтр по предмету"""
        self.current_subject_filter = None
        self.current_notes = self.db.get_all_notes()
        self.show_notes_list("все конспекты")
    
    def clear_search(self):
        """Очищает поиск"""
        self.current_search_word = None
        self.search_input.clear()
        self.show_all_notes()
    
    def create_note_card(self, note, is_user_note=False):
        """Создает карточку конспекта"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet('''
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        ''')
        
        card_layout = QVBoxLayout(card)
        
        # Заголовок
        title_label = QLabel(note[2])  # title
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #2c3e50;')
        title_label.setWordWrap(True)
        
        # Предмет и цвет
        subject_color = note[8] if len(note) > 8 else '#3498db'
        subject_name = note[7] if len(note) > 7 else 'Предмет'
        
        subject_widget = QWidget()
        subject_layout = QHBoxLayout(subject_widget)
        
        subject_label = QLabel(subject_name)
        subject_label.setStyleSheet(f'color: {subject_color}; font-weight: bold;')
        
        grade_label = QLabel("1 класс")
        grade_label.setStyleSheet('''
            background-color: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
        ''')
        
        subject_layout.addWidget(subject_label)
        subject_layout.addStretch()
        subject_layout.addWidget(grade_label)
        
        # Краткое содержание с подсветкой поиска
        content_preview_text = note[3][:100] + "..." if len(note[3]) > 100 else note[3]
        
        # Если есть слово поиска, подсвечиваем его в preview
        if self.current_search_word:
            search_word_lower = self.current_search_word.lower()
            content_lower = content_preview_text.lower()
            if search_word_lower in content_lower:
                # Простая подсветка - заменяем слово в preview
                content_preview_text = content_preview_text.replace(
                    self.current_search_word, 
                    f'<span style="background-color: #FFD700; font-weight: bold;">{self.current_search_word}</span>'
                )
        
        content_preview = QLabel()
        content_preview.setTextFormat(Qt.RichText)
        content_preview.setText(content_preview_text)
        content_preview.setWordWrap(True)
        content_preview.setStyleSheet('color: #7f8c8d; padding: 5px 0;')
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        view_btn = QPushButton("👁️ Просмотр")
        view_btn.clicked.connect(lambda checked, n=note, u=is_user_note: self.open_note(n, u))
        view_btn.setStyleSheet('padding: 5px;')
        
        if is_user_note:
            edit_btn = QPushButton("✏️ Редактировать")
            edit_btn.clicked.connect(lambda checked, n=note: self.edit_user_note(n))
            edit_btn.setStyleSheet('padding: 5px; background-color: #f39c12; color: white;')
            
            delete_btn = QPushButton("🗑️ Удалить")
            delete_btn.clicked.connect(lambda checked, nid=note[0]: self.delete_user_note(nid))
            delete_btn.setStyleSheet('padding: 5px; background-color: #e74c3c; color: white;')
            
            buttons_layout.addWidget(view_btn)
            buttons_layout.addWidget(edit_btn)
            buttons_layout.addWidget(delete_btn)
        else:
            save_copy_btn = QPushButton("💾 Сохранить копию")
            save_copy_btn.clicked.connect(lambda checked, n=note: self.save_as_user_note(n))
            save_copy_btn.setStyleSheet('padding: 5px; background-color: #2ecc71; color: white;')
            
            buttons_layout.addWidget(view_btn)
            buttons_layout.addWidget(save_copy_btn)
        
        # Собираем карточку
        card_layout.addWidget(title_label)
        card_layout.addWidget(subject_widget)
        card_layout.addWidget(content_preview)
        card_layout.addLayout(buttons_layout)
        
        return card
    
    def open_note(self, note, is_user_note=False):
        """Открывает конспект для просмотра с подсветкой поиска"""
        if is_user_note:
            note_data = {
                'title': note[2],
                'subject': note[1],
                'content': note[3],
                'images': json.loads(note[4]) if note[4] else []
            }
        else:
            note_data = {
                'title': note[2],
                'subject': note[7],
                'content': note[3],
                'images': []
            }
        
        # Передаем слово поиска в NoteViewer для подсветки
        viewer = NoteViewer(note_data, search_word=self.current_search_word)
        viewer.exec_()
    
    def on_search_advanced(self):
        """Обработка расширенного поиска с сохранением слова"""
        keyword = self.search_input.text().strip()
        
        if keyword:
            self.current_search_word = keyword
            self.current_subject_filter = None  # Сбрасываем фильтр предмета
            self.current_notes = self.db.search_notes(keyword)
            self.show_notes_list(f"результаты поиска: '{keyword}'")
    
    def create_user_note(self):
        """Создание нового конспекта"""
        editor = NoteEditor(self)
        if editor.exec_():
            note_data = editor.get_note_data()
            
            # Сохраняем в базу данных
            self.db.add_user_note(
                note_data['subject'],
                note_data['title'],
                note_data['content'],
                note_data['images']
            )
            
            self.statusBar().showMessage("Конспект сохранен!", 3000)
            self.show_user_notes()
    
    def edit_user_note(self, note):
        """Редактирование пользовательского конспекта"""
        note_data = {
            'subject': note[1],
            'title': note[2],
            'content': note[3],
            'images': json.loads(note[4]) if note[4] else []
        }
        
        editor = NoteEditor(self, note_data, mode='edit')
        if editor.exec_():
            updated_data = editor.get_note_data()
            
            # Обновляем в базе данных
            self.db.update_user_note(
                note[0],
                updated_data['subject'],
                updated_data['title'],
                updated_data['content'],
                updated_data['images']
            )
            
            self.statusBar().showMessage("Конспект обновлен!", 3000)
            self.show_user_notes()
    
    def save_as_user_note(self, note):
        """Сохраняет готовый конспект как пользовательский"""
        note_data = {
            'subject': note[7],  # subject_name
            'title': f"Копия: {note[2]}",
            'content': note[3],
            'images': []
        }
        
        self.db.add_user_note(
            note_data['subject'],
            note_data['title'],
            note_data['content'],
            note_data['images']
        )
        
        self.statusBar().showMessage("Конспект скопирован в 'Мои конспекты'!", 3000)
        self.show_user_notes()
    
    def delete_user_note(self, note_id):
        """Удаляет пользовательский конспект"""
        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            'Вы уверены, что хотите удалить этот конспект?\nЭто действие нельзя отменить.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_user_note(note_id)
            self.statusBar().showMessage("Конспект удален", 3000)
            self.show_user_notes()
    
    def import_note(self):
        """Импорт конспекта из файла"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Текстовые файлы (*.txt *.md);;Все файлы (*)")
        
        if file_dialog.exec_():
            filename = file_dialog.selectedFiles()[0]
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Предлагаем пользователю отредактировать
                editor = NoteEditor(self)
                editor.title_edit.setText(os.path.basename(filename).replace('.txt', '').replace('.md', ''))
                editor.content_edit.setPlainText(content)
                
                if editor.exec_():
                    note_data = editor.get_note_data()
                    self.db.add_user_note(
                        note_data['subject'],
                        note_data['title'],
                        note_data['content'],
                        note_data['images']
                    )
                    
                    self.statusBar().showMessage("Конспект импортирован!", 3000)
                    self.show_user_notes()
                    
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def export_all_notes(self):
        """Экспорт всех пользовательских конспектов"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для экспорта")
        
        if folder:
            notes = self.db.get_user_notes()
            export_count = 0
            
            for note in notes:
                note_id, subject, title, content, images, grade, created_at = note
                
                # Создаем безопасное имя файла
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = os.path.join(folder, f"{safe_title}.txt")
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Конспект: {title}\n")
                        f.write(f"Предмет: {subject}\n")
                        f.write(f"Дата создания: {created_at}\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(content)
                    
                    export_count += 1
                except Exception as e:
                    print(f"Ошибка экспорта {title}: {e}")
            
            QMessageBox.information(
                self,
                "Экспорт завершен",
                f"Экспортировано конспектов: {export_count} из {len(notes)}\n\nПапка: {folder}"
            )
    
    def refresh_view(self):
        """Обновление текущего вида"""
        current_widget = self.main_area.currentWidget()
        if current_widget:
            # Определяем, какой вид активен и обновляем его
            if "Мои конспекты" in current_widget.layout().itemAt(0).widget().text():
                self.show_user_notes()
            elif "Все конспекты" in current_widget.layout().itemAt(0).widget().text():
                self.show_all_notes()
            else:
                # Проверяем, не список ли это конспектов по предмету
                for subject_btn in self.subject_buttons:
                    if subject_btn.property('subject_id'):
                        # Это немного упрощенно, но показывает идею
                        self.show_all_notes()
                        break
    
    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """
        <h2>Школьные конспекты - 1 класс</h2>
        <p>Версия 1.2
        Добавлены: фильтр по предметам и расширенный поиск с подсветкой</p>
        <p>исправлены ошибки и добавлена возможность загружать фотографии</p>
        <p>Приложение для создания и хранения конспектов<br>
        по школьной программе первого класса РФ.</p>
        <hr>
        <p><b>Новые функции:</b></p>
        <ul>
        <li>Фильтр по предметам в разделе "Все конспекты"</li>
        <li>Расширенный поиск с подсветкой найденных слов</li>
        <li>Готовые конспекты по всем предметам</li>
        <li>Создание своих конспектов</li>
        <li>Добавление изображений и схем</li>
        <li>Импорт и экспорт конспектов</li>
        </ul>
        <hr>
        <p>© 2024 Школьные конспекты</p>
        """
        
        QMessageBox.about(self, "О программе", about_text)
    
    def show_help(self):
        """Показывает справку"""
        help_text = """
        <h2>Справка по использованию</h2>
        
        <h3>📚 Просмотр конспектов:</h3>
        <ul>
        <li>Выберите предмет в левой панели</li>
        <li>Или нажмите "Все конспекты" для полного списка</li>
        <li>Используйте поиск для быстрого нахождения</li>
        <li>В разделе "Все конспекты" используйте фильтр по предмету</li>
        </ul>
        
        <h3>🔍 Расширенный поиск:</h3>
        <ul>
        <li>Введите слово в поле поиска и нажмите Enter или кнопку "Найти"</li>
        <li>Найденные слова будут подсвечены желтым цветом</li>
        <li>Для очистки поиска нажмите "Очистить поиск"</li>
        </ul>
        
        <h3>📖 Фильтр по предметам:</h3>
        <ul>
        <li>В разделе "Все конспекты" выберите предмет из выпадающего списка</li>
        <li>Для сброса фильтра нажмите "Сбросить фильтр"</li>
        </ul>
        
        <h3>✏️ Создание конспектов:</h3>
        <ul>
        <li>Нажмите "Создать конспект" в левой панели</li>
        <li>Выберите предмет и введите заголовок</li>
        <li>Добавьте текст и изображения</li>
        <li>Используйте шаблоны для быстрого старта</li>
        </ul>
        
        <h3>💼 Мои конспекты:</h3>
        <ul>
        <li>Все созданные вами конспекты хранятся здесь</li>
        <li>Вы можете редактировать и удалять их</li>
        <li>Готовые конспекты можно скопировать к себе</li>
        </ul>
        
        <h3>📁 Импорт/Экспорт:</h3>
        <ul>
        <li>Импортируйте текстовые файлы (.txt, .md)</li>
        <li>Экспортируйте конспекты для печати или обмена</li>
        </ul>
        
        <hr>
        <p><b>Горячие клавиши:</b></p>
        <ul>
        <li>Ctrl+F - Поиск</li>
        <li>F5 - Обновить вид</li>
        </ul>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Справка")
        dialog.setGeometry(200, 200, 500, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(text_edit)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.close()
            event.accept()
        else:
            event.ignore()


# ============================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================
def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль
    app.setStyle('Fusion')
    
    # Создаем палитру для темной темы (опционально)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    # app.setPalette(palette)  # Раскомментируйте для темной темы
    
    # Устанавливаем иконку приложения
    app.setWindowIcon(QIcon.fromTheme("document-edit"))
    
    # Запускаем главное окно
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    # Проверяем наличие необходимых библиотек
    try:
        main()
    except ImportError as e:
        print(f"Ошибка: Не удалось импортировать модуль: {e}")
        print("\nУстановите необходимые библиотеки:")
        print("pip install PyQt5 Pillow")
        input("\nНажмите Enter для выхода...")