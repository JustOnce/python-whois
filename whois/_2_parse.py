import re

from . import tld_regexpr
from . import settings


DATES_KEYS = ('updated_date', 'expiration_date', 'creation_date', 'domain_name', )
TLD_RE = {}

def _add_tld(tld, v):
    extend = v.get('extend')
    if extend:
        e = get_tld_re(extend)
        tmp = e.copy()
        tmp.update(v)
    else:
        tmp = v

    if 'extend' in tmp: del tmp['extend']
    TLD_RE[tld] = {}
    for k, v in tmp.items():
        if settings.ONLY_DATES and k not in DATES_KEYS:
            continue
        TLD_RE[tld][k] = re.compile(v, re.IGNORECASE) if isinstance(v, str) else v

def get_tld_re(tld):
    if tld in TLD_RE: return TLD_RE[tld]
    v = getattr(tld_regexpr, tld)

    if tld == 'punycode_domains':
        for domain in v:
            _add_tld(domain, v[domain])
    else:
        _add_tld(tld, v)
        return TLD_RE[tld]


[get_tld_re(tld) for tld in dir(tld_regexpr) if tld[0] != '_']


def do_parse(whois_str, tld):
    r = {}

    if whois_str.count('\n') < 5:
        s = whois_str.strip().lower()
        if s == 'not found': return
        if s.count('error'): return
        raise Exception(whois_str)

    sn = re.findall(r'Server Name:\s?(.+)', whois_str, re.IGNORECASE)
    if sn:
        whois_str = whois_str[whois_str.find('Domain Name:'):]

    for k, v in TLD_RE.get(tld, TLD_RE['com']).items():
        if v is None:
            r[k] = ['']
        else:
            r[k] = v.findall(whois_str)or ['']

    return r