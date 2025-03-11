from DrissionPage import Chromium, ChromiumOptions
from PyPDF2 import PdfMerger
import pdfkit
import time
import os

cource_url = 'https://stepik.org/lesson/556253/step/1?unit=550261' # Ссылка на курс
video_url_list = [] # Список ссылок на видео

with open('styles/stepic.css', 'r', encoding='UTF-8') as file: # Открываем файл со стилями
    style_css = file.read() # Читаем файл

begin_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"> 
    <style>
        {style_css}
    </style>
</head>
<body>""" # Начало html кода

end_html = '</body></html>' # Конец html кода

config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf') # Путь к wkhtmltopdf

os.makedirs('content_files', exist_ok=True) # Создаем папку для файлов

co = ChromiumOptions() # Создаем объект опций
co.use_system_user_path(True) # Используем папку пользователя системы


browser = Chromium(addr_or_opts=co) # Создаем объект браузера
page = browser.latest_tab # Получаем активную вкладку


page.get(cource_url) # Переходим на страницу
time.sleep(10)  # Ждем загрузки страницы
sidebar = page.ele('tag:div@@class:lesson-sidebar__content') # Получаем боковую панель

last_count_links = len(sidebar.eles('tag:a'))   # Получаем количество ссылок
while True: # Прокручиваем страницу пока не закончатся ссылки
    sidebar.scroll.down(300) # Прокручиваем страницу вниз
    time.sleep(2)    # Ждем загрузки страницы
    new_count_links = len(sidebar.eles('tag:a')) # Получаем количество ссылок
    if new_count_links == last_count_links: # Если количество ссылок не изменилось, то прекращаем прокрутку
        nav_links = sidebar.eles('tag:a') # Получаем все ссылки
        break # Прекращаем прокрутку
    last_count_links = new_count_links  # Обновляем количество ссылок


nav_links = [link.attr('href') for link in nav_links if link.attr('href')] # Получаем все ссылки
chapter_count = 1
for nav_link in nav_links: # Перебираем все ссылки
    page.get(nav_link) # Переходим на страницу
    time.sleep(5) # Ждем загрузки страницы
    step_bar = page.ele('tag:div@@class:player-topbar__step-pins') # Получаем шаги
    step_links = [link.attr('href') for link in step_bar.eles('tag:a') if 'null_icon' in link.html] # Получаем ссылки
    if step_links: # Если есть ссылки
        count = 1   # Счетчик шагов
        for link in step_links: # Перебираем все ссылки
            page.get(link) # Переходим на страницу
            time.sleep(10) # Ждем загрузки страницы
            step_name = page.ele('tag:div@@class:top-tools__lesson-name').text # Получаем название шага
            page.scroll.to_see('tag:button@@class:lesson__next-btn') # Прокручиваем страницу до кнопки
            step_content = page.ele('tag:div@@class:player-content-wrapper').html # Получаем содержимое шага

            full_html = begin_html + step_content + end_html # Создаем полный html код

            html_path = f'content_files/temp.html' # Путь к временному файлу
            with open(html_path, 'w', encoding='utf-8') as f: # Создаем временный файл
                f.write(full_html)

            pdf_path = f'content_files/{chapter_count}.{count}. {step_name}.pdf' # Путь к pdf файлу 
            pdfkit.from_file(html_path, pdf_path, options={"enable-local-file-access": ""}, configuration=config)

            if os.path.exists(html_path):  # Проверяем, существует ли временный файл
                os.remove(html_path)  # Удаляем временный файл
            time.sleep(5)
            count += 1 # Увеличиваем счетчик шагов
    chapter_count += 1 # Увеличиваем счетчик глав

print('\nPDF файлы успешно созданы')

pdf_files = os.listdir('content_files') # Получаем все файлы
pdf_files.sort(key=lambda x: int(x.split()[0].replace('.', ''))) # Сортируем файлы

merger = PdfMerger() # Создаем объект объединения pdf файлов

for pdf in pdf_files: # Перебираем все файлы
    with open(f'content_files/{pdf}', "rb") as f: # Открываем файл
        merger.append(f) # Добавляем файл

with open("Конспект курса.pdf", "wb") as output_file: # Создаем конечный файл
    merger.write(output_file) # Записываем файл

merger.close() # Закрываем объект объединения файлов

print('\nКонспект курса.pdf успешно создан')

    
 


