# -*- coding: utf-8 -*-

import os

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
source_suffix = '.rst'
master_doc = 'index'
project = 'Sphinx Code Include'
year = '2019'
author = 'Colin Kennedy'
copyright = '{0}, {1}'.format(year, author)
version = release = '2.0.1'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/ColinKennedy/sphinx-code-include/issues/%s', '#'),
    'pr': ('https://github.com/ColinKennedy/sphinx-code-include/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'sphinx_rtd_theme'

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False


# Add this folder to `sys.path` so that Python can import conf.py.
# Normally we'd never do this. But this is done to show that the
# code-include directive can get the source-code anything that's
# importable.
#
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root, "src"))

extensions += ["code_include.extension", "sphinx.ext.intersphinx", "sphinx_rtd_theme"]

html_theme = "sphinx_rtd_theme"

intersphinx_mapping = {
    "https://requests.kennethreitz.org/en/latest": None,
}
