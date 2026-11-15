# Editing the portfolio pages

Each page of the portfolio is built from one file in this folder:

| File in `src/`      | Page                |
| ------------------- | ------------------- |
| `home.html`         | `index.html`        |
| `about.html`        | `about.html`        |
| `experience.html`   | `experience.html`   |
| `research.html`     | `research.html`     |
| `achievements.html` | `achievements.html` |
| `skills.html`       | `skills.html`       |
| `contact.html`      | `contact.html`      |

These files hold only the page content. The menu, footer and everything in
`<head>` (title, description, links for search engines and structured data)
are added by `tools/pages.py`, where each page's title and description are
listed at the top.

Don't edit the built pages (`index.html`, `about.html`, `uz/…`, `ru/…`)
directly: the next build overwrites them.

## After an edit

From the `site` folder:

```
python3 tools/build.py
```

The Uzbek and Russian pages are translated from the English ones using the
table in `tools/i18n.py`. If you change English text, the build lists the
lines whose translation is missing or out of date, so you can update that
table.
