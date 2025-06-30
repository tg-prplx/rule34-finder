from r34nfag import Rule34NewForAnimeGooners
from charCreate import CharCreate
from config import GROUP_COUNT
import logging as log

if __name__ == "__main__":
    bot = Rule34NewForAnimeGooners()
    char_creator = CharCreate()
    func_list: dict = {
        char_creator.choose_who: 'who',
        char_creator.choose_body_type: 'body_type',
        char_creator.choose_hair_style: 'hair_style',
        char_creator.choose_hair_color: 'hair_color',
        char_creator.choose_eyes: 'eyes',
        char_creator.choose_clothes: 'clothes',
        char_creator.choose_pose_action: 'pose_action',
        char_creator.choose_setting: 'setting',
        char_creator.choose_mood: 'mood',
        char_creator.choose_personality: 'personality',
        char_creator.choose_accessories_props: 'accessories_props',
        char_creator.choose_genre_theme: 'genre_theme',
        char_creator.choose_time_weather: 'time_weather',
        char_creator.choose_girls: 'girls',
        char_creator.choose_boys: 'boys',
    }

    for func, group in func_list.items():
        item = char_creator.get_tag_request_cli(group)
        if item < 0:
            log.warning(f"Skipping {group} selection.")
            continue
        func(item)

    bot.make_rule34_request(char_creator.get_character(), open_in_browser=True)

