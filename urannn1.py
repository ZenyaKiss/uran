import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk



# Подключение к базе данных
def connect_db():
    try:
        conn = sqlite3.connect('uranium_mining.db')
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        exit()


conn, cursor = connect_db()


# Универсальная функция для добавления данных
def add_data(table_name, values):
    placeholders = ', '.join(['?'] * len(values))
    cursor.execute(f"INSERT INTO {table_name} VALUES (NULL, {placeholders})", values)
    conn.commit()


# Универсальная функция для обновления данных
def update_data(table_name, values, record_id):
    set_clause = ', '.join([f"{col} = ?" for col in values.keys()])
    query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
    cursor.execute(query, list(values.values()) + [record_id])
    conn.commit()


# Универсальная функция для удаления данных
def delete_data(table_name, record_id):
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
    conn.commit()


# Универсальная функция для открытия окна добавления данных
def open_add_window(table_name, tree, frame):
    # Получаем столбцы таблицы
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns][1:]  # Пропускаем первый столбец ID

    # Создаем окно для добавления данных
    add_window = tk.Toplevel()
    add_window.title(f"Добавить данные в таблицу {table_name.capitalize()}")
    add_window.geometry("300x250")

    entries = {}

    # Создаем метки и поля ввода для каждого столбца (кроме ID)
    for i, col in enumerate(column_names):
        tk.Label(add_window, text=col.capitalize() + ":").grid(row=i, column=0)
        entries[col] = tk.Entry(add_window)
        entries[col].grid(row=i, column=1)

    def add_data_and_refresh():
        values = []
        for col in column_names:
            try:
                values.append(entries[col].get())
            except ValueError:
                messagebox.showerror("Ошибка", f"Пожалуйста, введите корректные данные для {col}.")
                return

        add_data(table_name, values)
        messagebox.showinfo("Успех", "Данные успешно добавлены")
        add_window.destroy()
        show_data(table_name, frame, tree)  # Обновление данных

    tk.Button(add_window, text="Добавить", command=add_data_and_refresh).grid(row=len(column_names), column=0,
                                                                              columnspan=2)


# Функция для отображения данных из таблицы
def show_data(table_name, frame, tree):
    for widget in frame.winfo_children():
        widget.destroy()

    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky="nsew")

    for row in results:
        tree.insert("", "end", values=row)

    window_width = 800
    window_height = len(results) * 25 + 100

    return window_width, window_height, tree


# Функция для открытия нового окна с таблицей
def open_table_window(table_name):
    table_window = tk.Toplevel()
    table_window.title(f"Таблица: {table_name.capitalize()}")

    frame = tk.Frame(table_window)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame)

    window_width, window_height, tree = show_data(table_name, frame, tree)

    buttons_frame = tk.Frame(table_window)
    buttons_frame.pack(pady=10)

    # Кнопки для добавления, редактирования и удаления
    add_button = tk.Button(buttons_frame, text="Добавить", command=lambda: open_add_window(table_name, tree, frame))
    add_button.grid(row=0, column=0, padx=5)

    edit_button = tk.Button(buttons_frame, text="Редактировать",
                            command=lambda: edit_selected_item(table_name, tree, frame))
    edit_button.grid(row=0, column=1, padx=5)

    delete_button = tk.Button(buttons_frame, text="Удалить",
                              command=lambda: delete_selected_item(table_name, tree, frame))
    delete_button.grid(row=0, column=2, padx=5)

    # Устанавливаем размер окна
    table_window.geometry(f"{window_width}x{window_height}")


# Функция для редактирования выбранного элемента
def edit_selected_item(table_name, tree, frame):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Выбор", "Пожалуйста, выберите запись для редактирования.")
        return

    item_values = tree.item(selected_item)["values"]
    record_id = item_values[0]  # Получаем ID записи (первый столбец)

    # Получаем столбцы таблицы
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns][1:]  # Пропускаем первый столбец ID

    # Создаем окно для редактирования данных
    edit_window = tk.Toplevel()
    edit_window.title(f"Редактировать данные в таблице {table_name.capitalize()}")
    edit_window.geometry("300x250")

    entries = {}

    # Создаем метки и поля ввода для каждого столбца (кроме ID)
    for i, col in enumerate(column_names):
        tk.Label(edit_window, text=col.capitalize() + ":").grid(row=i, column=0)
        entries[col] = tk.Entry(edit_window)
        entries[col].grid(row=i, column=1)
        entries[col].insert(0, item_values[i + 1])  # Заполняем полями текущими значениями

    def update_and_refresh():
        values = {col: entries[col].get() for col in column_names}
        update_data(table_name, values, record_id)
        messagebox.showinfo("Успех", "Данные успешно обновлены.")
        edit_window.destroy()
        show_data(table_name, frame, tree)  # Обновление данных

    tk.Button(edit_window, text="Обновить", command=update_and_refresh).grid(row=len(column_names), column=0,
                                                                               columnspan=2)


# Функция для удаления выбранного элемента
def delete_selected_item(table_name, tree, frame):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Выбор", "Пожалуйста, выберите запись для удаления.")
        return

    item_values = tree.item(selected_item)["values"]
    record_id = item_values[0]  # Получаем ID записи (первый столбец)

    confirm = messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить эту запись?")
    if confirm:
        delete_data(table_name, record_id)
        messagebox.showinfo("Удалено", "Запись успешно удалена.")
        show_data(table_name, frame, tree)  # Обновление данных


# Главное окно с кнопками для каждой таблицы
def main_window():
    window = tk.Tk()
    window.title("Система добычи урана")
    window.geometry("300x250")

    # Кнопки для открытия таблиц
    tk.Button(window, text="Месторождения", command=lambda: open_table_window("deposits")).pack(pady=5)
    tk.Button(window, text="Шахты", command=lambda: open_table_window("mines")).pack(pady=5)
    tk.Button(window, text="Персонал", command=lambda: open_table_window("personnel")).pack(pady=5)
    tk.Button(window, text="Оборудование", command=lambda: open_table_window("equipment")).pack(pady=5)

    # Кнопки "Добыча" и "Переработка"
    extraction_button = tk.Button(window, text="Добыча", command=lambda: open_table_window("extraction"),
                                  bg="lightblue")
    extraction_button.pack(pady=5)

    processing_button = tk.Button(window, text="Переработка", command=lambda: open_table_window("processing"),
                                  bg="lightblue")
    processing_button.pack(pady=5)

    def on_closing():
        conn.close()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_closing)

    window.mainloop()

# Запуск приложения
if __name__ == "__main__":
    main_window()