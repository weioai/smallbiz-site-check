#!/usr/bin/env python3
"""sitecheck.py: the 30-line website check behind the article
"We fetched 27,741 small-business websites in one California county".

For each domain it records, from ONE plain HTTP fetch (no JavaScript, no rendering):
  https        ok | cert-error | fail:<ExceptionName>      (https attempt)
  down         <ExceptionName> if neither https nor http answered
  final        URL after redirects
  https_final  True if the final URL is https
  viewport     True if a <meta name="viewport"> tag is present (minimum mobile-layout signal)
  copyright    latest 4-digit year found next to (c) / copyright
  gen          <meta name="generator"> content (what built the site), if any
  emails       up to 4 mailto: addresses found on the page
  size, tables page size in bytes and number of <table> tags

Usage:
  python3 sitecheck.py example.com other.org            # domains as arguments
  python3 sitecheck.py -f domains.txt -o checked.jsonl  # one domain per line
  python3 sitecheck.py -f domains.txt --summary          # print the counts only

Python 3.8+, standard library only.  Be polite: it runs 12 fetches in parallel with a
15-second timeout; do not point it at one host repeatedly.  A missing viewport tag is a
reliable "not built for phones" signal; its presence is NOT proof the layout works, so
render at 375px before you act on a result.  Sites behind bot walls answer 403 and will
show up as "down": treat the dead count as an upper bound.
"""
import argparse, json, re, ssl, sys, urllib.request, urllib.parse, urllib.error, concurrent.futures as cf

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126'
VIEWPORT = re.compile(r'<meta[^>]+name=["\']?viewport', re.I)
GENERATOR = re.compile(r'<meta[^>]+generator[^>]+content=["\']([^"\']+)', re.I)
COPYRIGHT = re.compile(r'(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?((?:19|20)\d{2})', re.I)
MAILTO = re.compile(r'mailto:([\w.+-]+@[\w-]+\.[\w.-]+)')


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    r = urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context())
    return r.geturl(), r.read(600000).decode('utf-8', 'ignore')


def hostname(s):
    s = s.strip()
    if not s or s.startswith('#'):
        return None
    return urllib.parse.urlparse(s if '://' in s else 'http://' + s).hostname


def check(host, timeout=15):
    f = {'host': host}
    body = None
    try:
        final, body = fetch('https://' + host, timeout)
        f['https'] = 'ok'
    except ssl.SSLError:
        f['https'] = 'cert-error'
    except urllib.error.URLError as e:
        # urllib wraps handshake failures: URLError(reason=SSLCertVerificationError)
        f['https'] = 'cert-error' if isinstance(e.reason, ssl.SSLError) else 'fail:' + type(e.reason).__name__
    except Exception as e:  # noqa: BLE001
        f['https'] = 'fail:' + type(e).__name__
    if body is None:
        try:
            final, body = fetch('http://' + host, timeout)
        except Exception as e:  # noqa: BLE001
            f['down'] = type(e).__name__
            return f
    f['final'] = final
    f['https_final'] = final.startswith('https')
    f['viewport'] = bool(VIEWPORT.search(body))
    years = [int(y) for y in COPYRIGHT.findall(body)]
    f['copyright'] = max(years) if years else None
    m = GENERATOR.search(body)
    f['gen'] = m.group(1) if m else None
    f['emails'] = sorted(set(e.lower() for e in MAILTO.findall(body)))[:4]
    f['size'] = len(body)
    f['tables'] = body.lower().count('<table')
    return f


def summary(rows):
    live = [r for r in rows if 'down' not in r]
    n, L = len(rows), max(1, len(live))
    def pct(k): return f'{100 * k / L:.1f}%'
    print(f'{n} domains; {len(live)} answered ({100 * len(live) / max(1, n):.1f}%); {n - len(live)} did not answer')
    print(f'  no viewport tag      {sum(1 for r in live if not r["viewport"]):6d}  {pct(sum(1 for r in live if not r["viewport"]))} of live')
    print(f'  no working https     {sum(1 for r in live if not r["https_final"]):6d}  {pct(sum(1 for r in live if not r["https_final"]))} of live')
    print(f'  certificate error    {sum(1 for r in live if r["https"] == "cert-error"):6d}  {pct(sum(1 for r in live if r["https"] == "cert-error"))} of live')
    print(f'  publish an email     {sum(1 for r in live if r["emails"]):6d}  {pct(sum(1 for r in live if r["emails"]))} of live')
    yrs = [r['copyright'] for r in live if r['copyright']]
    if yrs:
        old = sum(1 for y in yrs if y <= 2022)
        print(f'  copyright <= 2022    {old:6d}  {100 * old / len(yrs):.1f}% of {len(yrs)} with a year')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('domains', nargs='*')
    ap.add_argument('-f', '--file', help='file with one domain or URL per line')
    ap.add_argument('-o', '--out', help='write JSON lines here (default: stdout)')
    ap.add_argument('-j', '--jobs', type=int, default=12)
    ap.add_argument('-t', '--timeout', type=int, default=15)
    ap.add_argument('--summary', action='store_true', help='print counts only')
    a = ap.parse_args()
    hosts = list(a.domains)
    if a.file:
        hosts += open(a.file, encoding='utf-8').read().splitlines()
    hosts = list(dict.fromkeys(h for h in map(hostname, hosts) if h))
    if not hosts:
        ap.error('no domains given')
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        rows = list(ex.map(lambda h: check(h, a.timeout), hosts))
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r) + '\n')
    elif not a.summary:
        for r in rows:
            print(json.dumps(r))
    if a.summary or a.out:
        summary(rows)


if __name__ == '__main__':
    main()
