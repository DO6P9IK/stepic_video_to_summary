import whisper
import os
import subprocess
from multiprocessing import Pool
import time

# Создаем необходимые директории
files_names = os.listdir('downloaded_video')
os.makedirs('transcribed_video', exist_ok=True)
os.makedirs('audio_files', exist_ok=True)

# Загружаем модель один раз с явным указанием CPU
model = whisper.load_model("base", device="cpu")

def convert_to_audio(video_file):
    """Конвертирует видео в аудио с оптимизацией для распознавания речи"""
    video_path = f"downloaded_video/{video_file}"
    audio_path = f"audio_files/{os.path.splitext(video_file)[0]}.mp3"
    
    # Пропускаем, если аудиофайл уже существует
    if os.path.exists(audio_path):
        return audio_path
    
    try:
        # Конвертация в моно mp3 с низким битрейтом, что достаточно для распознавания
        cmd = f'ffmpeg -i "{video_path}" -ac 1 -ar 16000 -b:a 64k "{audio_path}" -y'
        subprocess.call(cmd, shell=True)
        return audio_path
    except Exception as e:
        print(f"Ошибка при конвертации {video_file}: {e}")
        return None

def process_file(item):
    try:
        start_time = time.time()
        # Конвертируем видео в аудио (легкий формат)
        audio_path = convert_to_audio(item)
        if not audio_path:
            print(f"Пропускаем файл {item} из-за ошибки конвертации")
            return
        
        # Транскрибируем аудио с оптимизированными настройками для CPU
        result = model.transcribe(
            audio_path, 
            language="ru",  # Указываем язык
            beam_size=3,    # Уменьшаем луч для ускорения
            best_of=1       # Отключаем множественную выборку
        )
        
        with open(f'transcribed_video/{item}.txt', 'w', encoding='UTF-8') as f:
            f.write(result['text'])
            
        elapsed = time.time() - start_time
        print(f'Файл {item} транскрибирован за {elapsed:.2f} секунд')
    except Exception as e:
        print(f'Ошибка в файле {item}: {str(e)}')

# Обрабатываем файлы последовательно, чтобы избежать перегрузки памяти
if __name__ == '__main__':
    # Используем меньше процессов для старого оборудования
    num_processes = 2  # Для K56CB достаточно 2 процесса
    
    with Pool(processes=num_processes) as pool:
        pool.map(process_file, files_names)