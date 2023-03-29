from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from requests.sessions import Session

from scraper.otodom_scraper import OtoDomScraper


class TestScraper:
    @pytest.fixture()
    def scraper(self):
        yield OtoDomScraper

    @patch(
        "scraper.otodom_scraper.OtoDomScraper.PARAMS",
        {
            "agent": "test_header",
            "retry": {"connect": None, "read": None, "redirect": None},
        },
    )
    def test_if_session_initialized(self, scraper: OtoDomScraper):
        sc: OtoDomScraper = scraper()

        assert isinstance(sc.session, Session)
        assert "test_header" in sc.session.headers["User-agent"]

    @patch(
        "scraper.otodom_scraper.OtoDomScraper.construct_url_for_listing"
    )
    def test_if_listing_page_soup_returned(
        self, mock_construct_url, requests_mock, scraper: OtoDomScraper
    ):
        test_url: str = "https://www.test"
        mock_construct_url.return_value: str = test_url
        requests_mock.get(test_url, text="<p>test_html_markup</p>")

        sc: OtoDomScraper = scraper()
        bs4: BeautifulSoup = sc.get_listing_page_soup(page_no=1)

        assert isinstance(bs4, BeautifulSoup)
        assert "test_html_markup" in bs4.text

    def test_if_estate_page_soup_returned(
        self, requests_mock, scraper: OtoDomScraper
    ):
        sc: OtoDomScraper = scraper()
        test_url: str = "https://www.test"
        requests_mock.get(test_url, text="<p>test_html_markup</p>")

        bs4: BeautifulSoup = sc.get_estate_page_soup(
            estate_url=test_url
        )

        assert isinstance(bs4, BeautifulSoup)
        assert "test_html_markup" in bs4.text
