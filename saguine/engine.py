import os
import shutil
from pathlib import Path
import glob

import yaml
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader

HERE = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(HERE, 'templates')
STATIC_DIR = os.path.join(HERE, 'static')
CONFIG_FN = 'config.yml'


def htmlize(s):
    parts = s.split('.')
    if len(parts) > 1:
        return '.'.join([parts[0], 'html'])
    return '/'.join([parts[0], 'index.html'])


def cleanup(basepath, exclude=()):
    base, dirs, fnames = next(os.walk(basepath))
    dirs = list(map(lambda d: os.path.join(base, d), dirs))
    fnames = list(map(lambda fn: os.path.join(base, fn), fnames))
    for d in dirs:
        if os.path.basename(d) not in exclude:
            shutil.rmtree(d)
    for fn in fnames:
        if os.path.basename(fn) not in exclude:
            os.remove(fn)


def read_config(basepath):
    config_path = os.path.join(basepath, CONFIG_FN)
    with open(config_path) as f:
        config = yaml.load(f)
    return config


def init_site(basepath):
    try:
        Path(os.path.join(basepath, CONFIG_FN)).touch()
    except FileExistsError:
        pass
    try:
        os.mkdir(os.path.join(basepath, 'web'))
    except FileExistsError:
        pass
    try:
        shutil.copytree(TEMPLATE_DIR, os.path.join(basepath, 'templates'))
        shutil.copytree(STATIC_DIR, os.path.join(basepath, 'web', 'static'))
    except FileExistsError:
        print('Cannot initialize folders, because '
              '"templates" or "static" folders already exist.')


def create_base(basepath):
    config = read_config(basepath)
    nav_pages = config['pages']
    sitename = config['sitename']
    pages = []
    for page in nav_pages:
        name, url = list(page.items())[0]
        url = htmlize(url)
        pages.append({'name': name, 'url': '/{}'.format(url)})
    env = Environment(
        loader=FileSystemLoader([os.path.join(basepath, 'templates')])
    )
    base_meta = env.get_template('base_meta.html')
    base = base_meta.render(pages=pages, sitename=sitename)
    with open(os.path.join(basepath, 'templates', 'base.html'), 'w') as f:
        f.write(base)


def _gen_page(basepath, item):
    env = Environment(
        loader=FileSystemLoader([os.path.join(basepath, 'templates')])
    )
    page_view = env.get_template('page_view.html')
    md = Markdown()
    with open(os.path.join(basepath, 'site', item)) as f:
        content = md.convert(f.read())
    html = page_view.render(content=content)
    with open(os.path.join(basepath, 'web', htmlize(item)), 'w') as f:
        f.write(html)


def _gen_list(basepath, item):
    os.mkdir(os.path.join(basepath, 'web', item))
    env = Environment(
        loader=FileSystemLoader([os.path.join(basepath, 'templates')])
    )
    page_view = env.get_template('page_view.html')
    list_view = env.get_template('list_view.html')

    mds = glob.glob(os.path.join(basepath, 'site', item, '*.md'))
    fn_abs = list(map(os.path.abspath, mds))
    fn_urls = []
    for fn in fn_abs:
        html_fn = htmlize(os.path.basename(fn))
        md = Markdown()
        with open(fn) as f:
            content = md.convert(f.read())
        html = page_view.render(content=content)
        with open(os.path.join(basepath, 'web', item, html_fn), 'w') as f:
            f.write(html)
        fn_urls.append({
            'url': html_fn,
            'name': html_fn.split('.')[0]
        })
    list_html = list_view.render(pages=fn_urls)
    with open(os.path.join(basepath, 'web', item, 'index.html'), 'w') as f:
        f.write(list_html)


def generate(basepath):
    webpath = os.path.join(basepath, 'web')
    if os.path.exists(webpath):
        cleanup(webpath, exclude=['static'])
    nav_pages = read_config(basepath)['pages']
    for page in nav_pages:
        name, item = list(page.items())[0]
        if item.endswith('.md'):
            _gen_page(basepath, item)
        else:
            _gen_list(basepath, item)
