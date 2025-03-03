import aiohttp
import asyncio
import os
import json

async def download_video(session, link_data):
    url = link_data['link']
    file_name = link_data['name'].replace('/', '')
    async with session.get(url) as response:
        with open(f'downloaded_video/{file_name}.mp4', 'wb') as f:
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
        tasks = [download_video(session, link) for link in video_url_list]
        await asyncio.gather(*tasks)

# Запускаем асинхронный цикл
asyncio.run(main())