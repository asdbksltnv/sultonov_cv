# Adding a blog post

Each post is a folder in `posts/`. The folder name becomes the web address:
`posts/my-first-surgery/` turns into `asadbeksultonov.com/blog/my-first-surgery.html`.
Use lowercase letters, numbers and dashes only.

## 1. Make the folder and add your photos

```
posts/
  my-first-surgery/
    en.md          required, the English version
    uz.md          optional, Uzbek
    ru.md          optional, Russian
    theatre.jpg    photos for this post (any name)
    team.jpg
```

Resize photos before adding them. About 1600 px on the long side keeps pages fast.

## 2. Write `en.md`

```
---
title: My first assisted hip replacement
date: 2026-11-20
cover: theatre.jpg
cover_alt: The operating theatre before the case
summary: One or two sentences shown on the blog page and when the link is shared.
---
Write the story here. Leave an empty line between paragraphs.

## A heading inside the post

- A list item
- Another item

**Bold text** and [a link](https://example.com) also work.

![Describe the photo for people who can't see it](team.jpg "Caption shown under the photo")
```

- **date** can be a full date (`2026-11-20`), a month (`2026-11`) or a year (`2026`). Leave it out if you don't know it.
- **cover** is the big photo at the top and on the blog card.
- A photo line on its own shows one large photo. Put two or more photo lines together, with no empty line between them, to show them side by side.
- Videos (`.mp4`) work the same way as photos.
- Add `draft: yes` at the top to keep a post off the site while you work on it.

## 3. Translations (optional)

`uz.md` and `ru.md` only need `title`, `summary`, `cover_alt` and the text. The date and
cover come from `en.md`. If a translation is missing, the Uzbek and Russian blogs show the
English post with an "In English" label.

## 4. Build and publish

From the `site` folder:

```
python3 tools/build.py
git add -A
git commit -m "Add post: my first assisted hip replacement"
git push
```

The build stops with a clear message if a photo is missing or the date is in the wrong format.

## View counts

Each post shows how many times it was viewed, added up across all three languages. The
numbers come from GoatCounter. They only appear after you switch on **Settings → "Allow
adding visitor counts on your website"** at asadbeksultonov.goatcounter.com. GoatCounter
updates them every few hours, and posts with no views yet show no number.
