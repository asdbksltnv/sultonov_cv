#!/usr/bin/env python3
"""Build every generated page. Run from the site folder after any edit:

    python3 tools/build.py

1. tools/i18n.py  builds uz/index.html and ru/index.html from index.html
2. tools/blog.py  builds the blog (blog/, uz/blog/, ru/blog/) from posts/,
                  the old gallery redirects, and sitemap.xml
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import i18n  # noqa: E402
import blog  # noqa: E402

i18n.main()
blog.main()
