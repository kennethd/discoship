import functools
import inspect
import logging
import os

import bs4

from discoship.defs import TESTS_DATA_PATH


# run with global option --save-fixture-data to update tests/data fixtures
# with runtime parameters
SAVE_FIXTURE_DATA = False

log = logging.getLogger(__name__)


def save_bs4_data_fixture(func):
    """save input bs4 Tag object to tests/data for re-use in unit tests

    use this to decorate a function that accepts bs4 Tag object as 1st arg

    when running with `discoship --save-fixture-data` inputs of functions
    decorated with this will have their 1st arg written to tests/data
    """
    log.debug(f"save_beautifulsoup_data_fixture is called by {func.__name__}")

    @functools.wraps(func)
    def _func(soup, *args, **kwargs):
        mod = '.'.join(func.__module__.split('.')[1:])
        path = os.path.sep.join([TESTS_DATA_PATH, f'{mod}.{func.__name__}.htm'])
        log.info(f"save_bs4_data_fixture called; path={path}")
        if SAVE_FIXTURE_DATA:
            with open(path, 'w') as fh:
                fh.write(str(soup))
            log.info(f"created bs4 data fixture @ {path}")
        return func(soup, *args, **kwargs)
    return _func


def load_bs4_data_fixture(filename):
    """load data previously saved by save_bs4_data_fixture()

    reads HTML from filename, found in `tests/data` dir, converts back to
    beautifulsoup `Tag` object, and returns so tests can replicate runtime input
    """
    path = os.path.sep.join([TESTS_DATA_PATH, filename])
    with open(path, 'r') as fh:
        html = fh.read()
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def save_output_for_caller(func, ext='htm'):
    """save the ouput of func to tests/data on behalf of caller so tests can
    mock decorated function to return collected results

    see for example `discoship.io.fetch_url`, several data scraping functions
    call `fetch_url`, and would like to mock that function to return data
    collected from real-world sources

    for each caller, `fetch_url` saves a file to `tests/data` named something
    like `fetch_url-caller_name.htm`, which tests can load to use as mock data
    """

    @functools.wraps(func)
    def _func(*args, **kwargs):
        stack = inspect.stack()
        log.debug(stack[1])
        callername = stack[1].function
        filename = f'{func.__name__}-{callername}.{ext}'

        path = os.path.sep.join([TESTS_DATA_PATH, filename])
        result = func(*args, **kwargs)
        if SAVE_FIXTURE_DATA:
            with open(path, 'w') as fh:
                fh.write(result)
            log.info(f"saved data fixture for caller @ {path}")
        return result

    return _func

