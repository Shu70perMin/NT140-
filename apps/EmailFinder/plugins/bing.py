
app_email = None


def search(domain, limit):
    url = "http://www.bing.com/search?q=%40{word}&count=50&first={counter}"
    app_email.init_search(url, domain, limit, 0, 50, 'Bing')
    app_email.process()
    return app_email.get_emails()


class Plugin:
    def __init__(self, app, conf):#
        global app_email, config
        #config = conf
        app.register_plugin('bing', {'search': search})
        app_email = app
        