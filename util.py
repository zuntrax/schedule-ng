import logging
import sys
import urllib.request

from typing import Union


log = logging.getLogger(__name__)


def looks_like_url(path: str):
    url_starts = ["http://", "https://"]
    return any(path.startswith(x) for x in url_starts)


def write_output(path: str, content: str) -> bool:
    if path == 'STDOUT':
        log.info(f'Writing to stdout.')
        sys.stdout.write(content)
        sys.stdout.flush()
        return True
    else:
        log.info(f'Writing file "{path}".')
        with open(path, "w") as f:
            try:
                f.write(content)
                return True
            except PermissionError:
                log.error(f'No permission to open "{path}".')
                return False
            except IsADirectoryError:
                log.error(f'Cannot open directory "{path}".')
                return False
            except IOError:
                log.exception(f'Error writing file "{path}".')
                return False


def read_input(path: str) -> Union[str, None]:
    if path == 'STDIN':
        return sys.stdin.read()
    elif looks_like_url(path):
        with urllib.request.urlopen(path) as f:
            content = f.read().decode()
        return content
    else:
        log.info(f'Reading file "{path}".')
        try:
            with open(path, "r", encoding='utf-8-sig') as f:
                content = f.read()
            return content
        except PermissionError:
            log.error(f'No permission to open "{path}".')
            return None
        except IsADirectoryError:
            log.error(f'Cannot open directory "{path}".')
            return None
        except IOError:
            log.exception(f'Error reading file "{path}".')
            return None
