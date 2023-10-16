import random
from pyrogram.types import Message
from typing import Union
import os
from faker import Faker
from config import RANDOM_NAME_TEXT_FILE, IMG_PROFILE_PATH
import glob
import logging
from smsactivateru import *
from errors import *
import multiprocessing
from functools import wraps
from concurrent.futures.thread import ThreadPoolExecutor
import asyncio

executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5)


def run_in_exc(func_):
    @wraps(func_)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, lambda: func_(*args, **kwargs))

    return wrapper


all_names = []
profile_pics = []


def walk_dir(path):
    path = f'{path}*'
    return [
        (i) for i in glob.iglob(path) if (i.endswith((".png", ".jpg", ".jpeg")))
    ]

if os.path.exists(RANDOM_NAME_TEXT_FILE):
    all_names = open(RANDOM_NAME_TEXT_FILE, "r").readlines()
if os.path.exists(IMG_PROFILE_PATH):
    profile_pics = walk_dir(IMG_PROFILE_PATH)

def get_text(message: Message) -> Union[str, None]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None

@run_in_exc
def gen_random_name():
    if all_names:
        firstname = random.choice(all_names)
        all_names.remove(firstname)
    else:
        fake = Faker()
        firstname = fake.name()
    return firstname

@run_in_exc
def gen_random_pic():
    if profile_pics:
        random_profile = random.choice(profile_pics)
        profile_pics.remove(random_profile)
        return random_profile
    return None

@run_in_exc
def remove_session(session_path):
    session_path = f'{session_path}.session'
    if os.path.exists(session_path):
        return os.remove(session_path)


async def cancel(activation, c_name):
    activation.mark_as_used()
    try:
        activation.cancel()
    except Exception:
        pass
    logging.info("Maked as used and canceled process..")

@run_in_exc
def open_proxy_path(file_path: str):
    if not file_path.endswith((".txt", ".text")): return None
    with open(file_path, "r") as f:
        proxy_ = f.readlines()
        if not proxy_:
            return None
    return proxy_


and_devices = ["XIAOMI Redmi Note 8",
               "XIAOMI Redmi Note 9 Pro 5G",
               "XIAOMI Redmi 9A",
               "POCO POCO M3",
               "LG LG-P990",
               "HTC Pyramid",
               "ASUS TF101",
               "ASUS ME302C",
               "SAMSUNG GT-I9305",
               "OPPO A31",
               "XIAOMI Redmi Note 11S",
               "NOKIA C20+",
               "XIAOMI Redmi 10 Prime", 
               "XIAOMI Redmi 6A",
               "XIAOMI Redmi 10 Note",
               ]

@run_in_exc
def gen_random_device():
    return random.choice(and_devices)

@run_in_exc
def gen_random_sys_version():
    return "Android " + "10." + str(random.randint(1, 9))

@run_in_exc
def gen_random_app_version():
    return f"Telegram Android 8.{str(random.randint(5, 6))}." + str(
        random.randint(3, 6)
    ) 