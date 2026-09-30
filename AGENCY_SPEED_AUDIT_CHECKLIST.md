# A practical speed-audit checklist for web agencies

This is a short, repeatable first pass for deciding which client sites deserve a
performance conversation. It is deliberately a diagnosis checklist, not a
promise that every item can be fixed with one plugin.

## 1. Start with a page a visitor actually uses

- Use the home page, a popular landing page, or the page the client says is
  slow. Record the exact URL and the date.
- Test once in an incognito browser on a phone connection if possible. Note
  what you observe before opening any score tool: blank screen, late hero
  image, jumping layout, unresponsive menu, or a checkout/form that feels slow.
- Check that both `https://example.com` and `https://www.example.com` open
  without a browser warning. A certificate warning is a separate urgent repair,
  not a speed optimization.

## 2. Take a repeatable baseline

- Run Lighthouse or PageSpeed Insights at least three times on mobile. Keep the
  median rather than selling a best or worst run.
- Record mobile Performance, LCP, INP/TBT, CLS, server response time, page
  weight, and the biggest opportunities it reports.
- Also run one desktop check. A good desktop score does not prove a site works
  well on a phone.
- Save a full-page phone screenshot. It makes the discussion concrete and lets
  you catch overflow or unreadable type that a score misses.

## 3. Separate likely causes before recommending work

| What you see | Check first | Typical next step |
| --- | --- | --- |
| Slow first response | hosting response time, cache headers, backend work | page/server cache, hosting review |
| Largest content is late | hero image size/format, preload, render blocking | resize/compress, modern format, preload only where justified |
| Browser freezes | unused JavaScript, third-party tags, long tasks | defer/remove scripts; audit tags |
| Page jumps | image dimensions, fonts, injected banners | reserve space; font/image sizing |
| Scores vary wildly | test conditions, CDN/cache warmness, third-party failures | repeat and disclose the variance |

Never promise a score number until you have a baseline and know the site,
host, and third-party constraints.

## 4. Turn the result into an honest client recommendation

1. State the visitor-visible symptom and the measurement conditions.
2. Name the two or three largest evidenced causes, not every Lighthouse hint.
3. Split work into changes you can safely make now, host/theme work, and items
   that need the client's approval (analytics, ads, payment tools, redesign).
4. Say what will be measured again after the work and what success means.
5. Keep a rollback/backup plan for production changes.

## Need a white-label baseline without doing the runs yourself?

Weio's [Speed audit pack](https://weio.ai/services/speed-audit-pack.html?utm_source=github&utm_medium=readme&utm_campaign=agency-speed-audit-checklist)
returns Lighthouse reports, screenshots and an evidence-based fix list for up to
10 public sites. It is a measurement product, not a guaranteed fix; agencies
can request white-label reports at no extra charge.

Maintained by [Weio, Inc.](https://weio.ai/?utm_source=github&utm_medium=readme&utm_campaign=agency-speed-audit-checklist).
