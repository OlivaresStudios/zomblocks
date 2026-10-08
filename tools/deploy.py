"""Publishes public/ on GitHub Pages: the gh-pages branch of this repo, served on zomblocks.eu (CNAME).

    python tools/build.py && python tools/check_links.py      first: a full build, "0 broken"
    python tools/deploy.py ["commit message"]

The branch only holds the built site (one commit per publish); the sources stay on main.
"""
import datetime
import os
import shutil
import subprocess
import sys
import tempfile

WIKI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(WIKI, 'public')
DOMAIN = 'zomblocks.eu'


def git(*args, cwd):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def main():
    if not os.path.exists(os.path.join(PUBLIC, 'index.html')):
        sys.exit('public/ is empty: run tools/build.py first')
    message = sys.argv[1] if len(sys.argv) > 1 else 'Wiki build %s' % datetime.date.today().isoformat()
    remote = git('remote', 'get-url', 'origin', cwd=WIKI).strip()
    tmp = tempfile.mkdtemp(prefix='zomblocks_pages_')
    try:
        if subprocess.run(['git', 'clone', '--quiet', '--depth', '1', '--branch', 'gh-pages', remote, tmp], capture_output=True).returncode:
            git('init', '--quiet', '-b', 'gh-pages', cwd=tmp)               # first publish: a branch of its own
            git('remote', 'add', 'origin', remote, cwd=tmp)
        for name in os.listdir(tmp):
            if name != '.git':
                path = os.path.join(tmp, name)
                shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        shutil.copytree(PUBLIC, tmp, dirs_exist_ok=True)
        with open(os.path.join(tmp, 'CNAME'), 'w') as fh:
            fh.write(DOMAIN + '\n')
        open(os.path.join(tmp, '.nojekyll'), 'w').close()                    # serve the folders as they are
        git('add', '-A', cwd=tmp)
        if not git('status', '--porcelain', cwd=tmp).strip():
            print('nothing changed since the last publish')
            return
        git('commit', '--quiet', '-m', message, cwd=tmp)
        git('push', '--quiet', 'origin', 'gh-pages', cwd=tmp)
        print('published: https://%s/ (gh-pages %s)' % (DOMAIN, git('rev-parse', '--short', 'HEAD', cwd=tmp).strip()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
