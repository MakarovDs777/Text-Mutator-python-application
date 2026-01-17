import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import random
from pathlib import Path

# Глобальные переменные
file1_words = []
file2_words = []
current_file1_path = ""
current_file2_path = ""

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
    widget.bind("<Control-Button-1>", show_menu)  # для macOS

def load_file(file_num):
    """Загружает текстовый файл и извлекает из него слова."""
    global file1_words, file2_words, current_file1_path, current_file2_path
    
    path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt;*.md;*.py;*.js;*.html;*.css"), ("All files", "*.*")]
    )
    
    if not path:
        return
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
        return
    
    # Извлекаем слова (разделяем по пробелам и знакам препинания)
    words = []
    for word in text.split():
        # Очищаем слово от знаков препинания в начале и конце
        clean_word = word.strip('.,!?;:"\'()[]{}<>')
        if clean_word:  # добавляем только непустые слова
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

def mix_words(percentage1, percentage2):
    """Смешивает слова из двух файлов в указанном процентном соотношении."""
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
    global file1_words, file2_words, current_file1_path, current_file2_path
    file1_words = []
    file2_words = []
    current_file1_path = ""
    current_file2_path = ""
    
    file1_label.config(text="Файл 1: не загружен")
    file2_label.config(text="Файл 2: не загружен")
    text_widget1.delete("1.0", tk.END)
    text_widget2.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)
    percentage1_var.set("50")
    percentage2_var.set("50")

# --- GUI ---
root = tk.Tk()
root.title("Текстовый миксер - смешивание слов")
root.geometry("1200x800")

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

# Подсказка внизу
hint = tk.Label(root, text="Загрузите два текстовых файла, затем смешайте их слова в нужной пропорции. Результат автоматически сохраняется на рабочем столе.", 
                anchor="w", wraplength=1100)
hint.pack(fill=tk.X, padx=10, pady=(0, 10))

root.mainloop()
