from rule34Py import rule34Py
import webbrowser as wb

r34 = rule34Py()

# 1. Берём случайный пост с тегами neko + -ai_generated
post = r34.random_post(['neko', '-ai_generated'])
print(f"ID={post['id']}, score={post['score']}")

# 2. Открываем sample_url в браузере
wb.open(post['img_sample_url'])

# 3. Смотрим комментарии
comments = r34.get_comments(post['id'])
for c in comments[:3]:
    print(f"{c['creator']['name']}: {c['content'][:80]}…")
