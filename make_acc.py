import json
import traceback
from pyrogram.types import Message
from smsactivateru import *
from errors import *
from telegram_obj import *
from _utils import *
import aiohttp


async def make_req_get_price(api_key_, ccode=16):
    url = f'https://api.sms-activate.org/stubs/handler_api.php?api_key={api_key_}&action=getPrices&service=tg&country={ccode}'
    async with aiohttp.ClientSession() as session:
      async with session.post(url) as resp:
          r = await resp.text()
    try:
        json_obj_r = json.loads(r)
    except Exception as e:
        raise APIFAILURE(r) from e
    if json_obj_r.get("status") and json_obj_r.get("status") is False and json_obj_r.get("msg"):
        raise APIFAILURE(json_obj_r['msg'])
    return json_obj_r[ccode]['tg']['cost'], json_obj_r[ccode]['tg']['count']

@run_in_exc
def choose_random_proxy(proxy_list: list):
    if not proxy_list: return None
    if not isinstance(proxy_list, list):
        return None
    proxy_ = random.choice(proxy_list)
    proxy_list.remove(proxy_)
    proxy_host, proxy_port = proxy_.rstrip().rsplit(":", 1)
    if "|" in proxy_port:
        proxy_port, proxy_user, proxy_pass = proxy_port.strip().split("|", 2)
    proxy_dict = dict(hostname=str(proxy_host.strip()), port=int(proxy_port.strip()))
    if proxy_user and proxy_pass:
        proxy_dict["username"] = proxy_user.strip()
        proxy_dict["password"] = proxy_pass.strip()
    return proxy_dict

async def make_accounts(msg: Message, wrapper: Sms, country: str, range_: int = None, nacc=0, cpath=None, proxy_list: list = None):
    proxy_usage = {}
    random_proxy = None
    if proxy_list:
        random_proxy = await choose_random_proxy(proxy_list)
        if random_proxy:
            proxy_usage[random_proxy['hostname']] = 1
    while True:
        if (range_) and (int(nacc) >= int(range_)) and (range_ > 0):
            break
        nacc += 1
        try: activation = GetNumber(service=SmsService().Telegram, country=country, operator=SmsTypes.Operator.any).request(wrapper)
        except Exception as e:
            if e.args[1] == "NO_BALANCE":
                if nacc == 1:
                    raise NOBALANCEERROR(
                        "No Balance Left, Please check your balance. and try again later!"
                    ) from e
                nacc -= 1
                break
            elif e.args[1] == "NO_NUMBERS":
                if nacc == 1:
                    raise NONUMBERERROR(
                        "No Numbers Available, Please check your balance. and try again later!"
                    ) from e
                nacc -= 1
                break
            else:
                raise e from e
        phone_number = f"+{str(activation.phone_number)}"
        tg_server_ = TG_SERVER(phone_number)
        if (proxy_list and proxy_usage and random_proxy and (proxy_usage.get(random_proxy.get("hostname")))) and (proxy_usage[random_proxy['hostname']] >= 3):
                proxy_usage.clear() 
                logging.info(f"Rotating Proxy : {random_proxy['hostname']}.")
                random_proxy = await choose_random_proxy(proxy_list)
                proxy_usage[random_proxy['hostname']] = 1
        if (
            proxy_list
            and proxy_usage
            and random_proxy
            and (proxy_usage.get(random_proxy.get("hostname")))
        ) and (proxy_usage[random_proxy['hostname']] < 3):
            logging.info(f"Using Proxy Hostname : {random_proxy['hostname']} for {proxy_usage[random_proxy['hostname']]}")
            proxy_usage[random_proxy['hostname']] += 1
        code_obj, client_, c_name = await tg_server_.send_otp(cpath, random_proxy)
        if not code_obj:
            nacc -= 1
            await cancel(activation, c_name)
            continue
        activation.was_sent()
        try: code = activation.wait_code(wrapper=wrapper, timeout=1200)
        except Exception as e:
            nacc -= 1
            await cancel(activation, c_name)
            logging.error("OTP_TIMEOUT: Waited for 120s, no otp recieved.")
            continue
        await asyncio.sleep(5)
        try:
            await tg_server_.login(code, client_, code_obj)
        except Exception:
            nacc -= 1
            await cancel(activation, c_name)
            logging.error(traceback.format_exc())
            continue
        await msg.edit(f"<code>Account {nacc} Created!</code>")
        await asyncio.sleep(10)
    return nacc
