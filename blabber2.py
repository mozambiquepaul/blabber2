import openai
import tweepy
import os

# Load the Twitter API credentials and OpenAI API key
consumer_key = "UXa53PchB3GcKYwTeqOexcU6P"
consumer_secret = "22MNTwPl5aBREyLp3XH9mZprFyhEYd0fsS0eUsY5ZyiXrTDRAZ"
access_token = "860639827-W8l8F999mac4T5Z1f1AV9LRuEI0xuANJt0lWReOk"
access_token_secret = "v6aWN6jeQr4vmo8O0OPbXJKQIN4gwj5JPRFHKKBqvTObM"
openai.api_key = "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"

# Authenticate with the Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Define a function to respond to a tweet or direct message using the OpenAI API
def respond_to_tweet(tweet):
    # Use the OpenAI API to generate a response
    prompt = "Reply to this tweet: " + tweet.text
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0].text.strip()
    # Post the response to Twitter
    api.update_status(
        status=response,
        in_reply_to_status_id=tweet.id,
        auto_populate_reply_metadata=True,
    )

# Define a class that listens for incoming tweets and direct messages
class MyStreamListener(tweepy.Stream):
    def __init__(self, api):
        self.api = api
        super().__init__(auth=self.api.auth, listener=self)

    def on_status(self, status):
        if status.user.id != self.api.me().id:  # Ignore self-tweets
            respond_to_tweet(status)

    def on_direct_message(self, message):
        if message.sender_id != self.api.me().id:  # Ignore self-messages
            respond_to_tweet(message)

# Create a stream to listen for incoming tweets and direct messages
myStreamListener = MyStreamListener(api)

# Start listening for incoming tweets and direct messages
myStreamListener.filter(track=[api.me().screen_name], is_async=True)
