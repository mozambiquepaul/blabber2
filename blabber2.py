import openai
import tweepy
import os

# Load the Twitter API credentials and OpenAI API key
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
openai.api_key = os.environ['OPENAI_API_KEY']

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
