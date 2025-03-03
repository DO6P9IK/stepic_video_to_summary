import os
import whisper
import subprocess
import time
import json

def convert_to_audio(video_file):
    """Конвертирует видео в аудио с оптимизацией для распознавания речи"""
    video_path = f"downloaded_video/{video_file}"
    audio_path = f"{os.path.splitext(video_file)[0]}.mp3"
    # Пропускаем, если аудиофайл уже существует
    if os.path.exists(audio_path):
        return audio_path
    try:
        # Конвертация в моно mp3 с низким битрейтом
        cmd = f'ffmpeg -i "{video_path}" -ac 1 -ar 16000 -b:a 64k "{audio_path}" -y'
        subprocess.call(cmd, shell=True)
        return audio_path
    except Exception as e:
        print(f"Ошибка при конвертации {video_file}: {e}")
        return None
    
filesname = os.listdir('downloaded_video')
filesname.sort(key=lambda x: int(x.split()[0].replace('.', '')))

with open('filesname.json', 'r', encoding='UTF-8') as file:
    filesname = json.load(file)

os.makedirs('transcribed_video', exist_ok=True)

model = whisper.load_model("base")  

modified_filesname = []
count = 0

for name in filesname:
    try:
        start = time.perf_counter()
        audio_path = convert_to_audio(name)
        result = model.transcribe(audio_path)
        transcribed_file_name = 'transcribed_video/' + audio_path[:-4] + '.txt'
        with open(transcribed_file_name, 'w', encoding='UTF-8') as file:
            file.write(result['text'])
        time_work = time.perf_counter() - start
        print(f'файл {name} транскирибирован за {time_work} сек.')
    except:
        with open('ERRORS.txt', 'a', encoding='UTF-8') as file:
            message = f'Ошибка транскрибации файла {name}\n'
        continue
    count += 1
    modified_filesname = filesname[count:]
    with open('filesname.json', 'w', encoding='UTF-8') as file:
        json.dump(modified_filesname, file, ensure_ascii=False, indent=4)
    os.remove(audio_path)

