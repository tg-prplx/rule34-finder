import sys
import logging as log
from r34nfag import Rule34NewForAnimeGooners
from charCreate import CharCreate

def browse_images(bot, char_tags, limit=10):
    """Интерактивная CLI-навигация по поиску изображений."""
    pid = 0  # page id
    images = []
    total_fetched = 0
    def fetch_page(pid):
        nonlocal images, total_fetched
        try:
            images = bot.make_rule34_request(
                char_tags, limit=limit, pid=pid, open_in_browser=False
            )
            if not isinstance(images, list) or not images:
                print("[Нет результатов на этой странице.]")
                images = []
                return False
            total_fetched = len(images)
            return True
        except Exception as e:
            print(f"[Ошибка при загрузке изображений: {e}]")
            images = []
            return False
    print("\n=== CLI-Навигация по Rule34 ===")
    print("Команды: n (next), p (prev), [номер], q (quit)")
    fetch_page(pid)
    while True:
        if not images:
            print("Попробуйте другую страницу или другой запрос (q для выхода).")
        else:
            print(f"\nСтраница {pid + 1}, позиций: {len(images)}.\n")
            for i, item in enumerate(images):
                tags_short = item.get("tags", "")[:60] + "..." if len(item.get("tags", "")) > 60 else item.get("tags", "")
                print(f"[{i}] {item.get('id', '??')} | Score: {item.get('score', '-')}, Tags: {tags_short}")
            print()
        cmd = input("Ваш выбор [n/p/номер/q]: ").strip().lower()
        if cmd == "n":
            pid += 1
            fetch_page(pid)
        elif cmd == "p":
            if pid > 0:
                pid -= 1
                fetch_page(pid)
            else:
                print("Это первая страница.")
        elif cmd == "q":
            print("Выход из просмотра.")
            break
        elif cmd.isdigit() and 0 <= int(cmd) < len(images):
            img_index = int(cmd)
            url = bot.get_link_from_data(images, img_index)
            print(f"Открываю изображение #{img_index} в браузере: {url}")
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception as e:
                print(f"Ошибка открытия браузера: {e}")
        else:
            print("Неизвестная команда, попробуйте снова.")

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)
    bot = Rule34NewForAnimeGooners()
    char_creator = CharCreate()
    func_list = [
        (char_creator.choose_who, 'who'),
        (char_creator.choose_body_type, 'body_type'),
        (char_creator.choose_hair_style, 'hair_style'),
        (char_creator.choose_hair_color, 'hair_color'),
        (char_creator.choose_eyes, 'eyes'),
        (char_creator.choose_clothes, 'clothes'),
        (char_creator.choose_pose_action, 'pose_action'),
        (char_creator.choose_setting, 'setting'),
        (char_creator.choose_mood, 'mood'),
        (char_creator.choose_personality, 'personality'),
        (char_creator.choose_accessories_props, 'accessories_props'),
        (char_creator.choose_genre_theme, 'genre_theme'),
        (char_creator.choose_time_weather, 'time_weather'),
        (char_creator.choose_girls, 'girls'),
        (char_creator.choose_boys, 'boys'),
    ]

    idx = 0
    history = []
    skip_all = False
    while idx < len(func_list):
        func, group = func_list[idx]
        choosen = char_creator.get_tag_request_cli_multi(group)
        if choosen == 'SKIP_ALL':
            print('Выбор пропущен до конца.')
            break
        elif choosen == 'BACK':
            if history:
                idx -= 1
                _, prev_group, prev_values = history.pop()
                continue
            else:
                print('Назад нельзя, это первый шаг')
                continue
        elif not choosen:
            history.append((func, group, []))
            idx += 1
            continue
        else:
            for item in choosen:
                func(item)
            history.append((func, group, choosen))
            idx += 1

    char_tags = char_creator.get_character()
    browse_images(bot, char_tags, limit=8)