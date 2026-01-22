from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinja2.ext import Extension
import re
import os
import pypandoc
import sys
from dotenv import load_dotenv


class RelativeInclude(Extension):
    # This Jinja2 extension Created 2014 by Janusz Skonieczny
    # Source https://gist.github.com/wooyek/8d4c37d684a5ba38b8c1
    """Allows to import relative template names"""
    tags = set(["include2"])

    def __init__(self, environment):
        super(RelativeInclude, self).__init__(environment)
        self.matcher = re.compile("\.*")

    def parse(self, parser):
        node = parser.parse_include()
        template = node.template.as_const()
        if template.startswith("."):
            # determine the number of go ups
            up = len(self.matcher.match(template).group())
            # split the current template name into path elements
            # take elements minus the number of go ups
            seq = parser.name.split("/")[:-up]
            # extend elements with the relative path elements
            seq.extend(template.split("/")[1:])
            template = "/".join(seq)
            node.template.value = template
        return node


# load .env file
load_dotenv()

# removed some code  here that used to automatically SFTP the generated
# slides to my course server using paramiko. 
# I've deprecated that server, so for now I'll just keep slides locally

# Setup environment for Jinja
env = Environment(
    loader=FileSystemLoader("templates"),
    #extensions=[RelativeInclude],
    trim_blocks=True,
    lstrip_blocks=True,
)

# Adding -V for pandoc variables (uppercase V for theme support)
pdoc_args = [
    "-s",
    "--include-in-header=style.css",
    "--include-in-header=scripts.html",
    "--template=default_plus_chalkboard.revealjs",
    "-V", "theme=dracula",
    "-V", "width=1920",
    "-V", "height=1080",
    "-V", "viewDistance=50",
]

for root, dirs, files in os.walk("./templates"):
    for name in files:
        if(name.find(".md") == -1):
            continue
        thisTemplateName = name
        generatedMdFileName = "generated/markdown/" + name
        generatedHtmlFileName = "generated/html/" + name.replace(
            ".md", ".html"
        )
        try:
            template = env.get_template(thisTemplateName)
        except TemplateNotFound:
            # print("cant find " + thisTemplateName)
            continue
        output_from_parsed_template = template.render()

        with open(generatedMdFileName, "w") as fh:
            fh.write(output_from_parsed_template)

        pypandoc.convert_file(
            generatedMdFileName,
            to="revealjs",
            outputfile=generatedHtmlFileName,
            extra_args=pdoc_args,
        )

print('Done!')
