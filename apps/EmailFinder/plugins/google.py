
app_email = None


def search(domain, limit):
    url = 'https://www.google.com/search?num=100&start={counter}&hl=en&q="%40{word}"'
    app_email.init_search(url, domain, limit, 0, 100, 'Google')
    app_email.process()
    return app_email.get_emails()


class Plugin:
    def __init__(self, app, conf):#
        global app_email, config
        
        app.register_plugin('google', {'search': search})
        app_email = app
        
