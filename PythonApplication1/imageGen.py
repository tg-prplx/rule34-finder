import requests as rq
import urllib.parse as parse
import random as rnd
import logging as log
import webbrowser

class PollinationsImageGenerator:
    def __init__(self, model="flux", width=1024, height=1024, seed=rnd.randint(0, 100000000), nologo="true", enhance="true"):
        self.model = model
        self.width = width
        self.height = height
        self.seed = seed
        self.nologo = nologo
        self.enhance = enhance

    def generate_image(self, prompt: str, seed=100440):
        prompt_encoded = parse.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{prompt_encoded}"
            f"?model={self.model}&width={self.width}&height={self.height}"
            f"&seed={seed}&nologo={self.nologo}&enhance={self.enhance}&referer=http://pollinations.ai&safe=false&private=true"
        )
        
        response = rq.get(url)
        if response.status_code == 200:
            log.info(f"Image generated successfully: {url}")
            return url
        else:
            log.error(f"Failed to generate image: {response.status_code} {response.text}")

if __name__ == "__main__":
    img = PollinationsImageGenerator()
    webbrowser.open(img.generate_image("tasteful, perfect anatomy, japanese anime style, hentai artwork, 2d anime, 2d illustration, cel shading, vibrant colors, sharp clean lines, manga aesthetics, HD screencap feel, 1girl small_breasts flat_chest loli long_hair naked_apron stockings masturbation shower"))
