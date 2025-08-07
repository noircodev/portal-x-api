from decouple import config

TWITTER_CONSUMER_KEY = config("TWITTER_CONSUMER_KEY", default=None)
TWITTER_BEARER_TOKEN = config("TWITTER_BEARER_TOKEN", default=None)
TWITTER_CONSUMER_SECRET = config("TWITTER_CONSUMER_SECRET", default=None)
TWITTER_ACCESS_TOKEN = config("TWITTER_ACCESS_TOKEN", default=None)
TWITTER_ACCESS_TOKEN_SECRET = config(
    "TWITTER_ACCESS_TOKEN_SECRET", default=None)


class TwitterConfig:
    def __init__(self):
        self.keys = {
            "TWITTER_BEARER_TOKEN": TWITTER_BEARER_TOKEN,
            "TWITTER_ACCESS_TOKEN": TWITTER_CONSUMER_SECRET,
            "TWITTER_ACCESS_TOKEN_SECRET": TWITTER_CONSUMER_SECRET,
            "TWITTER_CONSUMER_KEY": TWITTER_CONSUMER_KEY,
            "TWITTER_CONSUMER_SECRET": TWITTER_CONSUMER_SECRET,
        }

    def __getattr__(self, item):
        """Raise an error if an API key is not initialized."""
        if item in self.keys:
            if self.keys[item] is None:
                raise NotImplementedError(f"{item} is not initialized.")
            return self.keys[item]
        raise AttributeError(
            f"'TwitterConfig' object has no attribute '{item}'")

    def get_all_keys(self):
        """Returns all API keys as a dictionary, raising an error for any uninitialized key."""
        for key, value in self.keys.items():
            if value is None:
                raise NotImplementedError(f"{key} is not initialized.")
        return self.keys


twitter_config = TwitterConfig()
