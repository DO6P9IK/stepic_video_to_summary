from DrissionPage import Chromium, ChromiumOptions
import speech_recognition as sr
from pydub import AudioSegment
import pyautogui
import requests
import tqdm
import time
import os


base_url = "https://www.elibrary.ru/rubrics.asp"
login = 'aandrianov@bk.ru'
password = 'Issl2025'


def write_audio(url, name_audio_file='audio.mp3'):
    """Скачивает аудиофайл по указанному URL."""
    response = requests.get(url)
    with open(name_audio_file, 'wb') as file:
        file.write(response.content)


def audio_to_text(mp3_file_name='audio.mp3', output_name='audio.wav'):
    """Конвертирует MP3 файл в WAV и распознает текст"""
    # Конвертируем MP3 в WAV
    audio = AudioSegment.from_mp3(mp3_file_name)
    audio.export(output_name, format="wav")

    # Распознаем текст из аудио
    recognizer = sr.Recognizer()
    with sr.AudioFile(output_name) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)


def solve_recaptcha_with_audio(page):
    '''Решает reCaptcha'''
    print("Обнаружена reCAPTCHA, начинаем обработку...") 

    # Переключаемся в iframe с чекбоксом reCAPTCHA
    iframe_recaptcha = page.ele('css:iframe[title="reCAPTCHA"]', timeout=20)
    
    # Нажимаем на чекбокс reCAPTCHA
    recaptcha_anchor = iframe_recaptcha.ele('#recaptcha-anchor', timeout=20)
    recaptcha_anchor.click()
    time.sleep(2.7)

    # если чекбокс нажат то двигаемся дальше
    aria_checked = recaptcha_anchor.attr('aria-checked')
    if aria_checked == 'true':
        submit_button = page.ele('css:input[type="submit"][value="Продолжить"]')
        submit_button.click()
        print('Капча решена.')
        time.sleep(3)
        return

    # Переключаемся в iframe с набором картинок/аудио
    iframe_challenge = page.ele('css:iframe[title*="текущую проверку reCAPTCHA"]', timeout=20)

    # Нажимаем на кнопку "Аудио"
    audio_button = iframe_challenge.ele('#recaptcha-audio-button', timeout=20)
    audio_button.click()
    time.sleep(1.4)

    # Получаем ссылку на аудиофайл
    audio_src = iframe_challenge.ele('.rc-audiochallenge-tdownload-link', timeout=20).link
    if audio_src:
        print(f"Ссылка на аудиофайл капчи получена")
        
        # Скачиваем аудиофайл
        write_audio(audio_src)   
        try:
            # Распознаем текст из аудио
            recognized_text = audio_to_text().lower()
            print("Текст капчи распознан")
            time.sleep(4.2)

            # Вводим текст в поле ответа
            audio_response_input = iframe_challenge.ele('#audio-response')
            audio_response_input.input(recognized_text)
            button = iframe_challenge.ele('#recaptcha-verify-button')
            button.click()
            
        except Exception as e:
            print(f"[ERROR] Ошибка при работе с reCAPTCHA: {e}")
        
        finally:
            # Удаляем временные файлы
            os.remove('audio.mp3')
            os.remove('audio.wav')

    print('Капча решена.')
            

def handle_page_access(page, max_attempts=5):
    """Обработка страницы и решение капчи если она появилась"""
    attempts = 0
    while page.title == 'Тест Тьюринга' and attempts < max_attempts:
        solve_recaptcha_with_audio(page)
        time.sleep(2)
        if page.title == "Тест Тьюринга":
            submit_button = page.ele('css:input[type="submit"][value="Продолжить"]')
            submit_button.click()
        attempts += 1
        time.sleep(5)



def get_validated_number(prompt, max_value):
    """Получает и валидирует ввод от пользователя"""
    while True:
        value = input(prompt)
        if not value.isdigit():
            prompt = 'Это не число. Попробуйте снова: '
            continue
        value = int(value)
        if value <= 0:
            prompt = 'Число должно быть больше 0. Попробуйте снова: '
            continue
        if value > max_value:
            prompt = f'Число не должно быть больше {max_value}. Попробуйте снова: '
            continue
        return value
    


def handle_download_dialog():
    # Ждем появления диалога
    time.sleep(2)
    # Нажимаем Enter для подтверждения сохранения
    pyautogui.press('enter')


def handle_download(page, browser):
    """Обрабатывает процесс скачивания для одной статьи"""
    time.sleep(3) 
    try:
        # Пробуем несколько возможных способов найти ссылку на полный текст
        full_text_link = page.ele('xpath://a[contains(text(), "Полный текст")]', timeout=10) or \
                        page.ele('xpath://a[contains(@title, "Полный текст")]', timeout=10) or \
                        page.ele('css:a[href*="reader"]', timeout=10)
        
        if full_text_link:
            full_text_link.click()
            time.sleep(1)
            handle_download_dialog()
            time.sleep(2)
            if browser.tabs_count > 1:
                new_tab = browser.latest_tab
                handle_page_access(new_tab, 1)
                handle_download_dialog()
                browser.close_tabs([new_tab])
                browser.activate_tab(1)
                time.sleep(2)
            return True
        else:
            print("Предупреждение: Ссылка на полный текст не найдена")
            return False
    except Exception as e:
        print(f"Ошибка при скачивании статьи: {e}")
        return False


print('\nСКРИПТ ПОЛУЧЕНИЯ ДОКУМЕНТОВ С САЙТА')
print('НАУЧНОЙ ЭЛЕКТРОННОЙ БИБЛИОТЕКИ eLIBRARY.RU\n')
print("\nСкрипт запущен...\n")

# создаем папку для скачивания
download_folder = os.path.join(os.getcwd(), 'downloads')
os.makedirs(download_folder, exist_ok=True)

co = ChromiumOptions() 
co.headless()
co.incognito()
co.set_argument("--no-sandbox")
co.set_argument("--disable-blink-features=AutomationControlled")
co.use_system_user_path(True)

co.set_pref("download.default_directory", download_folder)
co.set_pref("download.prompt_for_download", False)
co.set_pref("download.directory_upgrade", True)
co.set_pref("plugins.always_open_pdf_externally", True)
co.set_pref("pdfjs.disabled", True)




browser = Chromium(addr_or_opts=co)
page = browser.latest_tab
if not page:
    print('Не удалось инициализировать браузер')
page.get(base_url)
handle_page_access(page)

# Проходим авторизацию
login_table = page.ele('@id=win_login')
if login_table:
    print('Авторизуемся...')
    login_inputs = login_table.eles('tag:input')
    login_inputs[0].input(login)
    login_inputs[1].input(password)
    login_inputs[3].click()
    login_inputs[2].click()
    time.sleep(2)
    handle_page_access(page)
    print('Авторизация пройдена успешно\n')

# получаем список из url рубрикатора и выводим на экран
print('Формируем список рубрик...')
rubricator_table = page.ele('#restab', timeout=5)
rubricator_link_tags = rubricator_table.eles('@href^rubric_titles')
rubricator_link_list = []
for id, el in enumerate(rubricator_link_tags, 1):
    link_text = el.text
    print(id, link_text)
    rubricator_link_list.append((id, el.text, el.link))

# Запрашиваем у пользователя номер рубрики и валидируем введенные данные1
print()
rubric_number = get_validated_number('Введите номер рубрики: ', len(rubricator_link_list))


# Переходим к списку журналов в выбранной рубрике
page.get(rubricator_link_list[rubric_number - 1][2])
time.sleep(1)
handle_page_access(page)

# получаем список из url журналов и выводим на экран
print('\nФормируем список журналов...')
journal_table = page.ele('#restab')
journal_link_tags = journal_table.eles('@href^contents.asp')
journal_link_list = []
for id, el in enumerate(journal_link_tags, 1):
    link_text = el.text
    print(id, link_text)
    journal_link_list.append((id, el.text, el.link))

# Запрашиваем у пользователя номер журнала и валидируем введенные данные1
print()
journal_number = get_validated_number('Введите номер журнала: ', len(journal_link_list))

# Переходим к списку статей в выбранном журнале
page.get(journal_link_list[journal_number - 1][2])
handle_page_access(page)

# получаем список из url номеров и выводим на экран
print('\nФормируем список номеров...')
number_table = page.ele('.right-panel')
number_link_tags = number_table.eles('@href^contents.asp')
number_link_list = []
for id, el in enumerate(number_link_tags, 1):
    link_text = el.text
    print(id, link_text)
    number_link_list.append((id, el.text, el.link))

# получаем список id для скачивания
print('\nПолучаем список ссылок для скачивания.')
print('Этот процесс может занять длительное время....')
article_ids = []
for number in tqdm.tqdm(number_link_list, desc="Обработка статей", unit="article", leave=False):
    page.get(number[2])
    handle_page_access(page)
    time.sleep(1)
    for _ in tqdm.tqdm(range(5), desc="Активация элементов", leave=False):  # Прокручиваем 5 раз
        page.run_js("window.scrollBy(0, window.innerHeight);")
        time.sleep(1)
    link_elements = page.eles('xpath://a[img[@title="Доступ к полному тексту открыт"]]', timeout=10)
    for link in link_elements:
        href_value = link.attr('href')
        parts = href_value.split('(')
        if len(parts) > 1:
            article_id = parts[1].split(')')[0]
            article_ids.append(article_id)
print(f'Получено {len(article_ids)} ссылок')

# скачиваем файлы
download_base_url = 'https://www.elibrary.ru/item.asp?id='
print('\nНачинаем загрузку файлов...')
successful_downloads = 0
failed_downloads = 0
for id in tqdm.tqdm(article_ids, desc="Загрузка файлов", unit="article", leave=False):
    try:
        page.get(download_base_url + id)
        time.sleep(2)
        handle_page_access(page)
        # time.sleep(2)
        if handle_download(page, browser):
            successful_downloads += 1
        else:
            failed_downloads += 1
            
    except Exception as e:
        print(f"\nError processing article {id}: {e}")
        failed_downloads += 1
        continue

print(f'\nЗагрузка завершена:')
print(f'Успешно загружено: {successful_downloads}')
print(f'Не удалось загрузить: {failed_downloads}\n')

print('\nДОКУМЕНТЫ ЗАГРУЖЕНЫ. ЗАКРОЙТЕ БРАУЗЕР\n')
