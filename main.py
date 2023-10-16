from asyncio import CancelledError, create_task
from ctypes.wintypes import MSG
from telegram_obj import *
from pyrogram import filters, idle, Client
import pyromod.listen
from loggers import *
from pyrogram.types import Message
from _utils import *
import shutil
from make_acc import *
from smsactivateru import *
import time
import traceback
from users_sql import add_user_, is_users_sudo
from pyrogram.raw.functions import Ping

bot_client = Client("project-sru", api_id=api_id, api_hash=api_hash, bot_token=BOT_TOKEN)

async def run_bot():
    logging.info("Starting Bot :: Please Wait.")
    await bot_client.start()
    logging.info("Bot Started :: Idling.")
    await idle()

tasks = {}

@bot_client.on_message(filters.command("start", ["!", "/"]))
async def pin_g(c: Client, m):
    s = time.perf_counter()
    await c.send(Ping(ping_id=c.rnd_id()))
    en = f"<b>Took</b> - <code>{round((time.perf_counter() - s), 2)}ms</code>!"
    await m.reply(en)

@bot_client.on_message(filters.command("add", ["!", "/"]))
async def add_user(c: Client, m: Message):
    _m = await m.reply("Please Wait..")
    if m.from_user.id != OWNER_ID:
        if not (await is_users_sudo(m.from_user.id)): 
            return await _m.edit("<b>[ACCESS_DENIED]:</b> <code>You are not my owner.</code>")
    if m.reply_to_message and m.reply_to_message.from_user:
        if not await is_users_sudo(m.reply_to_message.from_user.id):
            await add_user_(m.reply_to_message.from_user.id)
            return await _m.edit("Added this user to database.")
        return await _m.edit("User already in database.")
    input_user = await m.from_user.ask("Enter User ID Of the user :")
    await input_user.request.delete()
    if not input_user.text:
        return await _m.edit("No text Found!")
    if input_user.text.startswith("@"):
        try:
            user_id = (await c.get_users(input_user.text)).id
        except Exception as e:
            return await _m.edit("User ID not found in bot cache. please start the bot using that account.")
    elif not str(input_user.text).isdigit():
        return await _m.edit("I need ID not str!")
    user_id = int(input_user.text)
    if await is_users_sudo(user_id):
        return await _m.edit("User already in database.")
    await add_user_(user_id)
    return await _m.edit("Added this user to database.")

@bot_client.on_message(filters.command("run", ["/","!"]))
async def st_(c, m: Message):
    no_of_accounts = 0
    _m = await m.reply("PROCESSING..")
    if m.from_user.id != OWNER_ID:
        if not (await is_users_sudo(m.from_user.id)): 
            return await _m.edit("<b>[ACCESS_DENIED]:</b> <code>You are not my owner.</code>")
    api_key = await m.from_user.ask("Please Enter your API Key :")
    await api_key.delete()
    await api_key.request.delete()
    if not api_key.text:
        return await _m.edit("<b>[API_KEY_MISSING]:</b> <code>You need to give me an api key </code>")
    wrapper = Sms(api_key.text)
    try:
        balance = GetBalance().request(wrapper)
    except Exception as e:
        return await _m.edit(f"<b>[API_KEY_ERROR]:</b> <code>{e.args[1]} - Unable to get balance. check your api key please!</code>")
    await _m.edit(
        f"<b>[API_KEY_OK]:</b> <code>Your Balance is :</code> <code>{balance}</code>"
    )
    country_ = await m.from_user.ask("Enter Country Code :")
    await country_.delete()
    await country_.request.delete()
    if not country_.text:
        return await _m.edit("<b>[COUNTRY_CODE_MISSING]:</b> <code>No country Selected. </code>")
    if not str(country_.text).isdigit():
        return await _m.edit("<b>[COUNTRY_CODE_ERROR]:</b> <code>Country Code must be a digit.</code>")
    if int(country_.text) > 187:
        return await _m.edit("<b>[COUNTRY_CODE_ERROR]:</b> <code>Country Code must below 187.</code>")
    try:
        price, count = await make_req_get_price(api_key.text, country_.text)
    except Exception as e:
        return await _m.edit(f"<b>[APIERROR] :</b> <code>{e}</code>")
    if count == 0:
        return await _m.edit("<b>[NO_NUMBER_LEFT] :</b> <code>No numbers left for this region, please choose another region!</code>")
    confirm = await m.from_user.ask(f"<b>Price is:</b> <code>{price}</code> \n<b>Do you wish to continue?</b>\n<b>Send</b> <code>Yes</code>/<code>No</code>")
    await confirm.delete()
    await confirm.request.delete()
    if confirm.text and confirm.text.lower().startswith("n"):
        return await _m.edit("<b>Cancelled. Thank you, visit again!</b>")
    range_ = await m.from_user.ask("<b>How many accounts do you want to make?</b> \n<b>Tip :</b> <code>send 'nolimit' to bypass this: </code>")
    await range_.request.delete()
    await range_.delete()
    range_ = None if ((not range_.text) or (range_.text.lower() == "nolimit") or (not str(range_.text).isdigit())) else int(range_.text)
    proxy_file = await m.from_user.ask("Please send me proxy file, send anything else like any text to bypass this:")
    await proxy_file.request.delete()
    proxy_path = (await proxy_file.download()) if proxy_file.document else None
    await proxy_file.delete()
    proxy_list = (await open_proxy_path(proxy_path)) if proxy_path else None
    dir_ = f"./accounts_{api_key.text}"
    on_ = 0
    while os.path.exists(dir_):
        on_ += 1
        dir_ = f'{dir_}_{on_}'
    dir_ = f'{dir_}/'
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    random_digit = random.randint(0, 9999)
    process_ = create_task(make_accounts(_m, wrapper, country_.text, range_, no_of_accounts, dir_, proxy_list))
    tasks[random_digit] = process_
    m_k = await m.reply(f"<b>[PROCESS_STARTED]:</b> <code>Process Started. </code>\n<b>[PROCESS_ID]:</b> <code>{random_digit}</code>")
    try:
        no_of_accounts = await process_
    except CancelledError: # task cancelled by user
        pass
    except Exception as e:
        logging.error(traceback.format_exc()) 
        return await m_k.edit(f"<b>[PROCESS_FAILED] :</b> <b>Exception :</b> <code>{e}</code>")
    if no_of_accounts == 0:
        return await m_k.edit("<b>[PROCESS_FAILED] :</b> <code>No accounts created.</code>")
    await m_k.edit(f"<b>[PROCESS_COMPLETED]:</b> <code>Process Completed. </code>\n<b>[PROCESS_ID]:</b> <code>{random_digit}</code> \n<b>Accounts Made :</b> <code>{no_of_accounts}</code> \n<i>Sending Zip...</i>")
    make_zip = shutil.make_archive(f"{api_key.text}_clients", "zip", dir_)
    await c.send_document(m.chat.id, make_zip, caption=f"<b>[ZIP_SENT]:</b> <code>Zip Sent. </code>\n<b>[PROCESS_ID]:</b> <code>{random_digit}</code> \n<b>Accounts Made :</b> <code>{no_of_accounts}</code>")
    await m_k.delete()

@bot_client.on_message(filters.command("stop", ["/", "!"]))
async def stop_(c, msg: Message):
    if msg.from_user.id != OWNER_ID:
        if not (await is_users_sudo(msg.from_user.id)): 
            return await msg.reply("<b>[ACCESS_DENIED]:</b> <code>You are not my owner.</code>")
    m = await msg.reply("Please WAIT....")
    process_id = msg.from_user.ask("Please enter process id :")
    await process_id.delete()
    await process_id.request.delete()
    if (not process_id.text) or (not process_id.text.isdigit()):
        return await m.edit("<b>[PROCESS_ID_MISSING]:</b> <code>Process id missing. </code>")
    if process_id not in tasks:
        return await m.edit("<b>[PROCESS_NOT_FOUND]:</b> <code>Process not found.</code>")
    if tasks[process_id].done():
        return await m.edit("<b>[PROCESS_ALREADY_DONE]:</b> <code>Process already done.</code>")
    if tasks[process_id].cancelled():
        return await m.edit("<b>[PROCESS_ALREADY_CANCELLED]:</b> <code>Process already cancelled.</code>")
    tasks[process_id].cancel()
    await m.edit("<b>[PROCESS_STOPPED]:</b> <code>Process Stopped.</code>")
    del tasks[process_id]

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
