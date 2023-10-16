import asyncio
from pyrogram import Client
from pyrogram.types import User, TermsOfService
from pyrogram.errors import FloodWait
from config import *
from pyrogram.errors import RPCError
from _utils import gen_random_name, gen_random_pic, gen_random_device, gen_random_sys_version, gen_random_app_version
from pyrogram.errors.exceptions.bad_request_400 import PhoneNumberBanned
import logging
import traceback
import random

class TG_SERVER:
    def __init__(self, phone_number) -> None:
        self.phone_number = phone_number

    async def send_otp(self, custom_path=None, proxy_dict=None):
        phone_number = self.phone_number
        client_name = f'{phone_number}_client_'
        s = random.choice([1, 2])
        if s == 2:
            APP_CONFIG_API_ID = 4
            APP_CONFIG_API_HASH = "014b35b6184100b085b0d0572f9b5103"
        else:
            APP_CONFIG_API_HASH = api_id
            APP_CONFIG_API_HASH = api_hash
        if custom_path:
            client_name = custom_path + client_name
        if proxy_dict:
            logging.info(f"Using Proxies : {proxy_dict['hostname']}:{proxy_dict['port']}")
            app = Client(
                client_name,
                api_id=int(APP_CONFIG_API_ID),
                api_hash=str(APP_CONFIG_API_HASH),
                force_sms=True,
                no_updates=True,
                device_model=(await gen_random_device()),
                app_version=(await gen_random_app_version()),
                system_version=(await gen_random_sys_version()),
                proxy=proxy_dict
            )
        else:
            logging.info("Not Using Any Proxy!")
            app = Client(
                client_name,
                api_id=int(APP_CONFIG_API_ID),
                api_hash=str(APP_CONFIG_API_HASH),
                force_sms=True,
                no_updates=True,
                device_model=(await gen_random_device()),
                app_version=(await gen_random_app_version()),
                system_version=(await gen_random_sys_version()),
            )
        try:
            await app.connect()
        except ConnectionError:
            await app.disconnect()
            await app.connect()
        try:
            sent_code = await app.send_code(phone_number)
            logging.info("Code sent.")
        except PhoneNumberBanned:
            logging.info("Phone number banned.")
            await app.log_out()
            return False, None, client_name
        if sent_code.type != "sms":
            await app.log_out()
            logging.info(f"Code sent as : {sent_code}. ")
            return False, None, client_name
        return sent_code, app, client_name
    
    async def login(self, code, app: Client, code_obj):
        phone_number = self.phone_number
        first_name_ = await gen_random_name()
        random_photo = await gen_random_pic()
        signed_up_done = False
        await asyncio.sleep(10)
        signed_in = await app.sign_in(phone_number, code_obj.phone_code_hash, code)
        if isinstance(signed_in, User):
            await app.disconnect()
            return signed_in
        await asyncio.sleep(10)
        while not signed_up_done:
            try:
                logging.info("Signing UP.")
                signed_up_done = await app.sign_up(
                    phone_number,
                    code_obj.phone_code_hash,
                    first_name_
                )
                await asyncio.sleep(10)
                if isinstance(signed_in, TermsOfService):
                    logging.info("Accepting TERMS of Service.")
                    await app.accept_terms_of_service(signed_in.id)
                    await asyncio.sleep(10)
                if random_photo:
                    try: await app.set_profile_photo(photo=random_photo)
                    except BaseException: pass
                    await asyncio.sleep(10)
                    try: await app.enable_cloud_password(9999, hint="10,000-1=?")
                    except ValueError: pass
                    await asyncio.sleep(10)
                await app.disconnect()
                return signed_up_done    
            except FloodWait as e:
                logging.info(f"Sleeping for {e.x + 3} seconds, to retry.")
                await asyncio.sleep(e.x + 3)
            
