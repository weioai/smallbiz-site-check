# smallbiz-site-check

The 30-line website check behind [We fetched 27,741 small-business websites in one California county. 18% still have no mobile layout.](https://dev.to/weio/we-fetched-27741-small-business-websites-in-one-california-county-18-still-have-no-mobile-layout-2alg)

One plain HTTP fetch per domain, standard library only, no JavaScript. It records whether the site answers, whether https works, whether there is a certificate error, whether a `viewport` meta tag exists, what built the site, the footer copyright year, and any email addresses on the page.

```
python3 sitecheck.py example.com other.org
python3 sitecheck.py -f domains.txt -o checked.jsonl
python3 sitecheck.py -f domains.txt --summary
```

Example summary output:

```
27741 domains; 16723 answered (60.3%); 11018 did not answer
  no viewport tag        3097  18.5% of live
  no working https       1326   7.9% of live
  certificate error       252   1.5% of live
  publish an email       3659  21.9% of live
  copyright <= 2022      1319  18.5% of 7120 with a year
```

(That run predates the `URLError` branch in `check()`, so its certificate-error line is an undercount; a re-test put the real figure near 900. The current script classifies those correctly. Details in the article.)

## What the results mean

- **No viewport tag** is a reliable "not built for phones" signal. The reverse is not reliable: a page can carry the tag and still overflow on a phone. Render it at 375px (headless Chromium, Playwright, or just your phone) before you act on a result.
- **Certificate error** means the browser will show a full-page warning before the site. In our data most of these sites are otherwise fine and simply let a certificate expire.
- **Did not answer** is an upper bound on "dead". In a hand-checked sample of 40, about two thirds were gone or parked and about a third were live sites answering 403 to scripted requests.

## Being polite

12 parallel fetches, one request per domain, a 15 second timeout, a normal browser user agent. Do not hammer a single host. Respect robots and terms where you scan; this is a one-time reachability check, not a crawler.

## About

Maintained by [Weio, Inc.](https://weio.ai/?utm_source=github&utm_medium=readme&utm_campaign=smallbiz-site-check), a small California company where AI operators do most of the work and the owner is accountable. We use this check to find businesses whose sites need a mobile layout or an https fix, and we sell those fixes at fixed prices with refund terms. Two of the checks are free to run on your own site without an account: the [https check](https://weio.ai/https-check.html?utm_source=github&utm_medium=readme&utm_campaign=smallbiz-site-check) and the [WordPress mobile speed report](https://weio.ai/services/wp-speed-fix.html?utm_source=github&utm_medium=readme&utm_campaign=smallbiz-site-check#report).

MIT license. Issues and pull requests welcome; we answer from sales@weio.ai.

## Free agency resource

For a human-readable workflow after the scan, see the
[practical speed-audit checklist for web agencies](AGENCY_SPEED_AUDIT_CHECKLIST.md).
It covers a repeatable mobile baseline, how to separate likely causes, and how
to make an evidence-based recommendation without promising a score in advance.

## Keep certificates from expiring again

Once a site is fixed, [weioai/https-check-action](https://github.com/weioai/https-check-action) runs the same certificate check nightly in GitHub Actions (bash + openssl, no key) and fails the job when a certificate is expired, expiring within N days, for the wrong host, or untrusted.
