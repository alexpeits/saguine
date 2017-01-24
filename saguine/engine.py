import os
import glob
import shutil
import logging

import yaml
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader

HERE = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(HERE, 'templates')
STATIC_DIR = os.path.join(HERE, 'static')
CONFIG_FN = 'config.yml'
FORMATS = ('md', )
MD_DEFAULTS = {'description': ''}

logging.basicConfig(level=logging.INFO)

class FormatError(Exception):
    message = 'Unsupported format'


def to_url(target):
    name, ext = os.path.splitext(target)
    if ext:
        # name.html
        return '.'.join([name, 'html'])
    # name/index.html
    return '/'.join([name, 'index.html'])


def read_config(path):
    config_path = os.path.join(path, CONFIG_FN)
    with open(config_path) as f:
        config = yaml.load(f)
    return config


class Saguine:

    md_ext = {}

    def __init__(self, path):
        self.path = path
        self.config = read_config(path)

        self.site = os.path.join(path, 'site')
        self.web = os.path.join(path, 'web')
        self.templates = os.path.join(path, 'templates')

        self.base = os.path.join(self.templates, 'base.html')

        self.pages = {}

    @property
    def tmpl(self):
        return Environment(loader=FileSystemLoader(self.templates))

    @property
    def page_view(self):
        return self.tmpl.get_template('page_view.html')

    @property
    def list_view(self):
        return self.tmpl.get_template('list_view.html')

    def create_base(self):
        """Read the config and generate the base template from base_meta.

        Returns:
            str: the generated html template

        """
        nav_pages = self.config['pages']  # the navbar links
        sitename = self.config['sitename']

        pages = []
        for page in nav_pages:
            name, target = list(page.items())[0]
            ext = os.path.splitext(target)[1].strip('.')
            if ext and ext not in FORMATS:
                raise FormatError('Unsupported extension {}'.format(ext))
            url = to_url(target)
            pages.append({'name': name, 'url': '/{}'.format(url)})

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        base_meta = env.get_template('base_meta.html')
        base = base_meta.render(pages=pages, sitename=sitename)
        return base

    def init_folders(self):
        """For now, delete all files and regenerate project structure.

        TODO: recreate only what is needed

        """
        # remove previous
        shutil.rmtree(self.web, ignore_errors=True)
        shutil.rmtree(self.templates, ignore_errors=True)
        os.mkdir(self.web)
        # copy static files and templates
        logging.info('Copying static files...')
        shutil.copytree(STATIC_DIR, os.path.join(self.web, 'static'))
        logging.info('Copying templates...')
        shutil.copytree(TEMPLATE_DIR, self.templates)

        # create base template
        with open(self.base, 'w') as f:
            f.write(self.create_base())

    def gen_page(self, target):
        """Return a rendered page from markup"""
        md = Markdown(
            extensions=[
                'markdown.extensions.meta',
                'markdown.extensions.codehilite'
            ],
            extension_configs=self.md_ext
        )
        with open(os.path.join(self.site, target)) as f:
            content = md.convert(f.read())
        url = to_url(target)
        path = os.path.join(self.web, url)
        meta = md.Meta
        if 'pagetitle' in meta:
            pagetitle = md.Meta['pagetitle'][0]
        else:
            pagetitle = os.path.basename(target).split('.')[0]

        html = self.page_view.render(content=content, pagetitle=pagetitle)
        with open(path, 'w') as f:
            f.write(html)
        self.pages[target] = '/' + url

    def gen_list(self, target):
        os.mkdir(os.path.join(self.web, target))
        markups = glob.glob(os.path.join(self.site, target, '*.md'))
        urls = []
        for fn in markups:
            logging.info('    Found target: {}'.format(os.path.basename(fn)))
            html_fn = to_url(os.path.basename(fn))
            md = Markdown(
                extensions=[
                    'markdown.extensions.meta',
                    'markdown.extensions.codehilite'
                ],
                extension_configs=self.md_ext
            )
            with open(fn) as f:
                content = md.convert(f.read())
            meta = md.Meta
            url = html_fn
            if 'date' in meta:
                # TODO
                date = md.Meta['date'][0]
                if date:
                    path = os.path.join(self.web, target, date)
                    os.makedirs(path, exist_ok=True)
                    url = '/'.join([date, html_fn])
            if 'title' in meta:
                title = md.Meta['title'][0]
            else:
                title = html_fn.split('.')[0]
            if 'pagetitle' in meta:
                pagetitle = md.Meta['pagetitle'][0]
            else:
                pagetitle = title

            html = self.page_view.render(content=content, pagetitle=pagetitle)
            with open(os.path.join(self.web, target, url), 'w') as f:
                f.write(html)
            self.pages[os.path.basename(fn)] = '/' + '/'.join([target, url])

            urls.append({
                'url': url,
                'name': title
            })
        list_html = self.list_view.render(pages=urls)
        with open(os.path.join(self.web, target, 'index.html'), 'w') as f:
            f.write(list_html)

    def generate_web(self):
        """Generate html files from markup and put into appropriate dirs."""
        nav_pages = [
            list(item.items())[0]
            for item in read_config(self.path)['pages']
        ]
        for _, target in nav_pages:
            name, ext = os.path.splitext(target)
            if ext:
                logging.info('Found target: {}'.format(target))
                self.gen_page(target)
            else:
                logging.info('Found folder: {}'.format(target))
                self.gen_list(target)

    def run(self):
        self.init_folders()
        self.generate_web()


def main():
    import sys
    if len(sys.argv) != 2:
        print('You must provide a path for the site root')
        sys.exit(1)
    path = sys.argv[1]
    gen = Saguine(path)
    gen.run()


if __name__ == '__main__':
    main()
