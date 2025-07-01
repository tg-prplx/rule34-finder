import requests as rq
import urllib.parse as parse
import random as rnd
import logging as log

class PollinationsImageGenerator:
    def __init__(self, model="flux", width=1024, height=1024, seed=rnd.randint(0, 100000000), nologo="true", enhance="true"):
        self.model = model
        self.width = width
        self.height = height
        self.seed = seed
        self.nologo = nologo
        self.enhance = enhance

    def generate_image(self, prompt: str, seed=rnd.randint(0, 10000000)):
        prompt_encoded = parse.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{prompt_encoded}"
            f"?model={self.model}&width={self.width}&height={self.height}"
            f"&seed={self.seed}&nologo={self.nologo}&enhance={self.enhance}"
        )
        
        response = rq.get(url)
        if response.status_code == 200:
            log.info(f"Image generated successfully: {url}")
            return url
        else:
            log.error(f"Failed to generate image: {response.status_code} {response.text}")