import asyncio
import os
import sys
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


async def main(args: str):
    telegraph = Telegraph()
    try:
        html = mistune.create_markdown(renderer=TelegraphRenderer())
        md_content = Path("README.md").read_text("utf-8")
        html_content = html(md_content)
        nodes_content = list(filter(lambda x: x != "\n", html_to_nodes(html_content)))
        match args:
            case "deploy":
                token = os.environ["TELEGRAPH_TOKEN"]
                path = os.environ["TELEGRAPH_PATH"]
                title = os.environ["TELEGRAPH_TITLE"]
                author = os.environ["TELEGRAPH_AUTHOR"]
                author_url = os.environ["TELEGRAPH_AUTHOR_URL"]
                telegraph.token = token
                await telegraph.edit_page(path, title=title,
                                          content=nodes_content,
                                          author_name=author,
                                          author_url=author_url)
            case "preview":
                title = os.environ["TELEGRAPH_TITLE"]
                author = os.environ["TELEGRAPH_AUTHOR"]
                author_url = os.environ["TELEGRAPH_AUTHOR_URL"]
                await telegraph.create_account(short_name=author, author_name=author, author_url=author_url)
                page = await telegraph.create_page(title, nodes_content, author_name=author, author_url=author_url)
                print(f"PAGE_URL={page.url}")
    finally:
        await telegraph.close()


if __name__ == '__main__':
    asyncio.run(main("".join(sys.argv[1:])))
