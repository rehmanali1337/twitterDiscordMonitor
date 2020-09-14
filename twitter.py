import tweepy
import pprint
import json
from configparser import ConfigParser


class Twitter:
    def __init__(self):
        config = ConfigParser()
        config.read("conf.ini")
        consumer_key = config["CONF"]["consumer_key"]
        consumer_secret = config["CONF"]["consumer_secret"]
        access_token = config["CONF"]["access_token"]
        access_token_secret = config["CONF"]["access_token_secret"]
        self.target_name = config["CONF"]["target_account"]
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    async def get_tweets(self, since_id=None):
        to_return = []
        public_tweets = self.api.home_timeline(since_id=since_id)
        for tweet in public_tweets:
            if tweet.user.screen_name == self.target_name:
                to_return.append(tweet)
        if len(to_return) != 0:
            return to_return
        return None

    async def get_tweet_full_text(self, tweet_id):
        text = self.api.get_status(tweet_id, tweet_mode="extended")._json["full_text"]
        return text
