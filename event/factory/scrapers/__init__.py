
from ..scrapers.luma_scaper import LumaEventScraper


class Scrapper:
    def __init__(self, event_url, scrapper='luma'):
        if scrapper == 'luma':
            self.scrapper = LumaEventScraper(event_url)

        else:
            self.engine = None

    def run(self):
        if self.scrapper and hasattr(self.scrapper, 'run'):
            return self.scrapper.run()
        else:
            raise NotImplementedError(
                f"Scrapper {self.scrapper} does not have a run method.")
