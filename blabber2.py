import tweepy
import openai
import os

# Authenticate to Twitter
auth = tweepy.OAuthHandler(os.environ["TWITTER_API_KEY"], os.environ["TWITTER_API_SECRET"])
auth.set_access_token(os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"])

# Authenticate to OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super().__init__()

    def on_status(self, tweet):
        if tweet.user.id_str == self.api.me().id_str:
            # Skip tweets that I have posted
            return
        try:
            tweet_text = tweet.extended_tweet["full_text"]
        except AttributeError:
            tweet_text = tweet.text
        prompt = f"Q: What's the sentiment of this tweet?\nA: The sentiment is"
        prompt += " positive." if tweet.favorite_count > 0 else " negative."
        prompt += f"\nQ: What's the topic of this tweet?\nA: The topic is {tweet.user.name}."
        prompt += f"\nQ: Generate a reply to this tweet:\nA:"
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=60,
            n=1,
            stop=None,
            temperature=0.5,
            timeout=4,
        )
        reply_text = response.choices[0].text.strip()
        reply_tweet = f"@{tweet.user.screen_name} {reply_text}"
        print(f"Replying to {tweet.user.name}: {reply_tweet}")
        try:
            self.api.update_status(
                status=reply_tweet,
                in_reply_to_status_id=tweet.id_str,
                auto_populate_reply_metadata=True,
            )
        except tweepy.TweepError as error:
            print(f"Error: {error.reason}")


class MyStream(tweepy.Stream):
    def __init__(self, *args, **kwargs):
        listener = MyStreamListener(kwargs.pop("api"))
        super().__init__(listener=listener, *args, **kwargs)


if __name__ == "__main__":
    myStream = MyStream(auth=auth, listener=None)
    myStream.filter(track=["python", "javascript", "ruby"])

