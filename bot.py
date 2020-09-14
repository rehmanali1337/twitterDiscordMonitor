from twitter import Twitter
import asyncio
from discord import Embed
from discord import Webhook, AsyncWebhookAdapter
from datetime import datetime
from configparser import ConfigParser
import aiohttp
import shelve
import os
import re

config = ConfigParser()
config.read("conf.ini")
webhook_url = config["CONF"]["webhook_url"]


async def send_to_webhook(embed):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
        await webhook.send(embed=embed, username="On Twitter")
        print("Sent to webhook")


def create_embed(
    description=None,
    footer_image=None,
    media=None,
    author_icon=None,
    author_name=None,
    tweet_by=None,
):
    embed = Embed()
    # embed.title = "We are helpers!"
    embed.description = description
    embed.timestamp = datetime.utcnow()
    embed.color = 0xFFFF00
    embed.set_footer(text=f"@{tweet_by}")
    if footer_image:
        embed.set_footer(text=f"@{tweet_by}")
    if media:
        embed.set_image(url=media)
    # embed.set_thumbnail(url=thumbnail)
    embed.set_author(name=author_name, icon_url=author_icon)
    return embed


async def main():
    twitter = Twitter()
    if not os.path.exists("./tmps"):
        os.mkdir("./tmps")
    shelf = shelve.open("./tmps/data")
    while True:
        if not "last_tweet_id" in shelf:
            print("No previous ids")
            tweets = await twitter.get_tweets()
        else:
            print("Cached id found")
            last_tweet_id = shelf["last_tweet_id"]
            tweets = await twitter.get_tweets(since_id=last_tweet_id)
        if tweets:
            shelf["last_tweet_id"] = tweets[0].id
            shelf.sync()
            for tweet in tweets:
                med = None
                if "media" in tweet.entities:
                    media = tweet.entities["media"]
                    if len(media) != 0:
                        med = media[0]["media_url"]
                text = await twitter.get_tweet_full_text(tweet.id)
                text = re.sub(r"(?:\@|https?\://)\S+", "", text)
                name = tweet.user.name
                screen_name = tweet.user.screen_name
                author_image = tweet.user.profile_image_url_https
                embed = create_embed(
                    description=text,
                    media=med,
                    author_icon=author_image,
                    author_name=name,
                    tweet_by=screen_name,
                )
                await send_to_webhook(embed)
        print("Waiting for 1 minute before checking again...")
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Quiting the bot...")
        loop.close()
