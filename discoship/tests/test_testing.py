import os
import unittest
from unittest.mock import patch

import bs4

from discoship.defs import SOUP_PARSER
from discoship.testing import (
    save_bs4_data_fixture, load_bs4_data_fixture,
    save_output_for_caller, load_saved_output,
    tmpdir,
)


HTML = """<table>
        <thead>
            <tr>
                <th>Col A</th>
                <th>Col B</th>
                <th>Col C</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>aaa</td>
                <td>bbb</td>
                <td>ccc</td>
            </tr>
            <tr>
                <td>AAA</td>
                <td>BBB</td>
                <td>CCC</td>
            </tr>
        </tbody>
    </table>"""
# need .find('table') else .name reports as '[document]'
SOUP = bs4.BeautifulSoup(HTML, SOUP_PARSER).find('table')


def test_bs4_equivalence():
    """teaching moment...

    this test exists as an exercise in trying to isolate the reason
    test_bs4_data_fixtures() was failing at the line:
    ```
        assert soup == SOUP
    ```
    while this worked:
    ```
        assert str(soup) == str(SOUP)
    ```

    docs suggest the former should be fine
    https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html#comparing-objects-for-equality

    turns out load_bs4_data_fixture() was doing a `soup = soup.find('table')`,
    while `SOUP.name` was == '[document]', solution was to be consistent with `.find()`
    """
    assert SOUP.name == 'table'
    soup = bs4.BeautifulSoup(HTML, SOUP_PARSER).find('table')
    assert soup.name == 'table'
    assert soup == SOUP

    with tmpdir() as tmp_path:
        path = f'{tmp_path}/bs4.Tag.htm'
        # @save_bs4_data_fixture
        with open(path, 'w') as fh:
            fh.write(str(soup))

        # this works
        with open(path, 'r') as fh:
            html = fh.read()
        soup = bs4.BeautifulSoup(html, SOUP_PARSER).find('table')
        assert soup == SOUP

        # still good
        with open(path, 'r') as fh:
            soup = bs4.BeautifulSoup(fh, SOUP_PARSER).find('table')
        assert soup == SOUP

        with patch('discoship.testing.TESTS_DATA_PATH', tmp_path):
            soup = load_bs4_data_fixture('bs4.Tag.htm', expect_to_find='table')
        # this had been working
        assert str(soup) == str(SOUP)
        # following was failing due to inconsistent use of .find('table')
        # fixed by adding it to `SOUP = bs4.BeautifulSoup(HTML, SOUP_PARSER).find('table')`
        assert soup == SOUP


def test_bs4_data_fixtures():
    with tmpdir() as tmp_path:
        with (
            patch('discoship.testing.SAVE_FIXTURE_DATA', True),
            patch('discoship.testing.TESTS_DATA_PATH', tmp_path),
        ):

            @save_bs4_data_fixture
            def write_some_soup(soup):
                pass

            write_some_soup(SOUP)
            expect_file = 'tests.test_testing.write_some_soup.htm'
            files = os.listdir(tmp_path)
            assert files == [expect_file]
            #soup_path = os.path.sep.join([tmp_path, expect_file])
            #with open(soup_path, 'r') as fh:
            #    print(fh.read())
            soup = load_bs4_data_fixture(expect_file, expect_to_find='table')
            assert isinstance(soup, bs4.Tag)
            assert isinstance(SOUP, bs4.Tag)
            assert soup == SOUP

