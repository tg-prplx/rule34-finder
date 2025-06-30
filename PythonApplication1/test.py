import requests

# Параметры запроса
url = "https://api.rule34.xxx/index.php"
params = {
    "page": "dapi",
    "s": "post",
    "q": "index",
    "json": 1,  # Получить ответ в формате JSON
    "limit": 10,  # Ограничить количество постов
    "tags": "nakano_miku -ai_generated"  # Замените на нужный тег
}

# Выполнение GET-запроса
response = requests.get(url, params=params)

# Проверка статуса ответа
if response.status_code == 200:
    print(response.text)
    data = response.json()
    # Вывод информации о каждом посте
    for post in data:
        print(f"ID: {post['id']}, Tags: {post['tags']}, URL: {post['file_url']}")
else:
    print(f"Ошибка: {response.status_code}")
