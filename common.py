import os
import time
import httpx
from dotenv import load_dotenv
from IPython.display import display, Markdown
import parsel

TIMES: dict[tuple[int, int, str], float] = {}


def save_time(day: int, part: int, action: str, override: bool = False) -> None:
    key = (day, part, action)
    if key not in TIMES or override:
        TIMES[(day, part, action)] = time.time()


def show_time(day: int, part: int, action1: str, action2: str) -> str:
    key1 = (day, part, action1)
    key2 = (day, part, action2)
    time1 = TIMES[key1]
    time2 = TIMES[key2]
    diff = time2 - time1
    minutes = int(diff // 60)
    seconds = int(diff % 60)
    return f'{minutes:02}:{seconds:02}'


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
    save_time(day, part, 'task')
    selector = parsel.Selector(r.text)
    task = selector.xpath('//article[@class="day-desc"]').getall()
    return task[part - 1]


def get_test_input(day: int, part: int = 1) -> str:
    task = get_task(day, part)
    selector = parsel.Selector(task)
    pre_values = selector.xpath('//pre//text()').getall()
    pre_longest = max(pre_values, key=len)
    return pre_longest


def get_test_input_lines(day: int, part: int = 1) -> list[str]:
    return get_test_input(day, part).splitlines()


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
    save_time(day, part, 'send', override=True)

    text = r.text
    text = text.split("If you're stuck, make sure you're using the full input data; there are also", 1)[0]
    text = text.split('You can <span class="share"', 1)[0]
    selector = parsel.Selector(text)

    message_lines = selector.xpath('//main//article//p//text()').getall()
    message = ''.join(message_lines)
    message = message.strip()

    full_time = show_time(day, part, 'task', 'send')
    return message + f' (solved in {full_time})'
