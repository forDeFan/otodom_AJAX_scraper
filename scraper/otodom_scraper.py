import json
import logging
import time
from time import sleep
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from requests import Response
from requests.adapters import HTTPAdapter
from requests.sessions import Session
from tenacity import retry
from tenacity.wait import wait_exponential
from urllib3.util import Retry

from config.config_handler import ParametersHandler
from data_types.estate import Estate
from data_types.estate_details import EstateDetails

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(message)s"
)


class OtoDomScraper:
    PARAMS: Dict[str, Any] = ParametersHandler().get_params()

    def __init__(self) -> None:
        self.session: Session = self._init_session()
        # For script execution time probing
        self.time_start: float = time.time()
        self.time_stop: float

    def _init_session(self) -> Session:
        """
        Start session per single requests instance.
        """
        session: Session = Session()
        retries: Retry = Retry(
            connect=self.PARAMS["retry"]["connect"],
            read=self.PARAMS["retry"]["read"],
            redirect=self.PARAMS["retry"]["read"],
        )

        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update({"User-agent": self.PARAMS["agent"]})

        return session

    def construct_url_for_listing(self, page: str):
        search_base_url: str = f"{self.PARAMS['search_base_url']}"
        offering_type: str = f"{self.PARAMS['offering_type']}/"
        estate_type: str = f"{self.PARAMS['estate_type']}/"
        city: str = f"{self.PARAMS['city']}/"
        district: str = f"{self.PARAMS['district']}?"
        radius: str = (
            f"{self.PARAMS['radius']}={self.PARAMS['radius_value']}&"
        )
        page: str = f"{self.PARAMS['pagination']}={str(page)}&"
        max_listing_links: str = (
            f"limit={self.PARAMS['max_listing_links']}&"
        )
        price_min: str = f"{self.PARAMS['price_min']}={self.PARAMS['price_min_value']}&"
        price_max: str = f"{self.PARAMS['price_max']}={self.PARAMS['price_max_value']}&"
        area_min: str = f"{self.PARAMS['area_min']}={self.PARAMS['area_min_value']}&"
        area_max: str = f"{self.PARAMS['area_max']}={self.PARAMS['area_max_value']}&"
        suffix_url: str = f"{self.PARAMS['suffix_url']}"

        constructed_url: str = (
            search_base_url
            + offering_type
            + estate_type
            + city
            + district
            + radius
            + page
            + max_listing_links
            + price_min
            + price_max
            + area_min
            + area_max
            + suffix_url
        )

        return constructed_url

    @retry(wait=wait_exponential(multiplier=1, min=2, max=5))
    def get_listing_page_soup(self, page_no: int) -> BeautifulSoup:

        constructed_url: str = self.construct_url_for_listing(
            page=page_no
        )
        logging.info(msg="Search url " + constructed_url)

        with self.session as s:
            page_source: Response = s.get(url=constructed_url)
            soup = BeautifulSoup(page_source.text, "html.parser")

        return soup

    @retry(wait=wait_exponential(multiplier=1, min=2, max=5))
    def get_estate_page_soup(self, estate_url: str) -> BeautifulSoup:

        with self.session as s:
            page_source: Response = s.get(estate_url)
            soup: BeautifulSoup = BeautifulSoup(
                page_source.text, "html.parser"
            )

            return soup

    def get_estate_links_from_listing(
        self, listing_soup: BeautifulSoup
    ) -> List[str]:

        script: str = listing_soup.find(id="__NEXT_DATA__").text
        script_json: str = json.loads(script)
        script_json_estates: str = script_json["props"]["pageProps"][
            "data"
        ]["searchAds"]["items"]

        estate_urls: List[str] = []

        for elem in script_json_estates:
            estate_urls.append(
                self.PARAMS["result_base_url"] + elem["slug"]
            )

        return estate_urls

    def get_estate_details(
        self, estate_soup: BeautifulSoup
    ) -> List[str]:

        script: str = estate_soup.find(id="__NEXT_DATA__").text
        script_json: Dict[str, str] = json.loads(script)
        script_json_details: str = script_json["props"]["pageProps"][
            "ad"
        ]

        price: str = script_json_details["characteristics"][0]["value"]
        size: str = script_json_details["characteristics"][1]["value"]
        location: str = script_json_details["target"]["City"]
        description: str = script_json_details["description"]

        estate_details: List[str] = []

        for i in [price, size, location, description]:
            estate_details.append(i)

        return estate_details

    def parse_estate(self, estate_url: str) -> EstateDetails:

        soup: BeautifulSoup = self.get_estate_page_soup(
            estate_url=estate_url
        )
        estate_details: List[str] = self.get_estate_details(
            estate_soup=soup
        )

        return EstateDetails(
            price=estate_details[0],
            size=estate_details[1],
            location=estate_details[2],
            description=estate_details[3],
        )

    def parse_page(self, listing_soup: BeautifulSoup) -> List[Estate]:

        estate_results = self.get_estate_links_from_listing(
            listing_soup=listing_soup
        )

        estates: List[Estate] = []

        for link in estate_results:

            estate_details: EstateDetails = self.parse_estate(
                estate_url=link
            )

            if not estate_details:
                continue

            # To prevent server overload
            sleep(self.PARAMS["sleep_time"])

            estate: Estate = Estate(
                url=link,
                details=estate_details,
            )

            if self.PARAMS["verbose_logging"]:
                logging.info(f"New entry parsed:\n{estate.url}")

            estates.append(estate)

        return estates

    def parse_site(self) -> List[Estate]:

        if self.PARAMS["verbose_logging"]:
            logging.info("## Scraper started ##")

        first_page_soup: BeautifulSoup = self.get_listing_page_soup(
            page_no=1
        )
        page_results: List[Estate] = self.parse_page(
            listing_soup=first_page_soup
        )
        results: List[Estate] = page_results

        page_num: int = 2
        while len(page_results) > 0:
            if (
                self.PARAMS["page_limit"]
                and page_num >= self.PARAMS["page_limit"]
            ):
                break

            logging.info(
                msg=f"### Start parsing next page (no: {page_num}) ###"
            )

            page_soup: BeautifulSoup = self.get_listing_page_soup(
                page_no=page_num
            )
            page_results: List[Estate] = self.parse_page(
                listing_soup=page_soup
            )
            page_num += 1

            if page_results:
                results.extend(page_results)

        # For script execution time probing
        self.time_stop = time.time()

        if self.PARAMS["verbose_logging"]:
            logging.info(
                msg=f"## Scraper finished ##\n# Execution time "
                + str(self.time_stop - self.time_start)
                + " seconds #"
            )

        return results

    def save_data(self, temp_path: str, to_write: Any) -> None:
        """
        Save results to specified file in temp_path specified path - if just filename without path provided,
        it will be saved in project root.
        """
        with open(temp_path, "w+", encoding="utf-8") as f:
            for line in to_write:
                f.write(str(line))
                f.write("\n")
