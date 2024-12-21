app_email = None


def search(domain, limit):
    url = 'http://www.baidu.com/search/s?wd="%40{word}"&pn={counter}'
    app_email.init_search(url, domain, limit, 0, 10, 'Baidu')
    app_email.process()
    return app_email.get_emails()


class Plugin:
    def __init__(self, app, conf):#
        global app_email, config
        app.register_plugin('baidu', {'search': search})
        app_email = app
        