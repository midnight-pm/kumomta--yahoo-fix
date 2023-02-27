#!/usr/bin/env python3
import base64
import glob
import json
import os
import re
import subprocess
import sys

class Page(object):
    """ A page in the TOC, and its optional children """
    def __init__(self, title, filename, children=None):
        self.title = title
        self.filename = filename
        self.children = children or []

    def render(self, output, depth=0):
        indent = "  " * depth
        bullet = "- " if depth > 0 else ""
        output.write(f"{indent}{bullet}[{self.title}]({self.filename})\n")
        for kid in self.children:
            kid.render(output, depth + 1)


class Gen(object):
    """ autogenerate an index page from the contents of a directory """
    def __init__(self, title, dirname, index=None, extract_title=False):
        self.title = title
        self.dirname = dirname
        self.index = index
        self.extract_title = extract_title

    def render(self, output, depth=0):
        print(self.dirname)
        names = sorted(glob.glob(f"{self.dirname}/*.md"))
        children = []
        for filename in names:
            title = os.path.basename(filename).rsplit(".", 1)[0]
            if title == "index" or title == "_index":
                continue

            if self.extract_title:
                with open(filename, "r") as f:
                    title = f.readline().strip('#').strip()

            children.append(Page(title, filename))

        index_filename = f"{self.dirname}/index.md"
        index_page = Page(self.title, index_filename, children=children)
        index_page.render(output, depth)
        with open(index_filename, "w") as idx:
            if self.index:
                idx.write(self.index)
                idx.write("\n\n")
            else:
                try:
                    with open(f"{self.dirname}/_index.md", "r") as f:
                        idx.write(f.read())
                        idx.write("\n\n")
                except FileNotFoundError:
                    pass
            for page in children:
                idx.write(f"  - [{page.title}]({os.path.basename(page.filename)})\n")


TOC = [
    Page(
        "KumoMTA Documentation",
        "index.md",
        children=[
            Page(
                "Preface", "preface/index.md"
            ),
            Page(
                "General Information",
                "general/index.md",
                children=[
                    Page("About This Manual","general/about.md"),
                ]
                 ),
            Page(
                "User Guide",
                "guide/index.md",
            ),
            Page(
                "Referance Manual",
                "reference/index.md",
                children=[
                    Gen(
                        "module: kumo",
                        "reference/kumo",
                    ),
                    Gen(
                        "module: kumo.dkim",
                        "reference/kumo.dkim",
                    ),
                    Gen(
                        "object: address",
                        "reference/address",
                    ),
                    Gen(
                        "object: message",
                        "reference/message",
                    ),
                    Gen(
                        "events",
                        "reference/events",
                    ),
                    Gen("HTTP API", "reference/http", extract_title=True),
                ],
            ),
            Page("Change Log", "changelog.md"),
        ],
    )
]

os.chdir("docs")
with open("SUMMARY.md", "w") as f:
    f.write("<!-- this is auto-generated by docs/generate-toc.py, do not edit -->\n")
    for page in TOC:
        page.render(f)
