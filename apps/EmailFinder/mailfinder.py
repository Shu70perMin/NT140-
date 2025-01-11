#!/usr/bin/env python3
# encoding: UTF-8

import argparse
import sys
import time
import requests
import re
import os
import validators

from termcolor import colored
from argparse import RawTextHelpFormatter
from sys import platform as _platform
try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

__version__ = "1.3.2"

class myparser:
    
    def __init__(self):
        self.temp = []
        
    def extract(self, results, word):
            self.results = results
            self.word = word

    def genericClean(self):
        for e in '''<KW> </KW> </a> <b> </b> </div> <em> </em> <p> </span>
                    <strong> </strong> <title> <wbr> </wbr>'''.split():
            self.results = self.results.replace(e, '')
        for e in '%2f %3a %3A %3C %3D & / : ; < = > \\'.split():
            self.results = self.results.replace(e, ' ')
        
    def emails(self):
        self.genericClean()
        reg_emails = re.compile(
            '[a-zA-Z0-9.\-_+#~!$&\',;=:]+' +
            '@' +
            '[a-zA-Z0-9.-]*' +
            self.word)
        self.temp = reg_emails.findall(self.results)
        emails = self.unique()
        return emails
    
    def unique(self):
        self.new = list(set(self.temp))
        return self.new
    
###################################################################

class Emailfinder(object):
    
    def __init__(self, userAgent):
        self.plugins = {}
        self.userAgent = userAgent
        self.parser = myparser()
        self.activeEngine = "None"
        path = os.path.dirname(os.path.abspath(__file__)) + "/plugins/"
        plugins = {}
        
        sys.path.insert(0, path)
        for f in os.listdir(path):
            fname, ext = os.path.splitext(f)
            if ext == '.py':
                mod = __import__(fname, fromlist=[''])
                plugins[fname] = mod.Plugin(self, {'useragent':userAgent})
    
    def register_plugin(self, search_method, functions):
        self.plugins[search_method] = functions
        
    def get_plugins(self):
        return self.plugins
    
    def show_message(self, msg):
        print(green(msg))
        
    def init_search(self, url, word, limit, counterInit, counterStep, engineName):
        self.results = ""
        self.totalresults = ""
        self.limit = int(limit)
        self.counter = int(counterInit)
        self.url = url
        self.step = int(counterStep)
        self.word = word
        self.activeEngine = engineName
        
    def do_search(self):
        try:
            urly = self.url.format(counter=str(self.counter), word=self.word)
            headers = {'User-Agent': self.userAgent}
            r = requests.get(urly, headers=headers)
                
        except Exception as e:
            print(e)
            sys.exit(4)

        if r.encoding is None:
            r.encoding = 'UTF-8'

        self.results = r.content.decode(r.encoding)
        self.totalresults += self.results
    
    def process(self):
        while (self.counter < self.limit):
            self.do_search()
            time.sleep(1)
            self.counter += self.step
            print(green("[+] Searching in {}:".format(self.activeEngine)) + cyan(" {} results".format(str(self.counter))))
            
    def get_emails(self):
        self.parser.extract(self.totalresults, self.word)
        return self.parser.emails()
    
###################################################################

def yellow(text):
    return colored(text, 'yellow', attrs=['bold'])

def green(text):
    return colored(text, 'green', attrs=['bold'])

def red(text):
    return colored(text, 'red', attrs=['bold'])

def cyan(text):
    return colored(text, 'cyan', attrs=['bold'])

def unique(data):
        return list(set(data))

###################################################################

def limit_type(x):
    x = int(x)
    if x > 0:
        return x
    raise argparse.ArgumentTypeError("Minimum results limit is 1.")

def checkDomain(value):
    domain_checked = validators.domain(value)
    if not domain_checked:
        raise argparse.ArgumentTypeError('Invalid {} domain.'.format(value))
    return value

###################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", '--domain', action="store", metavar='DOMAIN', dest='domain', 
                        default=None, type=checkDomain, help="Domain to search.") 
    parser.add_argument("-e", '--engine', action="store", metavar='ENGINE', dest='engine', 
                        default="all", type=str, help="Select search engine plugin(eg. '-e google').")  
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    
    if not args.domain:
        print(red("[-] Please specify a domain name to search."))
        sys.exit(2)
    domain = args.domain

    userAgent = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1")
       
    filename = ""
    limit = 100       
    engine = args.engine
    app = Emailfinder(userAgent)
    plugins = app.get_plugins()

    all_emails = []
    excluded = []
    
    if engine == "all":
        print(green("[+] Searching everywhere"))
        for search_engine in plugins:
            if search_engine not in excluded:
                all_emails += plugins[search_engine]['search'](domain, limit)
    elif engine not in plugins:
        print(red("[-] Search engine plugin not found"))
        sys.exit(3)
    else:
        all_emails = plugins[engine]['search'](domain, limit)
    all_emails = unique(all_emails)
    
    if not all_emails:
        print(red("[-] No emails found"))
        sys.exit(4)

    print(green("[+] Emails found: ") + cyan(len(all_emails)))

    for email in all_emails:
        print(email)
