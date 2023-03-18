from typing import Any, Dict, List

from config.config_handler import ParametersHandler
from data_types.estate import Estate
from scraper.otodom_scraper import OtoDomScraper

if __name__ == "__main__":

    PARAMS: Dict[str, Any] = ParametersHandler().get_params()
    scraper: OtoDomScraper = OtoDomScraper()

    estates: List[Estate] = scraper.parse_site()
    scraper.save_data(
        temp_path=PARAMS["results_file"], to_write=estates
    )
