from g4f.client import Client
from weasyprint import HTML
from PyPDF2 import PdfMerger
import os


def get_anime_answer(qutestion):
    client = Client()
    system_message = {
        "role": "system",
        "content": "Ты профессиональный аналитик. Ты делаешь точные и понятные конспекты из предоставленного текста. И облачаешь их в красивый html код",
    }
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[system_message, {"role": "user", "content": qutestion}],
        temperature=0.2,
    )
    answer = response.choices[0].message.content
    return answer

question = 'сделай конспект из следующего текста в названии не пиши слово конспект: '

filesname = os.listdir('transcribed_video')
filesname.sort(key=lambda x: int(x.split()[0].replace('.', '')))

os.makedirs('summary_files', exist_ok=True)

for file_name in filesname:

    with open(f'transcribed_video/{file_name}', 'r', encoding='UTF-8') as file:
        transcribed_text = file.read()
    
    answer = get_anime_answer(question + transcribed_text).lstrip('```html').rstrip('```')

    HTML(string=answer).write_pdf(f'summary_files/{file_name[:-4]}.pdf')
    print(f'Файл {file_name[:-4]}.pdf создан')

pdf_files = os.listdir('summary_files')
pdf_files.sort(key=lambda x: int(x.split()[0].replace('.', '')))

merger = PdfMerger()

for pdf in pdf_files:
    with open(f'summary_files/{pdf}', "rb") as f:
        merger.append(f)

with open("Конспект.pdf", "wb") as output_file:
    merger.write(output_file)

merger.close()