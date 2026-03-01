"""HTML to Markdown conversion for Zenn content."""

import re

import html2text


def _create_html2text():
    h = html2text.HTML2Text()
    h.body_width = 0
    h.unicode_snob = True
    h.protect_links = True
    h.mark_code = False
    return h


_h = _create_html2text()


def html_to_markdown(body_html):
    """Convert HTML to markdown with proper fenced code blocks."""
    if not body_html:
        return ""

    placeholders = []
    counter = [0]

    def replace_code_block(match):
        full = match.group(0)
        lang_match = re.search(r'class="language-(\w+)"', full)
        lang = lang_match.group(1) if lang_match else ""
        code_match = re.search(r'<code[^>]*>(.*?)</code>', full, re.DOTALL)
        if not code_match:
            return full
        code = code_match.group(1)
        code = re.sub(r'<[^>]+>', '', code)
        code = code.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        code = code.replace('&#39;', "'").replace('&quot;', '"')
        code = code.rstrip('\n')

        placeholder = f"\n\nCODEBLOCK_PLACEHOLDER_{counter[0]}\n\n"
        placeholders.append((f"CODEBLOCK_PLACEHOLDER_{counter[0]}", lang, code))
        counter[0] += 1
        return placeholder

    processed_html = re.sub(
        r'<(?:div[^>]*class="code-block-container"[^>]*>.*?)?<pre[^>]*>\s*<code[^>]*>.*?</code>\s*</pre>(?:\s*</div>)?',
        replace_code_block,
        body_html,
        flags=re.DOTALL,
    )

    md = _h.handle(processed_html)

    for placeholder, lang, code in placeholders:
        fence = f"```{lang}\n{code}\n```"
        md = md.replace(placeholder, f"\n{fence}\n")

    return md
