
app_email = None


def search(domain, limit):
    all_emails = []
    app_email.show_message("[+] Searching in Twitter")

   
    
    bingUrl = 'http://www.bing.com/search?q=site%3Atwitter.com+intitle:"on Twitter"+%40{word}&count=50&first={counter}'
    app_email.init_search(bingUrl, domain, limit, 0, 50, 'Bing + Twitter')
    app_email.process()
    all_emails += app_email.get_emails()
    
    googleUrl = 'https://www.google.com/search?num=100&start={counter}&hl=en&q=site%3Atwitter.com+intitle:"on Twitter"+"%40{word}"'
    app_email.init_search(googleUrl, domain, limit, 0, 100, 'Google + Twitter')
    app_email.process()
    all_emails += app_email.get_emails()

    
    return all_emails


class Plugin:
    def __init__(self, app, conf):#
        global app_email, config
        app.register_plugin('twitter', {'search': search})
        app_email = app
        