from core.stats import StatsEvents


class StatsEvents(StatsEvents):
    AMDBUILD = "amdbuild"
    AMDBUILD_ERROR = "amdbuild-error"


# VIDEOCARDS = load_videocards()
# CPUS = load_cpus()

REDDIT_URL = "https://gateway.reddit.com/desktopapi/v1/subreddits/Amd/search"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
