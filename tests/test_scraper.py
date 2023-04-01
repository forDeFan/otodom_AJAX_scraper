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
    def test_if_session_initialized_with_custom_user_agent(
        self, scraper: OtoDomScraper
    ):
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

    @patch("json.loads")
    @patch("scraper.otodom_scraper.BeautifulSoup.find")
    def test_if_listing_links_returned(
        self, mock_find, mock_json, scraper
    ):
        mock_find.text.return_value = None
        mock_json.return_value = {
            "props": {
                "pageProps": {
                    "data": {
                        "searchAds": {
                            "items": [
                                {
                                    "id": 1,
                                    "title": "test flat",
                                    "slug": "test-flat",
                                }
                            ]
                        }
                    }
                }
            }
        }

        sc: OtoDomScraper = scraper()
        bs4: BeautifulSoup = BeautifulSoup()

        assert (
            "test-flat"
            in sc.get_estate_links_from_listing(listing_soup=bs4)[0]
        )

    @patch("json.loads")
    @patch("scraper.otodom_scraper.BeautifulSoup.find")
    def test_if_estate_details_returned(
        self, mock_find, mock_json, scraper
    ):
        mock_find.text.return_value = None
        mock_json.return_value = {
            "props": {
                "pageProps": {
                    "ad": {
                        "description": 'DESCRIPTION:EXTREMLY LONG DESCRIPTION"',
                        "target": {"City": "gdansk"},
                        "characteristics": [
                            {
                                "key": "price",
                                "value": "545000",
                                "label": "Cena",
                                "localizedValue": "545 000 zł",
                            },
                            {
                                "key": "m",
                                "value": "52.7",
                                "label": "Powierzchnia",
                                "localizedValue": "52,70 m²",
                            },
                        ],
                    }
                }
            }
        }

        sc: OtoDomScraper = scraper()
        bs4: BeautifulSoup = BeautifulSoup()

        assert "gdansk" in sc.get_estate_details(estate_soup=bs4)
