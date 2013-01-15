from gevent import monkey
monkey.patch_all()

import os
import sys

import gevent
from gevent.queue import Queue

import whois


domains = '''
google.jp
www.google.co.jp
www.google.com
www.google.com.ua
www.fsdfsdfsdfsd.google.com
digg.com
imdb.com
microsoft.com
www.google.org
ddarko.org
google.net
www.asp.net
google.pl
www.ddarko.pl
google.co.uk
google.co
google.de
yandex.ru
google.us
google.eu
google.me
google.be
google.biz
google.info
google.name
google.it
google.cz
google.fr
dfsdfsfsdf
test.ez.lv
http://www.google.com.ua/
http://www.php.su/
http://xn--j1ail.xn--p1ai/
xn--80aab5b.xn--p1ai
xn----7sbblj5b.xn--p1ai
XN--80AAFXO8ABI6B0EJ.XN--P1AI
elitelimousines.co.nz
automig.su
borum.su
meatvideokurs.ucoz.ru
kafe-skazka.kiev.ua
crimean.info
actualshop.ru
ruserver.ru
dsavtoservis.ru
zaborych.ru
webinar.abok.ru
schastlivie-deti.ru
www.google.co.jp
fsmaster.com.ua
aitoc.com
folimpex.ru
santechnika-kafel.dp.ua
crimea-kudo.com.ua
souz-vs.clan.su
angry-birds.org.ua
oborudovanie-bu.info
franshiza.denginadom.org
maz-kamaz-zil.narod2.ru
podnebesnaya.biz
vm4070.vps.agava.net
ufa1remont.ucoz.ru
'''

'''
for domain in domains.split('\n'):
    if domain:
        print('-'*80)
        print(domain)
        if domain.endswith('/'):
            domain = domain[:-1]
        domain = domain.replace('http://', '').replace('https://', '')
        try:
            w = whois.query(domain, ignore_returncode=1)
            if w:
                wd = w.__dict__
                for k, v in wd.items():
                    print('%20s\t"%s"' % (k, v))
        except Exception as ex:
            excType, excObj, excTb = sys.exc_info()
            fname = os.path.split(excTb.tb_frame.f_code.co_filename)[1]
            print 'Exception {} caught in file {} on line {}: "{}"'.format(excType, fname, excTb.tb_lineno, ex)
'''

class WhoisThreadingTester(object):

    def __init__(self):
        self._domainsQueue = Queue()

    def addDomain(self, domain, resultReadyCallback):
        if not callable(resultReadyCallback):
            raise ValueError('resultReadyCallback must be callable')
        domain = domain.replace('https://', '').replace('http://', '')

        if domain.startswith('www.'):
            domain = domain[4:]

        if domain.endswith('/'):
            domain = domain[:-1]

        self._domainsQueue.put({domain: resultReadyCallback})
        print 'add domain {}'.format(domain)

    def _whoisGetter(self):
        while True:
            gevent.sleep(0)
            for nextTask in self._domainsQueue.get().items():
                result = None
                domain, resultReadyCallback = nextTask
                try:
                    result = whois.query(domain, ignore_returncode=True)
                except Exception as ex:
                    print type(ex)
                    print ex

                resultReadyCallback(result)

    def start(self):
        try:
            gevent.joinall([gevent.spawn(self._whoisGetter)])
        except (KeyboardInterrupt, gevent.hub.LoopExit) as ex:
            print 'Exit...'
        except Exception as ex:
            print type(ex)
            print ex


if __name__ == '__main__':
    def readyCallback(val):
        print('-'*80)
        print type(val)
        if isinstance(val, whois.Domain):
            for key in val.__dict__:
                print '{}   =>  {}'.format(key, val.__dict__[key])

    def test(whoisChecker):
        #gevent.sleep(10)
        for domain in domains.split('\n'):
            if domain:
                whoisChecker.addDomain(domain, readyCallback)
            #gevent.sleep()

    whoisChecker = WhoisThreadingTester()
    gevent.spawn(test, whoisChecker)
    whoisChecker.start()