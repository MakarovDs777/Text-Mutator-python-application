import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import random
from datetime import datetime  
from pathlib import Path
from collections import Counter

# Глобальные переменные
file1_words = []
file2_words = []
current_file1_path = ""
current_file2_path = ""
current_text_for_analysis = ""

def setup_clipboard_bindings(widget):
    """Настроить привязки для копирования/вставки/вырезания и SelectAll."""
    def gen(event_name):
        return lambda e: (widget.event_generate(event_name), "break")
    # Windows/Linux: Ctrl
    widget.bind("<Control-c>", gen("<<Copy>>"))
    widget.bind("<Control-v>", gen("<<Paste>>"))
    widget.bind("<Control-x>", gen("<<Cut>>"))
    widget.bind("<Control-a>", lambda e: (widget.tag_add("sel", "1.0", "end"), "break"))
    # macOS: Command
    widget.bind("<Command-c>", gen("<<Copy>>"))
    widget.bind("<Command-v>", gen("<<Paste>>"))
    widget.bind("<Command-x>", gen("<<Cut>>"))
    widget.bind("<Command-a>", lambda e: (widget.tag_add("sel", "1.0", "end"), "break"))
    # При клике — ставим фокус в виджет
    widget.bind("<Button-1>", lambda e: widget.focus_set())
    # Контекстное меню (правый клик)
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Копировать", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_command(label="Вырезать", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_separator()
    menu.add_command(label="Выделить всё", command=lambda: widget.tag_add("sel", "1.0", "end"))
    def show_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    widget.bind("<Button-3>", show_menu)
    widget.bind("<Control-Button-1>", show_menu) # для macOS

def load_file(file_num):
    """Загружает текстовый файл и извлекает из него слова."""
    global file1_words, file2_words, current_file1_path, current_file2_path, current_text_for_analysis
    path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt;*.md;*.py;*.js;*.html;*.css"), ("All files", "*.*")]
    )
    if not path:
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            current_text_for_analysis = text  # Сохраняем текст для анализа
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
        return
    
    # Извлекаем слова (разделяем по пробелам и знакам препинания)
    words = []
    for word in text.split():
        # Очищаем слово от знаков препинания в начале и конце
        clean_word = word.strip('.,!?;:"\'()[]{}<>')
        if clean_word: # добавляем только непустые слова
            words.append(clean_word)
    
    if file_num == 1:
        file1_words = words
        current_file1_path = path
        file1_label.config(text=f"Файл 1: {os.path.basename(path)} ({len(words)} слов)")
        text_widget1.delete("1.0", tk.END)
        text_widget1.insert("1.0", f"Загружено {len(words)} слов из файла:\n{path}\n\nПервые 50 слов:\n{' '.join(words[:50])}")
        if len(words) > 50:
            text_widget1.insert(tk.END, f"\n... и еще {len(words)-50} слов")
    else:
        file2_words = words
        current_file2_path = path
        file2_label.config(text=f"Файл 2: {os.path.basename(path)} ({len(words)} слов)")
        text_widget2.delete("1.0", tk.END)
        text_widget2.insert("1.0", f"Загружено {len(words)} слов из файла:\n{path}\n\nПервые 50 слов:\n{' '.join(words[:50])}")
        if len(words) > 50:
            text_widget2.insert(tk.END, f"\n... и еще {len(words)-50} слов")
    
    # Обновляем статистику символов
    update_symbol_statistics()

def analyze_text():
    """Анализирует текст из поля ввода и обновляет статистику."""
    global current_text_for_analysis
    text = text_input.get("1.0", tk.END).strip()
    if text:
        current_text_for_analysis = text
        update_symbol_statistics()
        messagebox.showinfo("Успех", "Текст проанализирован. Перейдите на вкладку 'Статистика символов'.")
    else:
        messagebox.showwarning("Внимание", "Введите текст для анализа.")

def update_symbol_statistics():
    """Обновляет статистику символов на основе текущего текста."""
    if not current_text_for_analysis:
        # Если текста нет, показываем сообщение
        for widget in stats_frame.winfo_children():
            widget.destroy()
        tk.Label(stats_frame, text="Нет текста для анализа", font=("Arial", 12, "bold")).pack(pady=20)
        return
    
    # Очищаем предыдущие данные
    for widget in stats_frame.winfo_children():
        widget.destroy()
    
    # Создаем основной контейнер с прокруткой
    main_container = tk.Frame(stats_frame)
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Создаем Canvas для прокрутки
    canvas = tk.Canvas(main_container)
    scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Размещаем canvas и scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Заголовок
    tk.Label(scrollable_frame, text="ПОЛНАЯ СТАТИСТИКА СИМВОЛОВ", 
             font=("Arial", 14, "bold"), fg="darkblue").pack(pady=(10, 20))
    
    # Общая информация
    total_chars = len(current_text_for_analysis)
    unique_chars = len(set(current_text_for_analysis))
    
    info_frame = tk.Frame(scrollable_frame)
    info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    tk.Label(info_frame, text=f"📊 ОБЩАЯ ИНФОРМАЦИЯ:", 
             font=("Arial", 12, "bold")).pack(anchor="w")
    tk.Label(info_frame, text=f"• Всего символов в тексте: {total_chars:,}", 
             font=("Arial", 10)).pack(anchor="w", padx=20)
    tk.Label(info_frame, text=f"• Уникальных символов: {unique_chars}", 
             font=("Arial", 10)).pack(anchor="w", padx=20)
    
    # Разделитель
    tk.Frame(scrollable_frame, height=2, bg="gray").pack(fill=tk.X, padx=20, pady=10)
    
    # Раздел 1: ПОСИМВОЛЬНАЯ СТАТИСТИКА
    tk.Label(scrollable_frame, text="🔤 ПОСИМВОЛЬНАЯ СТАТИСТИКА", 
             font=("Arial", 12, "bold"), fg="darkgreen").pack(anchor="w", padx=20, pady=(10, 5))
    
    # Создаем таблицу для посимвольной статистики
    table_frame = tk.Frame(scrollable_frame)
    table_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # Заголовки таблицы
    headers = ["№", "Символ", "Код Unicode", "Количество", "Процент", "Частота на 1000"]
    for col, header in enumerate(headers):
        tk.Label(table_frame, text=header, font=("Arial", 10, "bold"), 
                 borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="nsew")
    
    # Подсчитываем все символы
    char_counts = {}
    for char in current_text_for_analysis:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    # Сортируем символы по частоте (по убыванию)
    sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Заполняем таблицу
    for row, (char, count) in enumerate(sorted_chars, 1):
        # Отображаем символ
        if char == '\n':
            char_display = "\\n (перенос строки)"
        elif char == '\t':
            char_display = "\\t (табуляция)"
        elif char == ' ':
            char_display = "␣ (пробел)"
        elif char == '\r':
            char_display = "\\r (возврат каретки)"
        elif char == '\x0b':  # вертикальная табуляция
            char_display = "\\v (верт. табуляция)"
        elif char == '\x0c':  # разрыв страницы
            char_display = "\\f (разрыв страницы)"
        elif ord(char) < 32:  # другие управляющие символы
            char_display = f"\\x{ord(char):02x} (управляющий)"
        else:
            char_display = char
        
        # Код Unicode
        unicode_code = f"U+{ord(char):04X}"
        
        # Процент от общего количества
        percentage = (count / total_chars) * 100
        
        # Частота на 1000 символов
        frequency_per_1000 = (count / total_chars) * 1000
        
        # Создаем ячейки
        tk.Label(table_frame, text=str(row), borderwidth=1, relief="solid", 
                 padx=5, pady=2).grid(row=row, column=0, sticky="nsew")
        tk.Label(table_frame, text=char_display, borderwidth=1, relief="solid", 
                 padx=5, pady=2).grid(row=row, column=1, sticky="nsew")
        tk.Label(table_frame, text=unicode_code, borderwidth=1, relief="solid", 
                 padx=5, pady=2).grid(row=row, column=2, sticky="nsew")
        tk.Label(table_frame, text=str(count), borderwidth=1, relief="solid", 
                 padx=5, pady=2).grid(row=row, column=3, sticky="nsew")
        tk.Label(table_frame, text=f"{percentage:.4f}%", borderwidth=1, relief="solid", 
                 padx=5, pady=2).grid(row=row, column=4, sticky="nsew")
        tk.Label(table_frame, text=f"{frequency_per_1000:.2f}", borderwidth=1, relief="solid", 
                 padx=5, pady=2).grid(row=row, column=5, sticky="nsew")
    
    # Настраиваем веса колонок
    for col in range(6):
        table_frame.grid_columnconfigure(col, weight=1)
    
    # Разделитель
    tk.Frame(scrollable_frame, height=2, bg="gray").pack(fill=tk.X, padx=20, pady=20)
    
    # Раздел 2: КАТЕГОРИИ СИМВОЛОВ
    tk.Label(scrollable_frame, text="📈 КАТЕГОРИИ СИМВОЛОВ", 
             font=("Arial", 12, "bold"), fg="darkred").pack(anchor="w", padx=20, pady=(10, 5))
    
    # Анализируем категории символов
    categories = {
        "Буквы (латиница)": lambda c: c.isalpha() and ('a' <= c.lower() <= 'z'),
        "Буквы (кириллица)": lambda c: c.isalpha() and ('а' <= c.lower() <= 'я'),
        "Цифры": lambda c: c.isdigit(),
        "Пробелы": lambda c: c == ' ',
        "Переносы строк": lambda c: c == '\n',
        "Табуляции": lambda c: c == '\t',
        "Знаки препинания": lambda c: c in '.,!?;:"\'()[]{}<>-—–…',
        "Специальные символы": lambda c: not (c.isalpha() or c.isdigit() or c.isspace() or c in '.,!?;:"\'()[]{}<>-—–…')
    }
    
    category_frame = tk.Frame(scrollable_frame)
    category_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # Заголовки для категорий
    cat_headers = ["Категория", "Количество", "Процент"]
    for col, header in enumerate(cat_headers):
        tk.Label(category_frame, text=header, font=("Arial", 10, "bold"), 
                 borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="nsew")
    
    # Подсчитываем категории
    row_num = 1
    for category_name, check_func in categories.items():
        count = sum(1 for char in current_text_for_analysis if check_func(char))
        if count > 0:
            percentage = (count / total_chars) * 100
            tk.Label(category_frame, text=category_name, borderwidth=1, relief="solid", 
                     padx=5, pady=2).grid(row=row_num, column=0, sticky="nsew")
            tk.Label(category_frame, text=str(count), borderwidth=1, relief="solid", 
                     padx=5, pady=2).grid(row=row_num, column=1, sticky="nsew")
            tk.Label(category_frame, text=f"{percentage:.2f}%", borderwidth=1, relief="solid", 
                     padx=5, pady=2).grid(row=row_num, column=2, sticky="nsew")
            row_num += 1
    
    # Настраиваем веса колонок для категорий
    for col in range(3):
        category_frame.grid_columnconfigure(col, weight=1)
    
    # Разделитель
    tk.Frame(scrollable_frame, height=2, bg="gray").pack(fill=tk.X, padx=20, pady=20)
    
    # Раздел 3: ТОП-10 САМЫХ ЧАСТЫХ СИМВОЛОВ
    tk.Label(scrollable_frame, text="🏆 ТОП-10 САМЫХ ЧАСТЫХ СИМВОЛОВ", 
             font=("Arial", 12, "bold"), fg="purple").pack(anchor="w", padx=20, pady=(10, 5))
    
    top_frame = tk.Frame(scrollable_frame)
    top_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # Отображаем топ-10 символов
    for i, (char, count) in enumerate(sorted_chars[:10], 1):
        percentage = (count / total_chars) * 100
        char_display = char
        if char == '\n':
            char_display = "\\n"
        elif char == '\t':
            char_display = "\\t"
        elif char == ' ':
            char_display = "␣"
        
        tk.Label(top_frame, text=f"{i}. '{char_display}'", font=("Arial", 10)).pack(anchor="w")
        tk.Label(top_frame, text=f"   Количество: {count:,} ({percentage:.2f}%)", 
                 font=("Arial", 9), fg="gray").pack(anchor="w", padx=20)
    
    # Разделитель
    tk.Frame(scrollable_frame, height=2, bg="gray").pack(fill=tk.X, padx=20, pady=20)
    
    # Раздел 4: РЕДКИЕ СИМВОЛЫ (встречаются 1 раз)
    rare_chars = [(char, count) for char, count in sorted_chars if count == 1]
    if rare_chars:
        tk.Label(scrollable_frame, text="🔍 РЕДКИЕ СИМВОЛЫ (встречаются 1 раз)", 
                 font=("Arial", 12, "bold"), fg="orange").pack(anchor="w", padx=20, pady=(10, 5))
        
        # Исправленная строка - убрана f-строка с обратной косой чертой
        rare_items = []
        for char, _ in rare_chars[:20]:
            if char == '\n':
                display = "'\\n' (U+000A)"
            elif char == '\t':
                display = "'\\t' (U+0009)"
            elif char == ' ':
                display = "'␣' (U+0020)"
            elif ord(char) < 32:
                display = f"'\\x{ord(char):02x}' (U+{ord(char):04X})"
            else:
                display = f"'{char}' (U+{ord(char):04X})"
            rare_items.append(display)
        
        rare_text = ", ".join(rare_items)
        
        rare_label = tk.Label(scrollable_frame, text=rare_text, wraplength=1000, 
                              justify="left", font=("Arial", 9))
        rare_label.pack(anchor="w", padx=20, pady=5)
        
        if len(rare_chars) > 20:
            tk.Label(scrollable_frame, text=f"... и еще {len(rare_chars) - 20} редких символов", 
                     font=("Arial", 9), fg="gray").pack(anchor="w", padx=20)
    
    # Кнопка для копирования статистики
    def copy_statistics():
        """Копирует статистику в буфер обмена."""
        stats_text = f"СТАТИСТИКА СИМВОЛОВ\n"
        stats_text += f"Всего символов: {total_chars}\n"
        stats_text += f"Уникальных символов: {unique_chars}\n\n"
        stats_text += "ПОСИМВОЛЬНАЯ СТАТИСТИКА:\n"
        stats_text += "№\tСимвол\tUnicode\tКоличество\tПроцент\tЧастота/1000\n"
        for i, (char, count) in enumerate(sorted_chars, 1):
            char_display = char
            if char == '\n':
                char_display = "\\n"
            elif char == '\t':
                char_display = "\\t"
            elif char == ' ':
                char_display = "␣"
            percentage = (count / total_chars) * 100
            frequency_per_1000 = (count / total_chars) * 1000
            stats_text += f"{i}\t{char_display}\tU+{ord(char):04X}\t{count}\t{percentage:.4f}%\t{frequency_per_1000:.2f}\n"
        root.clipboard_clear()
        root.clipboard_append(stats_text)
        messagebox.showinfo("Успех", "Статистика скопирована в буфер обмена!")

    def save_statistics_to_file():
        """Сохраняет статистику в текстовый файл."""
        if not current_text_for_analysis:
            messagebox.showwarning("Внимание", "Нет данных для сохранения.")
            return
        
        # Предлагаем выбрать место для сохранения
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"symbol_statistics_{len(current_text_for_analysis)}_chars.txt"
        )
        
        if not file_path:
            return  # Пользователь отменил сохранение
        
        try:
            # Формируем полную статистику
            stats_text = "=" * 60 + "\n"
            stats_text += "СТАТИСТИКА СИМВОЛОВ\n"
            stats_text += "=" * 60 + "\n\n"
            
            # Общая информация
            stats_text += f"📊 ОБЩАЯ ИНФОРМАЦИЯ:\n"
            stats_text += f"• Всего символов в тексте: {total_chars:,}\n"
            stats_text += f"• Уникальных символов: {unique_chars}\n"
            stats_text += f"• Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Посимвольная статистика
            stats_text += "🔤 ПОСИМВОЛЬНАЯ СТАТИСТИКА:\n"
            stats_text += "-" * 80 + "\n"
            stats_text += "№\tСимвол\t\tUnicode\t\tКоличество\tПроцент\t\tЧастота/1000\n"
            stats_text += "-" * 80 + "\n"
            
            for i, (char, count) in enumerate(sorted_chars, 1):
                # Отображаем символ
                if char == '\n':
                    char_display = "\\n (перенос строки)"
                elif char == '\t':
                    char_display = "\\t (табуляция)"
                elif char == ' ':
                    char_display = "␣ (пробел)"
                elif ord(char) < 32:
                    char_display = f"\\x{ord(char):02x} (управляющий)"
                else:
                    char_display = char
                
                percentage = (count / total_chars) * 100
                frequency_per_1000 = (count / total_chars) * 1000
                
                stats_text += f"{i}\t{char_display:<15}\tU+{ord(char):04X}\t{count:>10,}\t{percentage:>10.4f}%\t{frequency_per_1000:>10.2f}\n"
            
            stats_text += "\n" + "=" * 60 + "\n"
            stats_text += "📈 КАТЕГОРИИ СИМВОЛОВ:\n"
            stats_text += "-" * 60 + "\n"
            
            # Категории символов (используем те же категории, что и в GUI)
            categories = {
                "Буквы (латиница)": lambda c: c.isalpha() and ('a' <= c.lower() <= 'z'),
                "Буквы (кириллица)": lambda c: c.isalpha() and ('а' <= c.lower() <= 'я'),
                "Цифры": lambda c: c.isdigit(),
                "Пробелы": lambda c: c == ' ',
                "Переносы строк": lambda c: c == '\n',
                "Табуляции": lambda c: c == '\t',
                "Знаки препинания": lambda c: c in '.,!?;:"\'()[]{}<>-—–…',
                "Специальные символы": lambda c: not (c.isalpha() or c.isdigit() or c.isspace() or c in '.,!?;:"\'()[]{}<>-—–…')
            }
            
            for category_name, check_func in categories.items():
                count = sum(1 for char in current_text_for_analysis if check_func(char))
                if count > 0:
                    percentage = (count / total_chars) * 100
                    stats_text += f"• {category_name:<25}: {count:>8,} ({percentage:>6.2f}%)\n"
            
            stats_text += "\n" + "=" * 60 + "\n"
            stats_text += "🏆 ТОП-10 САМЫХ ЧАСТЫХ СИМВОЛОВ:\n"
            stats_text += "-" * 60 + "\n"
            
            for i, (char, count) in enumerate(sorted_chars[:10], 1):
                percentage = (count / total_chars) * 100
                char_display = char
                if char == '\n':
                    char_display = "\\n"
                elif char == '\t':
                    char_display = "\\t"
                elif char == ' ':
                    char_display = "␣"
                
                stats_text += f"{i:>2}. '{char_display}' - {count:>8,} раз ({percentage:>6.2f}%)\n"
            
            # Редкие символы
            rare_chars = [(char, count) for char, count in sorted_chars if count == 1]
            if rare_chars:
                stats_text += "\n" + "=" * 60 + "\n"
                stats_text += f"🔍 РЕДКИЕ СИМВОЛЫ (встречаются 1 раз, всего {len(rare_chars)}):\n"
                stats_text += "-" * 60 + "\n"
                
                for i, (char, _) in enumerate(rare_chars[:50], 1):
                    if char == '\n':
                        display = "'\\n' (U+000A)"
                    elif char == '\t':
                        display = "'\\t' (U+0009)"
                    elif char == ' ':
                        display = "'␣' (U+0020)"
                    elif ord(char) < 32:
                        display = f"'\\x{ord(char):02x}' (U+{ord(char):04X})"
                    else:
                        display = f"'{char}' (U+{ord(char):04X})"
                    
                    stats_text += f"{display}, "
                    if i % 5 == 0:
                        stats_text += "\n"
                
                if len(rare_chars) > 50:
                    stats_text += f"\n... и еще {len(rare_chars) - 50} редких символов"
            
            # Сохраняем в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(stats_text)
            
            messagebox.showinfo("Успех", f"Статистика сохранена в файл:\n{os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    # Фрейм для кнопок
    buttons_frame = tk.Frame(scrollable_frame)
    buttons_frame.pack(pady=20)
    
    # Кнопка копирования
    copy_btn = tk.Button(buttons_frame, text="📋 Копировать статистику",
                         command=copy_statistics, bg="lightblue", width=20)
    copy_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Кнопка сохранения в файл
    save_btn = tk.Button(buttons_frame, text="📥 Скачать статистику",
                         command=save_statistics_to_file, bg="lightgreen", width=20)
    save_btn.pack(side=tk.LEFT)

def mix_words(percentage1, percentage2):
    """Смешивает слова из двух файлов в указанном процентном соотношении."""
    global current_text_for_analysis
    if not file1_words:
        messagebox.showerror("Ошибка", "Сначала загрузите файл 1")
        return
    if not file2_words:
        messagebox.showerror("Ошибка", "Сначала загрузите файл 2")
        return
    
    # Определяем количество слов для каждого файла
    total_words = len(file1_words) + len(file2_words)
    words_from_file1 = int((percentage1 / 100) * total_words)
    words_from_file2 = int((percentage2 / 100) * total_words)
    
    # Если сумма не равна total_words, корректируем
    if words_from_file1 + words_from_file2 != total_words:
        words_from_file2 = total_words - words_from_file1
    
    # Выбираем случайные слова из каждого файла
    selected_words1 = random.sample(file1_words, min(words_from_file1, len(file1_words)))
    selected_words2 = random.sample(file2_words, min(words_from_file2, len(file2_words)))
    
    # Если нужно больше слов, чем есть в файле, добавляем повторения
    if words_from_file1 > len(file1_words):
        additional = words_from_file1 - len(file1_words)
        selected_words1.extend(random.choices(file1_words, k=additional))
    if words_from_file2 > len(file2_words):
        additional = words_from_file2 - len(file2_words)
        selected_words2.extend(random.choices(file2_words, k=additional))
    
    # Смешиваем слова
    all_words = selected_words1 + selected_words2
    random.shuffle(all_words)
    
    # Обновляем текущий текст для анализа
    current_text_for_analysis = ' '.join(all_words)
    
    # Отображаем результат
    result_text.delete("1.0", tk.END)
    result_text.insert("1.0", f"Смешанный текст ({len(all_words)} слов):\n")
    result_text.insert(tk.END, f"Файл 1: {percentage1}% ({len(selected_words1)} слов)\n")
    result_text.insert(tk.END, f"Файл 2: {percentage2}% ({len(selected_words2)} слов)\n\n")
    
    # Отображаем слова группами по 10 для удобства чтения
    for i in range(0, len(all_words), 10):
        chunk = all_words[i:i+10]
        result_text.insert(tk.END, ' '.join(chunk) + '\n')
    
    # Сохраняем результат в файл на рабочем столе
    save_to_file(all_words, percentage1, percentage2)
    
    # Обновляем статистику символов
    update_symbol_statistics()

def save_to_file(words, percentage1, percentage2):
    """Сохраняет смешанный текст в файл на рабочем столе."""
    desktop_path = Path.home() / "Desktop"
    filename = f"mixed_text_{percentage1}_{percentage2}_{random.randint(1000, 9999)}.txt"
    filepath = desktop_path / filename
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Смешанный текст из двух файлов\n")
            f.write(f"Файл 1: {percentage1}% ({current_file1_path})\n")
            f.write(f"Файл 2: {percentage2}% ({current_file2_path})\n")
            f.write(f"Всего слов: {len(words)}\n")
            f.write("="*50 + "\n\n")
            # Записываем слова группами по 10
            for i in range(0, len(words), 10):
                chunk = words[i:i+10]
                f.write(' '.join(chunk) + '\n')
        messagebox.showinfo("Успех", f"Файл сохранен на рабочем столе:\n{filename}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

def mix_50_50():
    """Смешивает слова в пропорции 50/50."""
    mix_words(50, 50)

def mix_custom():
    """Смешивает слова с пользовательскими процентами."""
    try:
        p1 = int(percentage1_var.get())
        p2 = int(percentage2_var.get())
        if p1 < 0 or p1 > 100 or p2 < 0 or p2 > 100:
            raise ValueError("Проценты должны быть от 0 до 100")
        if p1 + p2 != 100:
            messagebox.showwarning("Внимание",
                f"Сумма процентов ({p1}+{p2}={p1+p2}) не равна 100%. Автоматически скорректирую.")
            p2 = 100 - p1
        mix_words(p1, p2)
    except ValueError as e:
        messagebox.showerror("Ошибка", f"Некорректные значения: {e}")

def clear_all():
    """Очищает все поля."""
    global file1_words, file2_words, current_file1_path, current_file2_path, current_text_for_analysis
    file1_words = []
    file2_words = []
    current_file1_path = ""
    current_file2_path = ""
    current_text_for_analysis = ""
    file1_label.config(text="Файл 1: не загружен")
    file2_label.config(text="Файл 2: не загружен")
    text_widget1.delete("1.0", tk.END)
    text_widget2.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)
    text_input.delete("1.0", tk.END)
    percentage1_var.set("50")
    percentage2_var.set("50")
    
    # Очищаем статистику
    for widget in stats_frame.winfo_children():
        widget.destroy()

# --- GUI ---
root = tk.Tk()
root.title("Текстовый миксер и анализатор символов")
root.geometry("1300x900")

# Создаем панель вкладок
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Вкладка 1: Загрузка файлов
load_frame = ttk.Frame(notebook)
notebook.add(load_frame, text="Загрузка файлов")

# Фрейм для кнопок загрузки
load_buttons_frame = tk.Frame(load_frame)
load_buttons_frame.pack(fill=tk.X, padx=10, pady=10)

load_file1_btn = tk.Button(load_buttons_frame, text="Загрузить файл 1", command=lambda: load_file(1))
load_file1_btn.pack(side=tk.LEFT, padx=(0, 10))

load_file2_btn = tk.Button(load_buttons_frame, text="Загрузить файл 2", command=lambda: load_file(2))
load_file2_btn.pack(side=tk.LEFT)

# Метки для отображения информации о файлах
file1_label = tk.Label(load_frame, text="Файл 1: не загружен", anchor="w")
file1_label.pack(fill=tk.X, padx=10, pady=(0, 5))

file2_label = tk.Label(load_frame, text="Файл 2: не загружен", anchor="w")
file2_label.pack(fill=tk.X, padx=10, pady=(0, 10))

# Фрейм для отображения содержимого файлов
files_content_frame = tk.Frame(load_frame)
files_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Текстовые поля для отображения содержимого файлов
text_frame1 = tk.Frame(files_content_frame)
text_frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

tk.Label(text_frame1, text="Содержимое файла 1:").pack(anchor="w")
text_widget1 = tk.Text(text_frame1, wrap=tk.WORD, font=("Consolas", 10), height=15)
scroll1 = tk.Scrollbar(text_frame1, orient=tk.VERTICAL, command=text_widget1.yview)
text_widget1.configure(yscrollcommand=scroll1.set)
scroll1.pack(side=tk.RIGHT, fill=tk.Y)
text_widget1.pack(fill=tk.BOTH, expand=True)

text_frame2 = tk.Frame(files_content_frame)
text_frame2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

tk.Label(text_frame2, text="Содержимое файла 2:").pack(anchor="w")
text_widget2 = tk.Text(text_frame2, wrap=tk.WORD, font=("Consolas", 10), height=15)
scroll2 = tk.Scrollbar(text_frame2, orient=tk.VERTICAL, command=text_widget2.yview)
text_widget2.configure(yscrollcommand=scroll2.set)
scroll2.pack(side=tk.RIGHT, fill=tk.Y)
text_widget2.pack(fill=tk.BOTH, expand=True)

# Включаем привязки буфера обмена
setup_clipboard_bindings(text_widget1)
setup_clipboard_bindings(text_widget2)

# Вкладка 2: Смешивание
mix_frame = ttk.Frame(notebook)
notebook.add(mix_frame, text="Смешивание")

# Фрейм для управления смешиванием
control_frame = tk.Frame(mix_frame)
control_frame.pack(fill=tk.X, padx=10, pady=10)

# Процентное соотношение
percentage_frame = tk.Frame(control_frame)
percentage_frame.pack(pady=10)

tk.Label(percentage_frame, text="Процентное соотношение:").pack(side=tk.LEFT, padx=(0, 10))
tk.Label(percentage_frame, text="Файл 1:").pack(side=tk.LEFT)

percentage1_var = tk.StringVar(value="50")
percentage1_entry = tk.Entry(percentage_frame, textvariable=percentage1_var, width=5)
percentage1_entry.pack(side=tk.LEFT, padx=(0, 10))

tk.Label(percentage_frame, text="%").pack(side=tk.LEFT, padx=(0, 10))
tk.Label(percentage_frame, text="Файл 2:").pack(side=tk.LEFT)

percentage2_var = tk.StringVar(value="50")
percentage2_entry = tk.Entry(percentage_frame, textvariable=percentage2_var, width=5)
percentage2_entry.pack(side=tk.LEFT, padx=(0, 10))

tk.Label(percentage_frame, text="%").pack(side=tk.LEFT)

# Кнопки смешивания
buttons_frame = tk.Frame(control_frame)
buttons_frame.pack(pady=10)

mix_50_50_btn = tk.Button(buttons_frame, text="Смешать 50/50", command=mix_50_50, bg="lightblue")
mix_50_50_btn.pack(side=tk.LEFT, padx=(0, 10))

mix_custom_btn = tk.Button(buttons_frame, text="Смешать с указанными процентами", command=mix_custom)
mix_custom_btn.pack(side=tk.LEFT, padx=(0, 10))

clear_btn = tk.Button(buttons_frame, text="Очистить всё", command=clear_all, bg="lightcoral")
clear_btn.pack(side=tk.LEFT)

# Текстовое поле для результата
result_frame = tk.Frame(mix_frame)
result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

tk.Label(result_frame, text="Результат смешивания:").pack(anchor="w")
result_text = tk.Text(result_frame, wrap=tk.WORD, font=("Consolas", 10))
result_scroll = tk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_text.yview)
result_text.configure(yscrollcommand=result_scroll.set)
result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
result_text.pack(fill=tk.BOTH, expand=True)

# Включаем привязки буфера обмена для результата
setup_clipboard_bindings(result_text)

# Вкладка 3: Ввод текста для анализа
input_frame = ttk.Frame(notebook)
notebook.add(input_frame, text="Ввод текста")

# Поле для ввода текста
tk.Label(input_frame, text="Введите текст для анализа:", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

text_input = tk.Text(input_frame, wrap=tk.WORD, font=("Consolas", 10), height=15)
text_scroll = tk.Scrollbar(input_frame, orient=tk.VERTICAL, command=text_input.yview)
text_input.configure(yscrollcommand=text_scroll.set)
text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
text_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Кнопка анализа
analyze_btn = tk.Button(input_frame, text="Проанализировать текст", command=analyze_text, bg="lightgreen")
analyze_btn.pack(pady=10)

# Включаем привязки буфера обмена для поля ввода
setup_clipboard_bindings(text_input)

# Вкладка 4: Статистика символов
stats_tab = ttk.Frame(notebook)
notebook.add(stats_tab, text="Статистика символов")

# Фрейм для статистики
stats_frame = tk.Frame(stats_tab)
stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Подсказка внизу
hint = tk.Label(root, text="Загрузите два текстовых файла, затем смешайте их слова в нужной пропорции. Результат автоматически сохраняется на рабочем столе. Или введите текст для анализа символов.",
                anchor="w", wraplength=1200)
hint.pack(fill=tk.X, padx=10, pady=(0, 10))

root.mainloop()

