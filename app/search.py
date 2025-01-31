import re
import requests
from bs4 import BeautifulSoup
import duckduckgo_search
from duckduckgo_search import exceptions as ddg_exceptions
from omegaconf import OmegaConf


class SearchEngine:
    def __init__(self, config):
        self.num_cites = config['search']['num_cites']
        self.num_paragraphs = config['search']['num_paragraphs']

    def search_duckduckgo(self, query: str):
        '''
        Запрос по DuckDuckGo API
        '''
        try:
            with duckduckgo_search.DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.num_cites))
            return results[:self.num_cites] if results else []
        except ddg_exceptions.DuckDuckGoSearchException:
            # У DDGS есть ограничение на количество запросов
            return []


    def extract_text_from_url(self, url: str):
        '''
        Извлечение текста из страницы
        '''
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n\n".join(p.text.strip() for p in paragraphs[:self.num_paragraphs])
            return text if text else "Нет дополнительной информации"
        except requests.exceptions.RequestException:
            return "Ошибка загрузки страницы"

    def clean_text(self, text: str):
        '''
        Очистка текста. Для лучшего понимания текста, стоит удалить все спец символы
        '''
        text = re.sub(r'\s+', ' ', text)  # Убираем лишние пробелы и переносы строк
        text = re.sub(r'\[\d+\]', '', text)  # Удаляем ссылки в виде [число]
        return text.strip()

    def search_and_scrape(self, query: str):
        '''
        Получение информации из интернета по запросу
        '''
        results = self.search_duckduckgo(query)

        extracted_data = []
        for result in results:
            url = result["href"]
            snippet = self.extract_text_from_url(url)
            snippet = self.clean_text(snippet)
            extracted_data.append({ "url": url, "text": snippet})

        return extracted_data


if __name__ == "__main__":
    config = OmegaConf.load('configs/main_config.yaml')
    search_engine = SearchEngine(config)

    query = "В каком году Университет ИТМО был включён в число Национальных исследовательских университетов России?\n1. 2008\n2. 2009\n3. 2011\n4. 2015"
    extracted_data = search_engine.search_and_scrape(query)

    print(extracted_data)