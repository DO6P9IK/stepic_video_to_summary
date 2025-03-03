import aiohttp
import asyncio
import os
import json

async def download_video(session, link_data, number_linc):
    url = link_data['link']
    file_name = ''.join(c for c in link_data['name'] if c not in '!?/:+,"()')
    async with session.get(url) as response:
        with open(f'downloaded_video/{number_linc}. {file_name}.mp4', 'wb') as f:
            async for chunk in response.content.iter_chunked(1048576):  # 1 MB chunks
                f.write(chunk)

async def main():
    # Создаем папку для загрузок
    os.makedirs('downloaded_video', exist_ok=True)
    
    # Загружаем список ссылок
    with open('video_links.json', 'r', encoding='UTF-8') as file:
        video_url_list = json.load(file)
    
    # Настраиваем асинхронную сессию
    async with aiohttp.ClientSession() as session:
        tasks = [download_video(session, link, num) for num, link in enumerate(video_url_list, 1)]
        await asyncio.gather(*tasks)

# Запускаем асинхронный цикл
asyncio.run(main())

filesname = os.listdir('downloaded_video')
filesname.sort(key=lambda x: int(x.split()[0].replace('.', '')))
with open('filesname.json', 'w', encoding='UTF-8') as file:
    json.dump(filesname, file, ensure_ascii=False, indent=4)