
app_email = None


def search(domain, limit):
    url = "http://search.yahoo.com/search?p=%40{word}&n=100&ei=UTF-8&va_vt=any&vo_vt=any&ve_vt=any&vp_vt=any&vd=all&vst=0&vf=all&vm=p&fl=0&fr=yfp-t-152&xargs=0&pstart=1&b={counter}"
    app_email.init_search(url, domain, limit, 1, 100, 'Yahoo')
    app_email.process()
    return app_email.get_emails()


class Plugin:
    def __init__(self, app, conf):#
        global app_email, config
        #config = conf
        app.register_plugin('yahoo', {'search': search})
        app_email = app
        