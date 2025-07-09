import json
from config import TAGS_PATH
import logging as log

class CharCreate:
    def __init__(self):
        with open(TAGS_PATH, 'r', encoding='utf-8') as f:
            self.tags: dict = json.load(f)
        self.char: str = ''

    def choose_who(self, id: int):
        try:
           self.char += self.tags['who'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'who' tags.")
            return
        log.info(f"Character chosen: {self.char}")

    def choose_body_type(self, id: int):
        try:
            self.char += self.tags['body_type'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'body_type' tags.")
            return
        log.info(f"Body type chosen: {self.char}")

    def choose_hair_style(self, id: int):
        try:
            self.char += self.tags['hair_style'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'hair_style' tags.")
            return
        log.info(f"Hair style chosen: {self.char}")

    def choose_hair_color(self, id: int):
        try:
            self.char += self.tags['hair_color'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'hair_color' tags.")
            return
        log.info(f"Hair color chosen: {self.char}")

    def choose_eyes(self, id: int):
        try:
            self.char += self.tags['eyes'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'eyes' tags.")
            return
        log.info(f"Eyes chosen: {self.char}")

    def choose_clothes(self, id: int):
        try:
            self.char += self.tags['clothes'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'clothes' tags.")
            return
        log.info(f"Clothes chosen: {self.char}")

    def choose_pose_action(self, id: int):
        try:
            self.char += self.tags['pose_action'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'pose_action' tags.")
            return
        log.info(f"Pose/action chosen: {self.char}")

    def choose_setting(self, id: int):
        try:
            self.char += self.tags['setting'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'setting' tags.")
            return
        log.info(f"Setting chosen: {self.char}")

    def choose_mood(self, id: int):
        try:
            self.char += self.tags['mood'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'mood' tags.")
            return
        log.info(f"Mood chosen: {self.char}")

    def choose_personality(self, id: int):
        try:
            self.char += self.tags['personality'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'personality' tags.")
            return
        log.info(f"Personality chosen: {self.char}")

    def choose_accessories_props(self, id: int):
        try:
            self.char += self.tags['accessories_props'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'accessories_props' tags.")
            return
        log.info(f"Accessories/props chosen: {self.char}")

    def choose_genre_theme(self, id: int):
        try:
            self.char += self.tags['genre_theme'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'genre_theme' tags.")
            return
        log.info(f"Genre/theme chosen: {self.char}")

    def choose_time_weather(self, id: int):
        try:
            self.char += self.tags['time_weather'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'time_weather' tags.")
            return
        log.info(f"Time/weather chosen: {self.char}")

    def choose_girls(self, id: int):
        try:
            self.char += self.tags['girls'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'girls' tags.")
            return
        log.info(f"Girls chosen: {self.char}")

    def choose_boys(self, id: int):
        try:
            self.char += self.tags['boys'][id] + " "
        except IndexError:
            log.error(f"Invalid index {id} for 'boys' tags.")
            return
        log.info(f"Boys chosen: {self.char}")

    def get_character(self) -> str:
        if not self.char.strip():
            log.warning("No character attributes selected.")
            return "No character attributes selected."
        log.info(f"Final character description: {self.char.strip()}")
        return self.char.strip()

    def get_tags(self) -> dict:
        log.info("Returning available tags.")
        return self.tags

    def get_tag_request_cli_multi(self, tags_list: str) -> list:
        tags = self.get_tags()[tags_list]
        col_width = max(len(tag) for tag in tags) + 2
        cols = 4
        print(f"\nChoose {tags_list}:")
        print("-" * (col_width * cols))
        for i, tag in enumerate(tags):
            cell = f"{i}: {tag}".ljust(col_width)
            print(cell, end=' ')
            if (i + 1) % cols == 0:
                print()
        if len(tags) % cols != 0:
            print()
        print("-" * (col_width * cols))

        print("Введите номера тегов через запятую. Примеры: 0,2,5")
        print("s - skip до конца, b - back на предыдущий шаг, Enter - пропустить только этот")
        choice = input(f"Your choice (0-{len(tags)-1}, s:skip, b:back): ").strip()

        if choice.lower() == 's':
            return 'SKIP_ALL'
        if choice.lower() == 'b':
            return 'BACK'
        if not choice:
            return []
        try:
            ids = [int(x) for x in choice.split(',') if x.strip().isdigit() and 0 <= int(x.strip()) < len(tags)]
            return ids
        except Exception:
            print("Некорректный ввод, попробуйте снова.")
            return self.get_tag_request_cli_multi(tags_list)
