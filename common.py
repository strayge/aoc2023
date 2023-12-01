import os
import httpx
from dotenv import load_dotenv
from IPython.display import display, Markdown
import parsel


def get_session() -> str:
    load_dotenv()
    return os.environ['AOC_SESSION']


def get_input(day: int) -> str:
    url = f'https://adventofcode.com/2023/day/{day}/input'
    r = httpx.get(url, cookies={'session': get_session()})
    assert r.status_code == 200, f'{r.status_code}: {r.text}'
    return r.text


def get_input_lines(day: int) -> list[str]:
    return get_input(day).splitlines()


def get_task(day: int, part: int) -> str:
    url = f'https://adventofcode.com/2023/day/{day}'
    r = httpx.get(url, cookies={'session': get_session()})
    assert r.status_code == 200, f'{r.status_code}: {r.text}'
    selector = parsel.Selector(r.text)
    task = selector.xpath('//article[@class="day-desc"]').getall()
    return task[part - 1]


def get_day_status(day: int) -> str:
    url = f'https://adventofcode.com/2023/day/{day}'
    r = httpx.get(url, cookies={'session': get_session()})
    assert r.status_code == 200, f'{r.status_code}: {r.text}'
    selector = parsel.Selector(r.text)
    return selector.xpath('//main//p[@class="day-success"]//text()').get()


def show_md(md: str) -> None:
    display(Markdown(md))


def show_task(day: int, part: int = 1) -> None:
    show_md(get_task(day, part))


def send_result(day: int, part: int, answer: str) -> str:
    url = f'https://adventofcode.com/2023/day/{day}/answer'
    data = {
        'level': part,
        'answer': answer,
    }
    r = httpx.post(url, cookies={'session': get_session()}, data=data)
    assert r.status_code == 200, f'{r.status_code}: {r.text}'

    text = r.text
    text = text.split("If you're stuck, make sure you're using the full input data; there are also", 1)[0]
    text = text.split('You can <span class="share"', 1)[0]
    selector = parsel.Selector(text)

    message_lines = selector.xpath('//main//article//p//text()').getall()
    message = ''.join(message_lines)
    return message.strip()
