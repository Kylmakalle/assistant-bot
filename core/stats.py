class StatsEvents:
    # common
    ERROR = 'error'

    # voteban
    SELF_BAN = 'self-ban'
    VOTEBAN_CALL = 'voteban-call'
    VOTEBAN_CONFIRM = 'voteban-confirm'
    VOTEBAN_VOTE = 'voteban-vote'
    VOTEBAN_UNVOTE = 'voteban-unvote'
    ADMIN_BAN = 'admin-ban'
    ADMIN_KICK = 'admin-kick'

    # nsfw
    NSFW = 'nsfw'

    # captcha_button
    JOIN_CHAT = 'join-chat'
    CAPTCHA_TIMEOUT = 'captcha-timeout'
    CAPTCHA_PASSED = 'captcha-passed'
    CAPTCHA_ERROR = 'captcha-error'

    # Tempban
    TEMPBAN = 'admin-tempban'
