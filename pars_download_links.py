from DrissionPage import Chromium, ChromiumOptions
import time
import json

cource_url = 'https://stepik.org/lesson/1107514/step/1?unit=1118755'
video_url_list = []


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
for nav_link in nav_links: # Перебираем все ссылки
    page.get(nav_link) # Переходим на страницу
    time.sleep(10)
    step_bar = page.ele('tag:div@@class:player-topbar__step-pins') # Получаем шаги
    step_links = [link.attr('href') for link in step_bar.eles('tag:a') if 'video-pin_icon' in link.html] # Получаем ссылки на видео
    if step_links:
        for link in step_links:
            page.get(link)
            time.sleep(5)
            video_url = page.ele('tag:video').attr('src')
            name_video = page.ele('tag:div@@class:top-tools__lesson-name').text
            video_url_list.append({'name': name_video, 'link': video_url})
            print(f'Добавлена ссылка {video_url} на видео {name_video} успешно ')

with open('video_links.json', 'w', encoding='UTF-8') as json_file:
    json.dump(video_url_list, json_file, ensure_ascii=False)

    
 


