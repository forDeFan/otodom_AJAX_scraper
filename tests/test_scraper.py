from typing import List
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from requests.sessions import Session

from data_types.estate import Estate
from data_types.estate_details import EstateDetails
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

    @patch("scraper.otodom_scraper.OtoDomScraper.get_estate_details")
    @patch("scraper.otodom_scraper.OtoDomScraper.get_estate_page_soup")
    def test_if_estate_details_returned_at_parse_estate(
        self, mock_soup, mock_details, scraper: OtoDomScraper
    ):

        mock_soup.return_value = None
        mock_details.return_value = [
            "test_price",
            "test_size",
            "test_location",
            "test_description",
        ]

        sc: OtoDomScraper = scraper()
        result: EstateDetails = sc.parse_estate(estate_url="test")

        assert isinstance(result, EstateDetails)
        assert "test_description" in result.description

    @patch(
        "scraper.otodom_scraper.OtoDomScraper.PARAMS",
        {
            "agent": "test_header",
            "retry": {"connect": None, "read": None, "redirect": None},
            "sleep_time": 0,
            "verbose_logging": False,
        },
    )
    @patch("scraper.otodom_scraper.OtoDomScraper.parse_estate")
    @patch(
        "scraper.otodom_scraper.OtoDomScraper.get_estate_links_from_listing"
    )
    def test_if_list_of_estates_returned_when_parse_page(
        self, mock_links, mock_parse, scraper
    ):
        mock_links.return_value = ["test_url_1", "test_url_2"]
        mock_parse.return_value = EstateDetails(
            price="test_price",
            size="test_size",
            location="test_location",
            description="test_description",
        )

        sc: OtoDomScraper = scraper()
        result: List[Estate] = sc.parse_page(listing_soup="test")

        assert "test_url_1" in result[0].url
        assert isinstance(result[0].details, EstateDetails)

    @patch(
        "scraper.otodom_scraper.OtoDomScraper.PARAMS",
        {
            "agent": "test_header",
            "retry": {"connect": None, "read": None, "redirect": None},
            "sleep_time": 0,
            "verbose_logging": False,
            "page_limit": 1,
        },
    )
    @patch("scraper.otodom_scraper.OtoDomScraper.parse_page")
    @patch("scraper.otodom_scraper.OtoDomScraper.get_listing_page_soup")
    def test_if_list_of_estates_returned_when_parse_site(
        self, mock_listing, mock_parse, scraper
    ):
        mock_listing.return_value = None
        mock_parse.return_value = [
            Estate(
                url="test_url_estate_1",
                details=EstateDetails(
                    price="test_price",
                    size="test_size",
                    location="test_location",
                    description="test_description",
                ),
            ),
            Estate(
                url="test_url_estate_2",
                details=EstateDetails(
                    price="test_price_2",
                    size="test_size",
                    location="test_location",
                    description="test_description",
                ),
            ),
        ]

        sc: OtoDomScraper = scraper()
        result: List[Estate] = sc.parse_site()

        assert "test_url_estate_1" in result[0].url
        assert "test_price_2" in result[1].details.price
        assert len(result) == 2
