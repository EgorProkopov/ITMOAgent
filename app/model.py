import re
import requests
from omegaconf import OmegaConf
import logging

from typing import Optional, Tuple, Dict

from app.search import SearchEngine


class ChatModel:
    def __init__(self, config, logger):
        self.name = config['api']['model_name']

        self.api_url = config['api']['url']
        self.headers = {"Authorization": f"Bearer {config['api']['key']}"}

        self.system_prompt = config['api']['system_prompt']

        self.logger = logger

        self.search_engine = SearchEngine(config)

    def get_additional_sources(self, query):
        extracted_data = self.search_engine.search_and_scrape(query)
        urls = []
        additional_text = "Дополнительная информация:\n"
        for data in extracted_data:
            urls.append(data['url'])
            additional_text += data['text'] + "\n"

        return additional_text, urls


    def generate_response(self, query: str):
        '''
        Отправляет запрос к API HF и получает ответ.
        '''
        additional_text, urls = self.get_additional_sources(query)

        payload = {"inputs": self.system_prompt + "\n" + query + "\n" + additional_text}

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            response_json = response.json()

            if isinstance(response_json, list) and "generated_text" in response_json[0]:
                return response_json[0]["generated_text"], urls
            elif isinstance(response_json, dict) and "generated_text" in response_json:
                return response_json["generated_text"], urls
            else:
                self.logger.error(f"Непредвиденный формат ответа: {response_json}")
                return "", urls
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка запроса к API: {e}")
            return "", urls

    def clean_response(self, response: str) -> str:
        '''
        Очищение текста от системного промпта.
        '''
        generated_text = response.replace(self.system_prompt, "").strip()
        return generated_text

    def extract_answer_and_reasoning(self, generated_text: str) -> Tuple[Optional[int], str]:
        '''
        Извлечение номера правильного ответа и рассуждения из сгенерированного текста.
        Формат ответа:
          - "Правильный ответ: X"
          - "Рассуждения: ..."
        '''
        answer_match = re.search(r"Правильный ответ:\s*(\d+)", generated_text)
        reasoning_match = re.search(r"Рассуждения:\s*(.*)", generated_text, re.DOTALL)

        answer = int(answer_match.group(1)) if answer_match else None
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return answer, reasoning

    def form_answer(self, answer_num: int, reasoning: str, urls) -> Dict:
        '''
        Формирование ответа в формате JSON
        '''
        json_answer =  {
            "answer": answer_num,
            "reasoning": reasoning,
            "sources": urls
        }
        if answer_num == 0:
            json_answer['answer'] = "null"

        return json_answer

    def reasoning_header(self) -> str:
        '''
        По условию задания бот должен сообщать, какой моделью сгененирован ответ
        '''
        header = f"Ответ сгененирован моделью {self.name}. "
        return header

    def get_answer(self, query: str) -> dict:
        '''
        Полный пайплайн ответа
        '''

        response, urls = self.generate_response(query)
        generated_text = self.clean_response(response)
        answer_num, reasoning = self.extract_answer_and_reasoning(generated_text)
        reasoning = self.reasoning_header() + reasoning
        json_answer = self.form_answer(answer_num, reasoning, urls)
        return json_answer


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    config = OmegaConf.load('configs/main_config.yaml')
    model = ChatModel(config, logger)

    # query = "В каком году Университет ИТМО был включён в число Национальных исследовательских университетов России?\n1. 2007\n2. 2009\n3. 2011\n4. 2015"

    query = "В каком году Университет ИТМО был включён в число Национальных исследовательских университетов России?\n1. 2008\n2. 2010\n3. 2011\n4. 2015"
    response, urls = model.generate_response(query)
    generated_text = model.clean_response(response)
    # print(generated_text)
    # print(model.extract_answer_and_reasoning(generated_text))
    print(model.get_answer(query))


