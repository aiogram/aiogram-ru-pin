import asyncio
import os
from pathlib import Path

import mistune
from aiograph import Telegraph
from aiograph.utils.html import html_to_nodes


class TelegraphRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        if info == "inline-message":
            return f'<figure><iframe src="/embed/telegram?url={code}" width="640" height="360" frameborder="0" allowtransparency="true" allowfullscreen="true" scrolling="no"></iframe><figcaption></figcaption></figure>'
        else:
            return f"<pre>{mistune.util.escape(code)}</pre>"

    def list(self, text, ordered, level, start=None):
        if ordered:
            html = '<ol'
            if start is not None:
                html += ' start="' + str(start) + '"'
            return html + '>' + text + '</ol>'
        return '<ul>' + text + '</ul>'

    def list_item(self, text, level):
        return '<li>' + text + '</li>'


async def main():
    telegraph = Telegraph(os.environ["TELEGRAPH_TOKEN"])
    html = mistune.create_markdown(renderer=TelegraphRenderer())
    md_content = Path("README.md").read_text("utf-8")
    html_content = html(md_content)
    nodes_content = list(filter(lambda x: x != "\n", html_to_nodes(html_content)))
    await telegraph.edit_page(os.environ["TELEGRAPH_PATH"], title=os.environ["TELEGRAPH_TITLE"], content=nodes_content,
                              author_name=os.environ["TELEGRAPH_AUTHOR"], author_url=os.environ["TELEGRAPH_AUTHOR_URL"])

    await telegraph.close()

if __name__ == '__main__':
    asyncio.run(main())
