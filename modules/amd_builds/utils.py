import logging
from urllib.parse import urljoin, urlparse

import asyncpraw
from aiogram.utils.json import json

from core.config import reddit_config

log = logging.getLogger("amd_builds")


def load_videocards():
    with open("data/videocards.json") as file:
        return json.load(file)


def load_cpus():
    with open("data/cpu.json") as file:
        return json.load(file)


class RedditImageSearcher:
    _reddit = None

    @property
    def reddit(self):
        if not self._reddit:
            self._reddit = asyncpraw.Reddit(**reddit_config)
            self.reddit.read_only = True
        return self._reddit

    async def get_images_for_flair(self, subreddit: str, flair: str, limit=100) -> list:
        result = []

        subreddit = await self.reddit.subreddit(subreddit)
        async for submission in subreddit.search(f"flair:{flair}", sort="new", limit=limit):
            url = self.sanitize_url_parameters(submission.url)
            if self.is_reddit_url_an_image(url):
                photo_url = submission.url
            else:
                if not hasattr(submission, "media_metadata"):
                    continue
                image_dict = list(submission.media_metadata.values())[0]
                if image_dict["e"] != "Image":
                    continue
                photo_url = image_dict["s"]["u"]
            result.append({"photo": photo_url, "title": submission.title, "reddit_url": submission.permalink})
        return result

    @staticmethod
    def is_reddit_url_an_image(url: str) -> bool:
        return url.endswith(".png") or url.endswith(".jpg")

    @staticmethod
    def sanitize_url_parameters(url: str) -> str:
        return urljoin(url, urlparse(url).path)
