#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#   👑 NM.CDX SQUAD BOT — PREMIUM EDITION (ALL FIXED) 👑
#   ✅ Auto Update · Auto Emote · Auto Animation · Dual Recruit
#   ✅ Web Account Manager · Stop All · Auto Kick · Welcome FIXED
# ═══════════════════════════════════════════════════════════════════

import subprocess, sys, importlib, os, ssl, json, time, random, asyncio, threading, gc, re, struct, base64
from collections import deque
from datetime import datetime
import gzip, http.client, uuid, requests, urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import aiohttp, jwt
from rich.console import Console
from rich.panel import Panel
from cfonts import render
from protobuf_decoder.protobuf_decoder import Parser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console()

# ========== BUFFER LOG LIVE ==========
log_buffer = deque(maxlen=500)
log_lock = threading.Lock()
_orig_console_print = console.print

def _patched_console_print(*args, **kwargs):
    try: _orig_console_print(*args, **kwargs)
    except Exception: pass
    try:
        text = " ".join(str(a) for a in args)
        text = re.sub(r'\[/?[a-zA-Z0-9_#= ]+\]', '', text)
        ts = datetime.now().strftime("%H:%M:%S")
        with log_lock: log_buffer.append(f"[{ts}] {text}")
    except Exception: pass

console.print = _patched_console_print

# ================================================================
#   AUTO UPDATE
# ================================================================
try:
    from google_play_scraper import app as _gps_app
    _GPS_AVAILABLE = True
except Exception:
    _GPS_AVAILABLE = False
    console.print("[bold yellow]⚠ google-play-scraper belum dipasang[/bold yellow]")

DYNAMIC_SERVER_URL = CURRENT_OB = FREEFIRE_VERSION_NAME = STORE_VERSION = DYNAMIC_CLIENT_URL = login_url = ob = version = ""

def AuToUpDaTE(max_retries: int = 6, retry_delay: int = 5):
    if not _GPS_AVAILABLE:
        console.print("[bold red]❌ google-play-scraper tidak ditemukan![/bold red]"); sys.exit(1)
    for attempt in range(1, max_retries + 1):
        try:
            console.print(f"[cyan]🌐 [{attempt}/{max_retries}] Mengambil versi terbaru...[/cyan]")
            data = _gps_app('com.dts.freefireth', lang="fr", country='CA')
            store_version = data.get("version")
            if not store_version: raise RuntimeError("Versi store kosong")
            api_url = f"https://version.ggwhitehawk.com/live/ver.php?version={store_version}&lang=fr&device=android&channel=android"
            r = requests.get(api_url, timeout=20)
            if r.status_code != 200: raise RuntimeError(f"HTTP {r.status_code}")
            j = r.json()
            su, obv, rp = j.get('server_url'), j.get('latest_release_version'), j.get('remote_version')
            missing = [n for n, v in [("server_url", su), ("ob", obv), ("remote", rp)] if not v]
            if missing: raise RuntimeError(f"Hilang: {missing}")
            return str(su).strip(), str(obv).strip(), str(rp).strip(), str(store_version).strip()
        except Exception as e:
            console.print(f"[bold yellow]⚠ Percobaan {attempt} gagal: {e}[/bold yellow]")
            if attempt < max_retries: time.sleep(retry_delay)
            else: console.print("[bold red]❌ Semua percobaan gagal[/bold red]"); sys.exit(1)

_tmp = AuToUpDaTE()
DYNAMIC_SERVER_URL    = _tmp[0].rstrip('/')
CURRENT_OB            = _tmp[1]
FREEFIRE_VERSION_NAME = _tmp[2]
STORE_VERSION         = _tmp[3]
login_url = DYNAMIC_SERVER_URL
ob = CURRENT_OB
version = FREEFIRE_VERSION_NAME
DYNAMIC_CLIENT_URL = DYNAMIC_SERVER_URL.replace("loginbp", "clientbp")

if not all([DYNAMIC_SERVER_URL, CURRENT_OB, FREEFIRE_VERSION_NAME, STORE_VERSION]):
    console.print("[bold red]❌ Kritis: Data live hilang![/bold red]"); sys.exit(1)

console.print(f"""
[bold green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 DATA LIVE DIMUAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 OB         : [white]{CURRENT_OB}[/white]
🛒 Versi Store: [white]{STORE_VERSION}[/white]
🎮 Versi Game : [white]{FREEFIRE_VERSION_NAME}[/white]
🌐 Server     : [white]{DYNAMIC_SERVER_URL}[/white]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

TIMEOUT = aiohttp.ClientTimeout(total=30)
WEB_CONFIG_FILE = "web_config.json"
ACCOUNTS_FILE = "accounts.txt"

# ================================================================
#   SISTEM EQUIP EMOTE
# ================================================================
EMOTE_DATA_HEX = "CA F6 83 22 2A 25 C7 BE FE B5 1F 59 54 4D B3 13"
EMOTE_BINARY = bytes.fromhex(EMOTE_DATA_HEX.replace(" ", ""))
REGION_SERVER_MAP = {
    "BD": DYNAMIC_CLIENT_URL, "IND": "https://client.ind.freefiremobile.com",
    "PK": DYNAMIC_CLIENT_URL, "ME": DYNAMIC_CLIENT_URL, "VN": DYNAMIC_CLIENT_URL,
    "SG": DYNAMIC_CLIENT_URL, "ID": DYNAMIC_CLIENT_URL, "TH": DYNAMIC_CLIENT_URL,
    "BR": "https://client.us.freefiremobile.com", "NA": "https://client.us.freefiremobile.com",
    "US": "https://client.us.freefiremobile.com", "RU": DYNAMIC_CLIENT_URL,
}
console.print(f"[green]✅ Server Region Sinkron: {DYNAMIC_CLIENT_URL}[/green]")

def decode_jwt_noverify(token: str):
    try:
        parts = token.split(".")
        if len(parts) < 2: return None
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_b64).decode())
    except Exception: return None

async def equip_emote_on_login(jwt_token, logger=None):
    log = logger or console.print
    try:
        payload = decode_jwt_noverify(jwt_token)
        if not payload: log("[red]❌ Equip Emote: JWT tidak valid[/red]"); return
        region_code = payload.get("noti_region") or payload.get("lock_region")
        if not region_code: log("[red]❌ Equip Emote: Region tidak ditemukan[/red]"); return
        base_url = REGION_SERVER_MAP.get(region_code.upper())
        if not base_url: log(f"[red]❌ Equip Emote: Tidak ada mapping untuk {region_code}[/red]"); return
        url = f"{base_url}/ChooseEmote"
        headers = {
            "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {jwt_token}",
            "ReleaseVersion": CURRENT_OB,
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
            "X-GA": "v1 1",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=EMOTE_BINARY, ssl=False, timeout=10) as resp:
                if resp.status == 200: log(f"[bold green]✅ Equip Emote OK ({region_code})[/bold green]")
                else: log(f"[bold yellow]⚠ Equip Emote Gagal ({resp.status})[/bold yellow]")
    except Exception as e: log(f"[red]❌ Error Equip Emote: {e}[/red]")

# ========== TRACKING GLOBAL ==========
welcome_tracking = {}
running_bots = set()
running_bots_lock = threading.Lock()
bot_status = {}
bot_lock = threading.Lock()
online_count = 0
total_accounts = 0
active_accounts = []
active_lock = threading.Lock()

# ========== SISTEM SIGNAL ==========
signal_lock = threading.Lock()
_restart_timestamp = 0
_recreate_timestamp = 0
_stop_all_flag = False
_stop_all_lock = threading.Lock()

def trigger_restart_all():
    global _restart_timestamp
    with signal_lock: _restart_timestamp = time.time()

def trigger_recreate_all():
    global _recreate_timestamp
    with signal_lock: _recreate_timestamp = time.time()

def get_restart_timestamp():
    with signal_lock: return _restart_timestamp

def get_recreate_timestamp():
    with signal_lock: return _recreate_timestamp

def set_stop_all(v: bool):
    global _stop_all_flag
    with _stop_all_lock: _stop_all_flag = bool(v)

def is_stopped() -> bool:
    with _stop_all_lock: return _stop_all_flag

# ================================================================
#   EKSTRAKTOR AMAN
# ================================================================
def safe_get_data(f):
    if f is None: return None
    if isinstance(f, dict): return f.get("data")
    return f

def safe_get_int(f, default=None):
    v = safe_get_data(f)
    if v is None: return default
    if isinstance(v, bool): return int(v)
    if isinstance(v, int): return v
    if isinstance(v, (str, bytes, bytearray)):
        try: return int(v)
        except: return default
    return default

def safe_get_str(f, default=""):
    v = safe_get_data(f)
    if v is None: return default
    if isinstance(v, str): return v
    if isinstance(v, (bytes, bytearray)):
        try: return v.decode('utf-8', errors='ignore')
        except: return default
    return str(v)

def safe_dict(f):
    v = safe_get_data(f)
    return v if isinstance(v, dict) else {}

def extract_chat_code(f5d):
    """✅ FIX #2: Ekstrak chat_code dengan benar dari nested dict"""
    for key in ('14', '17', '31', '33', '36', '40'):
        v = f5d.get(key)
        if v is None: continue
        data = v.get('data') if isinstance(v, dict) else v
        if isinstance(data, str) and len(data) > 3:
            return data
        if isinstance(data, dict):
            for kk in ('1', '2', '3', '4'):
                inner = data.get(kk) if kk in data else data.get(int(kk))
                if isinstance(inner, dict) and 'data' in inner:
                    inner = inner['data']
                if isinstance(inner, str) and len(inner) > 3:
                    return inner
    return None

# ================================================================
#   POOL
# ================================================================
AUTO_BUNDLE_POOL = [914000002, 914000003, 914038001, 914039001, 914042001, 914044001, 914047001, 914047002, 914048001, 914050001, 914051001, 914053001]
ANIMATION_POOL = AUTO_BUNDLE_POOL[:]
DEFAULT_JOIN_EMOTES = [909049013, 909045010, 909000020, 909000010, 909055004, 909055005, 909000062]

_last_bundle_time = {}
_BUNDLE_COOLDOWN = 3.0

# ================================================================
#   KONFIG DEFAULT
# ================================================================
DEFAULT_WELCOME_MSG = (
    "[C][FFD700]❖━━━━━━━━━━━━━━━❖\n"
    "[C][FFFFFF]Halo [FF0000]{user_name}\n"
    "[C][00FF7F]Selamat datang di Squad kami! ✨\n"
    "[C][FFD700]❖━━━━━━━━━━━━━━━❖\n"
    "[C][B][00FFFF]🔥 NM.C😶DX AUTOMATION BOT 🔥\n"
    "[C][FFD700]────────────────\n"
    "[C][FFFF00] Ketik [00FF00]/store [FFFF00]untuk lihat item\n"
    "[C][FFFF00] Ketik [00FF00]/app [FFFF00]untuk Android App\n"
    "[C][FFD700]────────────────\n"
    "[C][00BFFF]📢 Telegram : [FFFFFF]@NMC😶DX\n"
    "[C][FF69B4]🎬 TikTok   : [FFFFFF]@NM.C😶DX\n"
    "[C][FFD700]❖━━━━━━━━━━━━━━━❖"
)

DEFAULT_COMMANDS = {
    "/store": {"enabled": True, "match": "contains", "type": "message",
        "response": "[C][FFD700]⚡ TOKO NM.C😶DX ⚡\n[C][00FF00]🤖 TCP BOT: [FFFF00]500 BDT\n[C][00FF00]🌐 Website: [FFFF00]nmc😶dx.xo.je\n[C][00FF00]👤 Owner: [FFFF00]@NMC😶DX"},
    "/app": {"enabled": True, "match": "contains", "type": "message",
        "response": "[C][B][00FFFF]📱 APP NM.C😶DX TCP\n[C][00FF00]https://www.mediafire.com/file/lvykrek51q17hae/NMC😶DX_TCP.apk"},
    "st": {"enabled": True, "match": "exact", "type": "recruit_squad"}
}

# ================================================================
#   KONFIG WEB
# ================================================================
web_config = {
    "squad_size": 4,
    "world_recruit_count": 3,
    "world_recruit_type": "1",
    "squad_lifetime_sec": 5,
    "auto_recreate": True,
    "welcome_msg": DEFAULT_WELCOME_MSG,
    "auto_recruit_on_join": True,
    "auto_recruit_on_leave": True,
    "recruit_delay_sec": 1.5,
    "auto_bundle_on_join": True,
    "bundle_count_on_join": 2,
    "auto_animation": True,
    "animation_interval_sec": 10,
    "auto_emote_on_join": True,
    "emote_join_delay_sec": 0.5,
    "join_emote_pool": DEFAULT_JOIN_EMOTES[:],
    "auto_kick_on_join": False,
    "kick_delay_sec": 1.0,
    "kick_msg": "[B][C][FF0000]🚫 AKSES DITOLAK!\n[FFFFFF]Kamu telah di-kick otomatis.",
    "auto_welcome_on_join": True,
    "welcome_delay_sec": 0.5,
    "bot_self_emote_enabled": False,
    "bot_self_emote_pool": DEFAULT_JOIN_EMOTES[:],
    "bot_self_emote_interval": 8.0,
    "commands": {},
}
web_config_lock = threading.Lock()

def to_json_safe(obj):
    if isinstance(obj, dict): return {str(k): to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list): return [to_json_safe(i) for i in obj]
    if isinstance(obj, (bytes, bytearray)): return {"__hex__": bytes(obj).hex()}
    return obj

def from_json_safe(obj):
    if isinstance(obj, dict):
        if "__hex__" in obj and len(obj) == 1:
            try: return bytes.fromhex(obj["__hex__"])
            except: return b""
        r = {}
        for k, v in obj.items():
            try: key = int(k)
            except: key = k
            r[key] = from_json_safe(v)
        return r
    if isinstance(obj, list): return [from_json_safe(i) for i in obj]
    return obj

def load_web_config():
    try:
        saved = {}
        if os.path.exists(WEB_CONFIG_FILE):
            with open(WEB_CONFIG_FILE, "r", encoding="utf-8") as f: saved = json.load(f)
        with web_config_lock:
            int_fields = {
                "squad_size": (3, 5), "world_recruit_count": (1, 10),
                "squad_lifetime_sec": (5, 3600), "bundle_count_on_join": (1, 5),
                "animation_interval_sec": (5, 300),
            }
            for k, (lo, hi) in int_fields.items():
                v = saved.get(k)
                if isinstance(v, int) and lo <= v <= hi: web_config[k] = v

            float_fields = {
                "recruit_delay_sec": (0.5, 30), "emote_join_delay_sec": (0.1, 30),
                "kick_delay_sec": (0.1, 30), "welcome_delay_sec": (0.1, 30),
                "bot_self_emote_interval": (1, 300),
            }
            for k, (lo, hi) in float_fields.items():
                v = saved.get(k)
                if isinstance(v, (int, float)) and lo <= float(v) <= hi: web_config[k] = float(v)

            wrt = saved.get("world_recruit_type")
            if wrt in ("1", "2", "half", "random"): web_config["world_recruit_type"] = wrt

            bool_fields = [
                "auto_recreate", "auto_recruit_on_join", "auto_recruit_on_leave",
                "auto_bundle_on_join", "auto_animation", "auto_emote_on_join",
                "auto_kick_on_join", "auto_welcome_on_join", "bot_self_emote_enabled"
            ]
            for bf in bool_fields:
                v = saved.get(bf)
                if isinstance(v, bool): web_config[bf] = v

            wm = saved.get("welcome_msg")
            if isinstance(wm, str) and wm: web_config["welcome_msg"] = wm

            km = saved.get("kick_msg")
            if isinstance(km, str) and km: web_config["kick_msg"] = km

            jep = saved.get("join_emote_pool")
            if isinstance(jep, list):
                cleaned = []
                for x in jep:
                    try: cleaned.append(int(x))
                    except: pass
                if cleaned: web_config["join_emote_pool"] = cleaned

            bsep = saved.get("bot_self_emote_pool")
            if isinstance(bsep, list):
                cleaned = []
                for x in bsep:
                    try: cleaned.append(int(x))
                    except: pass
                if cleaned: web_config["bot_self_emote_pool"] = cleaned

            cmds_saved = saved.get("commands", {})
            commands = {}
            for name, default_val in DEFAULT_COMMANDS.items():
                if name in cmds_saved:
                    try:
                        loaded = from_json_safe(cmds_saved[name])
                        commands[name] = loaded if isinstance(loaded, dict) else dict(default_val)
                    except: commands[name] = dict(default_val)
                else: commands[name] = dict(default_val)
            for name, val in cmds_saved.items():
                if name not in commands:
                    try:
                        loaded = from_json_safe(val)
                        if isinstance(loaded, dict): commands[name] = loaded
                    except: pass
            web_config["commands"] = commands
        console.print(f"[bold green]✅ Konfigurasi Dimuat[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Gagal Muat Konfigurasi: {e}[/bold red]")
        with web_config_lock:
            web_config["commands"] = {k: dict(v) for k, v in DEFAULT_COMMANDS.items()}

def save_web_config():
    try:
        with web_config_lock:
            data = {k: web_config[k] for k in [
                "squad_size", "world_recruit_count", "world_recruit_type",
                "squad_lifetime_sec", "auto_recreate", "welcome_msg",
                "auto_recruit_on_join", "auto_recruit_on_leave", "recruit_delay_sec",
                "auto_bundle_on_join", "bundle_count_on_join", "auto_animation",
                "animation_interval_sec", "auto_emote_on_join", "emote_join_delay_sec",
                "join_emote_pool", "auto_kick_on_join", "kick_delay_sec", "kick_msg",
                "auto_welcome_on_join", "welcome_delay_sec",
                "bot_self_emote_enabled", "bot_self_emote_pool", "bot_self_emote_interval",
            ]}
            data["commands"] = to_json_safe(web_config["commands"])
        with open(WEB_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        console.print(f"[bold red]Gagal Simpan Konfigurasi: {e}[/bold red]"); return False

# ================================================================
#   PENYIMPANAN AKUN
# ================================================================
def load_accounts(file_path=ACCOUNTS_FILE):
    try:
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f: f.write("")
            return {}
        with open(file_path, "r", encoding="utf-8") as f: lines = f.readlines()
        accounts = {}
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith("#"): continue
            sep = ":" if ":" in line else ("|" if "|" in line else None)
            if sep is None: continue
            parts = line.split(sep, 1)
            if len(parts) != 2: continue
            uid, pwd = parts[0].strip(), parts[1].strip()
            if uid.isdigit() and pwd: accounts[uid] = pwd
        return accounts
    except Exception as e:
        console.print(f"[bold red]Gagal Muat Akun: {e}[/bold red]"); return {}

def save_accounts(accs, file_path=ACCOUNTS_FILE):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for uid, pwd in accs.items(): f.write(f"{uid}:{pwd}\n")
        return True
    except Exception as e:
        console.print(f"[bold red]Gagal Simpan Akun: {e}[/bold red]"); return False

def save_accounts_raw(text, file_path=ACCOUNTS_FILE):
    try:
        with open(file_path, "w", encoding="utf-8") as f: f.write(text)
        return True
    except Exception as e:
        console.print(f"[bold red]Gagal Simpan Akun: {e}[/bold red]"); return False

# ================================================================
#   PROTOBUF HELPER
# ================================================================
def read_varint(data, pos):
    result = shift = 0
    while pos < len(data):
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return result, pos

def parse_pb(data):
    fields = {}; pos = 0; n = len(data)
    while pos < n:
        try: key, pos = read_varint(data, pos)
        except: break
        fn = key >> 3; wt = key & 0x07
        try:
            if wt == 0: val, pos = read_varint(data, pos)
            elif wt == 2:
                ln, pos = read_varint(data, pos); val = data[pos:pos + ln]; pos += ln
            elif wt == 5: val = data[pos:pos + 4]; pos += 4
            elif wt == 1: val = data[pos:pos + 8]; pos += 8
            else: break
        except: break
        fields.setdefault(fn, []).append(val)
    return fields

def extract_player_name(login_data_bytes):
    try:
        fields = parse_pb(login_data_bytes)
        for fn in [4, 3, 5, 6]:
            if fn in fields:
                nv = fields[fn][0]
                if isinstance(nv, (bytes, bytearray)):
                    d = nv.decode('utf-8', errors='ignore')
                    if d and len(d) < 60 and not d.startswith("0OuCe") and not d.startswith("eyJ") and all(c.isprintable() or c in '\u200b\u200c\u200d' for c in d):
                        return d
    except: pass
    return None

def Uaa():
    versions = ['5.0.1B2','5.1.0P1','5.2.0B1']
    models = ['SM-A125F','Redmi 9A','POCO M3']
    return f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {random.choice(['11','12','13'])};en-US;USA;)"

Hr = {
    'User-Agent': Uaa(), 'Connection': "Keep-Alive", 'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': ob
}

def xBunnEr():
    return random.choice([
        902000011, 902000013, 902047016, 902049015,
        902000154, 902000127, 902000207, 902000305,
        902037031, 902042011, 902053016, 902053018
    ])

def update_bot_info(uid, **kwargs):
    with bot_lock:
        if uid not in bot_status:
            bot_status[uid] = {"guest_uid": uid, "account_uid": "Memuat...", "status": "🔄 Inisialisasi...",
                "last_squad_id": "None", "last_active": "N/A", "squad_active": False}
        bot_status[uid].update(kwargs)

def update_active_account(uid, **kwargs):
    with active_lock:
        global online_count
        for acc in active_accounts:
            if acc['uid'] == uid:
                acc.update(kwargs); return
        active_accounts.append({
            'uid': uid, 'bot_uid': kwargs.get('bot_uid', uid),
            'name': kwargs.get('name', 'Tidak Diketahui'), 'region': kwargs.get('region', 'BD'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'squad_id': kwargs.get('squad_id', 'Menunggu...'),
            'squad_members': kwargs.get('squad_members', '0/0')
        })

def remove_active_account(uid):
    global online_count
    with active_lock:
        active_accounts[:] = [a for a in active_accounts if a['uid'] != uid]
        if online_count > 0: online_count -= 1

def Fix_PackEt(parsed_results):
    rd = {}
    for r in parsed_results:
        fd = {'wire_type': r.wire_type}
        if r.wire_type in ["varint", "string", "bytes"]: fd['data'] = r.data
        elif r.wire_type == 'length_delimited': fd["data"] = Fix_PackEt(r.data.results)
        rd[r.field] = fd
    return rd

def DeCode_PackEt(input_text):
    try: return json.dumps(Fix_PackEt(Parser().parse(input_text)))
    except Exception: return None

async def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        b = N & 0x7F; N >>= 7
        if N: b |= 0x80
        H.append(b)
        if not N: break
    return bytes(H)

async def CrEaTe_VarianT(fn, val):
    return await EnC_Vr((fn<<3)|0) + await EnC_Vr(val)

async def CrEaTe_LenGTh(fn, val):
    ev = val.encode() if isinstance(val, str) else val
    return await EnC_Vr((fn<<3)|2) + await EnC_Vr(len(ev)) + ev

async def CrEaTe_ProTo(fields):
    packet = bytearray()
    for f, v in fields.items():
        if isinstance(f, str):
            try: f = int(f)
            except: continue
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    nested = await CrEaTe_ProTo(item)
                    packet.extend(await CrEaTe_LenGTh(f, nested))
        elif isinstance(v, dict):
            nested = await CrEaTe_ProTo(v)
            packet.extend(await CrEaTe_LenGTh(f, nested))
        elif isinstance(v, int):
            packet.extend(await CrEaTe_VarianT(f, v))
        elif isinstance(v, (str, bytes)):
            packet.extend(await CrEaTe_LenGTh(f, v))
    return bytes(packet)

async def DecodE_HeX(H):
    F = str(hex(H))[2:]
    return "0" + F if len(F) == 1 else F

async def EnC_PacKeT(HeX, K, V):
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

async def GeneRaTePk(Pk, N, K, V):
    PkEnc = await EnC_PacKeT(Pk, K, V)
    _ = await DecodE_HeX(len(PkEnc) // 2)
    HeadEr = N+"000000" if len(_)==2 else N+"00000" if len(_)==3 else N+"0000" if len(_)==4 else N+"000"
    return bytes.fromhex(HeadEr + _ + PkEnc)

async def encrypt_packet(packet_hex, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(packet_hex), AES.block_size)).hex()

# ================================================================
#   BUNDLE / ANIMASI
# ================================================================
async def mahir_animation_packet(animation_id, key, iv):
    try:
        fields = {1: 88, 2: {1: {1: int(animation_id)}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = format(pl, 'x')
        return bytes.fromhex("051500" + "0" * (6 - len(hl)) + hl + encrypted)
    except Exception as e:
        console.print(f"[red]error animasi: {e}[/red]"); return None

async def Mahir_bundle_packet(bundle_id, key, iv, region="bd"):
    try:
        fields = {1: 88, 2: {1: {1: bundle_id, 2: 1}, 2: 2}}
        encrypted = await encrypt_packet((await CrEaTe_ProTo(fields)).hex(), key, iv)
        hl = await DecodE_HeX(len(encrypted) // 2)
        pt = '0514' if region.lower() == "ind" else ("0519" if region.lower() == "bd" else "0515")
        fh = f"{pt}000000" if len(hl) == 2 else f"{pt}00000" if len(hl) == 3 else f"{pt}0000" if len(hl) == 4 else f"{pt}000" if len(hl) == 5 else f"{pt}000000"
        return bytes.fromhex(fh + hl + encrypted)
    except Exception as e:
        console.print(f"[red]error bundle: {e}[/red]"); return None

async def Mahir_bundle_packet_2(bundle_id, key, iv, region="bd"):
    try:
        fields = {1: 88, 2: {1: {1: bundle_id, 2: 2}, 2: 2}}
        encrypted = await encrypt_packet((await CrEaTe_ProTo(fields)).hex(), key, iv)
        hl = await DecodE_HeX(len(encrypted) // 2)
        pt = '0514' if region.lower() == "ind" else ("0519" if region.lower() == "bd" else "0515")
        fh = f"{pt}000000" if len(hl) == 2 else f"{pt}00000" if len(hl) == 3 else f"{pt}0000" if len(hl) == 4 else f"{pt}000" if len(hl) == 5 else f"{pt}000000"
        return bytes.fromhex(fh + hl + encrypted)
    except Exception as e:
        console.print(f"[red]error bundle2: {e}[/red]"); return None

# ================================================================
#   PAKET SQUAD
# ================================================================
async def MAHIR_OPenSq(key, iv, region, version_):
    fields = {
        1: 1,
        2: {
            2: "\u0001", 3: 43, 4: 1, 5: "en",
            8: [{1: "IDC2", 2: 171, 3: "BD"}], 9: 1,
            10: "rYUW\u0017\t\u0007NR\u000f\u0005\u0004\\W\u0002\u000fV\u0004TPQ\u0003\u000f\u0005\u0004]\u0005\u000b\u0000\u0002W\u0005\r\nVY\u0004\u0007\u0007\u0007\u0017\u0001\bNQ\fS\u0005\u000e\u0006\f\u0005\rT\u0002\r\u0000TS\u0007U\u0004X\u0006RY\u0005\u0003\u0003SW\u0000\u000eQ\u0000^\u0014\u0003\u0004JXS\u000f\u0000g{gqfePblEZJp{_xU\bmQW\f\u0007\u000f\u0015\u0007H\\U^CHXh@Ax`\u000f~\rPN~Nz\\\u001fr_ckPU\u000b\u0015\u0005\u0003Ekfp\u007fcY\u0001nWV\u0002\u0005azE~N\u0007HTg\u0007w}@\u0002{\t\u0013\u0001NeNP]DUf|]ugINs{\u0001\\rAgB_\u0004fA]\u0004\r\u001a\u0000HpOv\\\u0005|gS\u0019\\A\u007fWW\u0003\u007fTqFGi\u0004Qr\u0019dW\u0004\u0011\rD\u0002yeZ]A\u0016a\u0007Ungeg\u0007E\\P\u001b\u000b\u0004\u0005dd\ff\r\u000f\u0017\t\u000fNRyZd\u0012tZ\fe\u0007AGv\u007fw]{P\u001c\u007f\u000ff\u0005ZJK\u0004\u0005\u0014\u0001Jgq\u001frymsB\u0001\u000fd`\u001bj~[}\u0004SDZ|IxKB\u0000\n\u0011\u0002J^`tjYN\u0007WQdE[PQ\u0002_{VP`S\t\u007f\u001dP\n\u000f\u000f\u0015\u0004\u0004L{V\u0003@yP[rgJ{Hpk\u0001\u000bw\u0001Agt_\u0003HxPc\u000b\u0017\u0005E`y\ngWoy\u0006S{A\u001b``Y\u0002Xzw}dDWOKsg\t\u0013\u000eNf\u000e\\`\u0005AwJc\u0003BM\u0001^\u0000R\u0002Qoh]tbS~`G\r\u001a\u0004HibAQ\u000f^XNt~kDUWaeaNqcLQ]Py[G\u0004",
            11: 1, 13: 1,
            14: {
                1: "08FAA33B035B3F16020859055555000200030001000000004AFA7572105C674946762514220104186fa2e8770e748c3f6a68ed75000000ff18470f0bcacfa16d",
                2: 681,
                3: {14: {11: "1106064f50055401030f03020403060155070d01540e060e020607540706030354530f041003064d715c46434b1f061f031e1205034a1c40677c5f554775755f504e677446185b584901534144685b67620f", 0: 72}},
                4: "x\\\\R", 6: 13, 7: {2: 80}, 8: version_, 9: 2, 10: 1,
                11: "03626253513677542b504e4635416456324b796f566c576a326567507844414c33507138513031762b66536c626a587648434e3348414e376c472b72474637794165676e72436b553671626b694538706f534e5a582b2f7a44675a547475465650542b384d69565a507151312b444b53576f786f6d592f7156394f76755254482b7154486a78486f664169734267564970454d454e6b4c326a4763445a4a5176416d687947356b7669564e544d71515745754b32324d4e384e4931424d437445395532415156694b667948314574412b32644536464b53773132554155596363372b7753652b66676c393742756544446a58496d6e35666d45444a51535948326644484c5650676755472f51794b776e77545151324a505265352f72314830616d374264424f556b712f523246734d635475516d47364c684a547a4379345774444245795268305754366f68532f785a48736a4c7a4366506378372f386a534133352b67787642657450397a4f6f463639344945386e6e77336b507344357a6e6337593649776b4142435761776f6d572b6948594f5939686d647632706975584168416d6d6a74496f5945444c6e506e5738616f7153304f74486b732f5a3953543252447345507a3343655438774e6874756d57634b4438585445376649386c305173726a772f4a57514f76394b50307257644538593375422f2b495836757675452b487a6a4853466c75726f33515432536567595758535854714674495a61454d476c51314b7639666c59525539465047366c30663045314f7a2b2b36324339644b664c4d39315a782f6f625938726a6e682b77524a3962636e544e41715466486f72354b714d3d"
            },
            19: 329, 21: "374f5219", 24: {1: 21}, 27: "a_6534489873065906362"
        }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

async def MAHIR_cHSq22(Nu, bot_uid, key, iv, region):
    fields = {1: 17, 2: {1: int(bot_uid), 2: 1, 3: 3, 4: 1, 5: "\x1a", 8: 1}}
    pt = '0514' if region.lower() == "ind" else ("0519" if region.lower() == "bd" else "0515")
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pt, key, iv)

async def MAHIR_World_Recruit(tid, key, iv):
    try:
        fields = {1: 66, 2: {1: int(tid), 5: {}, 9: "", 10: 1}}
        return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)
    except: return None

async def MAHIR_World_Recruit2(tid, key, iv):
    try:
        fields = {1: 66, 2: {1: int(tid), 5: "\u0007", 9: {}, 10: 1}}
        return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)
    except: return None

async def MAHIR_LeaveSquad(key, iv, region, bot_own_id):
    fields = {1: 7, 2: {1: int(bot_own_id)}}
    pt = '0514' if region.lower() == "ind" else ("0519" if region.lower() == "bd" else "0515")
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pt, key, iv)

# ⭐ FIXED: MAHIR_SendSquadMsg — field order sudah benar
async def MAHIR_SendSquadMsg(squad_owner, message, bot_uid, key, iv):
    try:
        if not squad_owner or not bot_uid:
            return None
        
        squad_owner = int(squad_owner)
        bot_uid = int(bot_uid)
        avatar_id = xBunnEr()
        if not isinstance(avatar_id, int):
            avatar_id = 902000011
        
        msg_str = str(message)
        preview = msg_str[:15] if len(msg_str) > 15 else msg_str
        
        fields = {
            1: 1,
            2: {
                1: bot_uid,          # ✅ FIX: field 1 = pengirim (bot)
                2: squad_owner,      # ✅ FIX: field 2 = target (squad)
                3: 0,
                4: msg_str,
                5: int(datetime.now().timestamp()),
                7: 6,
                9: {
                    1: f"[C][FF0000]{preview}",
                    2: avatar_id,
                    3: 2,
                    4: 330,
                    5: 800000304,
                    6: 66,
                    7: 66,
                    8: "NM.CDX",
                    9: 66,
                    10: 1,
                    11: 1,
                    13: {1: 68, 2: 67},
                    14: {
                        1: 1158053040,
                        2: 8,
                        3: b"\x10\x15\x08\x0A\x0B\x15\x0C\x0F\x11\x04\x07\x02\x03\x0D\x0E\x12\x01\x05\x06"
                    }
                },
                10: "en",
                13: {3: 1},
                14: {}
            }
        }
        proto = await CrEaTe_ProTo(fields)
        pk = "080112" + (await EnC_Vr(len(proto))).hex() + proto.hex()
        return await GeneRaTePk(pk, '1215', key, iv)
    except Exception as e:
        console.print(f"[red]Error pesan squad: {e}[/red]")
        return None

async def MAHIR_OpenSquadChat(squad_id, chat_code, key, iv):
    try:
        squad_id = int(squad_id)
        fields = {1: 3, 2: {1: squad_id, 2: 3, 3: "en", 4: str(chat_code)}}
        proto = await CrEaTe_ProTo(fields)
        pk = "080112" + (await EnC_Vr(len(proto))).hex() + proto.hex()
        return await GeneRaTePk(pk, '1215', key, iv)
    except Exception as e:
        console.print(f"[red]Error BukaChatSquad: {e}[/red]")
        return None

async def Emote_k(TarGeT, idT, K, V, region):
    try:
        bot_self_id = int(BOT_OWN_ID) if 'BOT_OWN_ID' in globals() and globals().get('BOT_OWN_ID') else 0
    except:
        bot_self_id = 0
    fields = {1: 21, 2: {1: bot_self_id, 2: 909000001, 5: {1: int(TarGeT), 3: int(idT)}}}
    if region.lower() == "ind": pkt = '0514'
    elif region.lower() == "bd": pkt = "0519"
    else: pkt = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pkt, K, V)

async def KickTarget(target_uid, key, iv):
    fields = {1: 35, 2: {1: int(target_uid)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

# ================================================================
#   MENU BANTUAN
# ================================================================
async def build_help_menu(nickname="User", bot_uid="0"):
    def pg(bdr, ttl_col, ttl, items):
        out = f"[b][c][{bdr}]┌───────────────┐\n[{ttl_col}][b][c]●  {ttl} ●\n[{bdr}][b][c]└───────────────┘\n"
        CLR = [("ff6600","ffd700","ffff55","00ffcc"),("aaff00","ff9944","ffffff","55ff99"),
               ("00ffaa","ff66bb","aaffff","ff88ff"),("00ccff","ffee88","ffaa44","44ddff")]
        for i, (d, c) in enumerate(items):
            bc, dc, ac, cc = CLR[i % 4]
            out += f"\n[{bc}]◆ [{dc}][b]{d}[/b] [{ac}]→  [{cc}]{c}"
        out += f"\n\n[{bdr}][b][c]◆───────────────◆"
        return out
    sn = nickname if nickname and nickname != "Unknown" else "User"
    pages = [f"[FF0000][b][c]◉\n[b][c][0dffd0]Hai {sn}, Selamat datang di [ffffff]NM.CDX [0dffd0] BOT\n[FF0000]• [0dffd0]Ketik [ffffff]help [0dffd0]untuk bantuan\n[FF0000][b][c]◉\n\n[C][B][0dffd0]+------ 📊 PROFIL PEMAIN ------+\n[C][0dffd0] » Nama      : [ffffff]{sn}\n[C][0dffd0] » UID       : [ffffff]{bot_uid}\n[C][B][0dffd0]+--------------------------------+"]
    pages.append(pg("ff9900", "ffee00", "UMUM", [("Menu Bantuan","help / hello"),("Sambutan","HI"),("Waktu",".time"),("Info Saya","my id")]))
    pages.append(pg("00aaff", "00eeff", "TOKO", [("Toko","/store"),("Aplikasi","/app"),("Owner","NM.CDX"),("Versi",".ffv")]))
    pages.append(pg("ff44aa", "ff99dd", "SQUAD", [("Undang","/inv"),("Recruit","st"),("Ukuran","/5  /6"),("Keluar","/exit")]))
    pages.append(f"[b][c][FF1493]╔═══════════════════════╗\n[b][c][FF1493]║      👑 INFO OWNER 👑      ║\n[b][c][FF1493]╠═══════════════════════╣\n[b][c][FFFFFF]║ 👤 Nama     : [FFD700]NM.CDX\n[b][c][FFFFFF]║ 📱 Telegram : [00FFFF]@NMCDX\n[b][c][FFFFFF]║ 🎵 TikTok   : [00FFFF]@NM.CDX\n[b][c][FFFFFF]║ 🌐 Website  : [00FFFF]nmcdx.xo.je\n[b][c][FF1493]╚═══════════════════════╝")
    return pages

# ================================================================
#   HELPER AUTH
# ================================================================
async def GeNeRaTeAccAccess(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {"Host":"100067.connect.garena.com","User-Agent":Uaa(),"Content-Type":"application/x-www-form-urlencoded","Connection":"close"}
    data = {"uid":uid,"password":password,"response_type":"token","client_type":"2","client_secret":"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3","client_id":"100067"}
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.post(url, headers=headers, data=data) as resp:
                if resp.status != 200: return None, None
                d = await resp.json()
                return d.get("open_id"), d.get("access_token")
    except: return None, None

def encode_varint(value):
    result = []
    if value < 0: value &= (1 << 64) - 1
    while True:
        byte = value & 0x7F; value >>= 7
        if value: byte |= 0x80
        result.append(byte)
        if not value: break
    return bytes(result)

def create_proto(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested = create_proto(value)
            packet.extend(encode_varint((field << 3) | 2))
            packet.extend(encode_varint(len(nested))); packet.extend(nested)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    nested = create_proto(item)
                    packet.extend(encode_varint((field << 3) | 2))
                    packet.extend(encode_varint(len(nested))); packet.extend(nested)
        elif isinstance(value, int):
            packet.extend(encode_varint((field << 3) | 0)); packet.extend(encode_varint(value))
        elif isinstance(value, str):
            encoded = value.encode('utf-8')
            packet.extend(encode_varint((field << 3) | 2))
            packet.extend(encode_varint(len(encoded))); packet.extend(encoded)
        elif isinstance(value, bytes):
            packet.extend(encode_varint((field << 3) | 2))
            packet.extend(encode_varint(len(value))); packet.extend(value)
    return bytes(packet)

def encrypt_aes(hex_data: str) -> str:
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(bytes.fromhex(hex_data), AES.block_size)).hex()

async def EncRypTMajoRLoGin(open_id, access_token, version_):
    fields = {
        3: str(datetime.now())[:-7], 4: "free fire", 5: 1, 7: str(version_),
        8: "Android OS 11 / API-30 (RP1A.200720.011/230921V810)", 9: "Handheld",
        10: "Grameenphone", 11: "WIFI", 12: 1708, 13: 750, 14: "480",
        15: "ARM64 FP ASIMD AES | 2000 | 8", 16: 5767, 17: "Mali-G52 MC2",
        18: "OpenGL ES 3.2 v1.r26p0-01eac0.f143e3f9482527bbad36b3ec27f93e59",
        19: "Google|3f10d414-be33-4ac3-b9fc-fcbf47c183b5", 20: "103.200.36.134",
        21: "en", 22: str(open_id), 23: "4", 24: "Handheld",
        25: "INFINIX MOBILITY LIMITED Infinix X6812", 26: "BD", 29: str(access_token), 30: 1,
        41: "Grameenphone", 42: "WIFI", 57: "7428b253defc164018c604a1ebbfebdf",
        60: 110962, 61: 80611, 62: 1051, 64: 80829, 65: 110962, 66: 80829, 67: 110962, 73: 2,
        74: "/data/app/~~MxBbX9YA6AkFscre_RExgw==/com.dts.freefireth-hLOkTeh1Q46L_oLV4UXQTg==/lib/arm64", 76: 1,
        77: "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~MxBbX9YA6AkFscre_RExgw==/com.dts.freefireth-hLOkTeh1Q46L_oLV4UXQTg==/base.apk",
        78: 3, 79: 2, 81: "64", 83: "2019121229", 85: 3, 86: "OpenGLES2", 87: 4095, 88: 4,
        91: {9: 65}, 92: 10508, 93: "android",
        94: "KqsHT76RdsVKvnpkirzc2FQs3eu0OZChfZxMTZn+Rjv06Ri2qeOQkyPcdk5JceWKmXhOFFUPuNy9S8esTr37yCT5piY32iUcehVw0bL4F4lzAmyD",
        95: 111207, 96: '{"cur_rate":[60,90],"support_etc2":false}', 97: 1, 98: 1, 99: "4", 100: "4",
        102: "B\\FFP[[\tf", 103: 1, 104: 28754, 105: 1,
        106: "https://dl.ak.freefiremobile.com/live/ABHotUpdates/|https://core-ak.freefiremobile.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a",
        107: "1.477aa00e98bf924c"
    }
    return bytes.fromhex(encrypt_aes(create_proto(fields).hex()))

async def MajorLogin(payload):
    base = login_url.rstrip("/")
    if not base.startswith(("http://", "https://")): base = "https://" + base
    url = f"{base}/MajorLogin"
    Hr["X-GA-SV"] = str(int(time.time()))
    Hr["ReleaseVersion"] = ob
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False; ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as r:
            if r.status != 200: return None
            raw = await r.read()
            return raw[64:] if len(raw) > 64 else raw

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False; ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization'] = f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as r:
            if r.status == 200: return await r.read()
            return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    class P:
        def __init__(self, f):
            self.account_uid = int(f.get(1, 0)); self.region = str(f.get(2, ""))
            self.token = str(f.get(8, "")); self.url = str(f.get(10, ""))
            self.timestamp = int(f.get(21, 0))
            rk = f.get(22, b"")
            if isinstance(rk, str):
                try: self.key = bytes.fromhex(rk.replace(" ", ""))
                except: self.key = rk.encode()
            else: self.key = bytes(rk)
            riv = f.get(23, b"")
            if isinstance(riv, str):
                try: self.iv = bytes.fromhex(riv.replace(" ", ""))
                except: self.iv = riv.encode()
            else: self.iv = bytes(riv)
    def dv(buf, off):
        res, sh, st = 0, 0, off
        while True:
            if off >= len(buf): raise IndexError
            b = buf[off]; off += 1
            res += (b & 0x7F) << sh; sh += 7
            if b < 0x80: break
        return res, off - st
    def dp(buf):
        off, parts, blen = 0, [], len(buf)
        try:
            while off < blen:
                it, vl = dv(buf, off); off += vl
                wt, fn = it & 7, it >> 3
                if wt == 0: val, vl = dv(buf, off); off += vl
                elif wt == 2:
                    length, vl = dv(buf, off); off += vl
                    if off + length > blen: return None
                    val = buf[off:off+length]; off += length
                elif wt == 5:
                    if off + 4 > blen: return None
                    val = struct.unpack_from("<I", buf, off)[0]; off += 4
                elif wt == 1:
                    if off + 8 > blen: return None
                    val = struct.unpack_from("<Q", buf, off)[0]; off += 8
                else: return None
                parts.append((fn, wt, val))
            return parts
        except: return None
    def td(parts):
        r = {}
        for fn, wt, v in parts:
            if wt == 2:
                try: val = v.decode("utf-8")
                except: val = v
            else: val = v
            r[fn] = val
        return r
    buf = MajoRLoGinResPonsE
    try:
        c = AES.new(b'Yg&tc%DEuh6%Zc^8', AES.MODE_CBC, b'6oyZDr22E3ychjM%')
        buf = unpad(c.decrypt(buf), AES.block_size)
    except: pass
    p = dp(buf)
    if p:
        d = td(p)
        if 1 in d or 8 in d or 10 in d: return P(d)
    for o in range(len(buf)):
        p = dp(buf[o:])
        if p:
            d = td(p)
            if 1 in d or 8 in d or 10 in d: return P(d)
    return P({})

def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv)  if isinstance(iv, str) else iv
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_token.encode('utf-8'), AES.block_size))
        header = bytes.fromhex('6d19') + int(account_id).to_bytes(8, 'big') + int(timestamp).to_bytes(4, 'big') + len(ct).to_bytes(4, 'big')
        return (header + ct).hex()
    except Exception as e:
        print(f"❌ AUTH CHAT: {e}"); return None

def create_auth_token_online(account_uid, token, kts, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv)  if isinstance(iv, str) else iv
        enc_token = AES.new(K, AES.MODE_CBC, V).encrypt(pad(token.encode("utf-8"), 16))
        opcode = bytes.fromhex("830c")
        return (opcode + int(account_uid).to_bytes(8, byteorder="big") + int(kts).to_bytes(4, byteorder="big") + len(enc_token).to_bytes(8, byteorder="big") + enc_token).hex()
    except Exception as e:
        print(f"❌ AUTH ONLINE: {e}"); return None

# ================================================================
#   PEMUAT AKUN BATCH
# ================================================================
async def batch_account_loader():
    global total_accounts
    active_bots, bot_tasks, last_passwords = {}, {}, {}
    console.print("[bold cyan]🚀 Pemuat Akun Batch dijalankan...[/bold cyan]")
    while True:
        try:
            accounts = load_accounts()
            total_accounts = len(accounts)
            stopped = is_stopped()

            for uid, pwd in accounts.items():
                if uid in last_passwords and last_passwords[uid] != pwd:
                    console.print(f"[bold yellow]🔑 UID {uid} password berubah → restart[/bold yellow]")
                    if uid in active_bots:
                        try: active_bots[uid].is_running = False
                        except: pass
                        del active_bots[uid]
                    if uid in bot_tasks:
                        if not bot_tasks[uid].done(): bot_tasks[uid].cancel()
                        del bot_tasks[uid]
                last_passwords[uid] = pwd

            if not stopped:
                for uid, pwd in accounts.items():
                    with running_bots_lock: running_bots.add(uid)
                    if uid in bot_tasks and not bot_tasks[uid].done(): continue
                    if uid in bot_tasks: del bot_tasks[uid]
                    if uid in active_bots:
                        try: active_bots[uid].is_running = False
                        except: pass
                        del active_bots[uid]
                    bot = SquadBot(uid=uid, password=pwd, server='bd', index=len(bot_tasks)+1)
                    active_bots[uid] = bot
                    bot_tasks[uid] = asyncio.create_task(bot.keep_online_forever())
                    console.print(f"[bold green]✨ UID {uid} → Diluncurkan[/bold green]")
                    await asyncio.sleep(0.05)
            else:
                for uid in list(bot_tasks.keys()):
                    try:
                        if uid in active_bots: active_bots[uid].is_running = False
                        if not bot_tasks[uid].done(): bot_tasks[uid].cancel()
                    except: pass
                    remove_active_account(uid)
                    with running_bots_lock: running_bots.discard(uid)
                    del bot_tasks[uid]
                    if uid in active_bots: del active_bots[uid]

            if not stopped:
                for uid in list(bot_tasks.keys()):
                    if bot_tasks[uid].done():
                        try: exc = bot_tasks[uid].exception()
                        except: exc = None
                        if exc: console.print(f"[bold red]⚠️ UID {uid} crash → coba lagi[/bold red]")
                        if uid in active_bots:
                            try: active_bots[uid].is_running = False
                            except: pass
                            del active_bots[uid]
                        del bot_tasks[uid]
                for uid in list(bot_tasks.keys()):
                    if uid not in accounts:
                        console.print(f"[bold red]🗑️ UID {uid} dihapus → stop[/bold red]")
                        if uid in active_bots:
                            try: active_bots[uid].is_running = False
                            except: pass
                            del active_bots[uid]
                        if not bot_tasks[uid].done(): bot_tasks[uid].cancel()
                        del bot_tasks[uid]
                        with running_bots_lock: running_bots.discard(uid)
                        last_passwords.pop(uid, None)

            if stopped: console.print(f"[bold red]🛑 DIHENTIKAN — {len(accounts)} idle[/bold red]", end="\r")
            elif accounts: console.print(f"[dim]📊 Aktif: {len(bot_tasks)}/{len(accounts)}[/dim]", end="\r")
        except Exception as e:
            console.print(f"[bold red]Error Pemuat: {e}[/bold red]")
        await asyncio.sleep(2)

def ResTarTinG():
    console.print("[bold yellow]♻️ Restart...[/bold yellow]")
    time.sleep(0.5); os.execl(sys.executable, sys.executable, *sys.argv)

def AuTo_ResTartinG():
    while True:
        time.sleep(3600)
        console.print("[bold red]⚠️ Auto restart...[/bold red]")
        ResTarTinG()

# ================================================================
#   KLIEN BOT SQUAD
# ================================================================
class SquadBot:
    def __init__(self, uid, password, server='bd', index=0):
        self.uid, self.password, self.server, self.index = uid, password, server, index
        self.is_running = True
        self.online_writer = self.chat_writer = self.reader = None
        self.key = self.iv = self.region = None
        self.tasks = []
        self.is_online = False
        self.Nm = "Tidak Diketahui"
        self.bot_uid = None
        self.chat_reader = None
        self.squad_created = False
        self.squad_members = set()
        self.member_names = {}
        self.current_squad_id = self.current_chat_code = None
        self.seen_recreate_ts = self.seen_restart_ts = 0
        self.squad_created_at = 0
        self.last_recruit_at = self.last_bundle_at = 0
        self.last_emote_on_join_at = 0
        self.jwt_token = None
        self._recruit_lock = asyncio.Lock()
        self._bundle_lock = asyncio.Lock()
        self._recreate_lock = asyncio.Lock()
        self._animation_task = None
        self._self_emote_task = None
        update_bot_info(self.uid, status="🔄 Inisialisasi...", squad_active=False)

    async def _send_emote_on_join(self, target_uid):
        try:
            with web_config_lock:
                enabled = web_config.get("auto_emote_on_join", True)
                delay = float(web_config.get("emote_join_delay_sec", 0.5))
                pool = list(web_config.get("join_emote_pool", DEFAULT_JOIN_EMOTES))
            if not enabled or not pool: return False
            if not self.online_writer or not self.bot_uid: return False
            global BOT_OWN_ID
            try: BOT_OWN_ID = int(self.bot_uid)
            except: pass
            await asyncio.sleep(max(0.05, delay))
            emote_id = random.choice(pool)
            pkt = await Emote_k(int(target_uid), int(emote_id), self.key, self.iv, self.region or "bd")
            if pkt and self.online_writer and not self.online_writer.is_closing():
                self.online_writer.write(pkt); await self.online_writer.drain()
                self.last_emote_on_join_at = time.time()
                console.print(f"[bold magenta]🎭 [{self.uid}] Emote Join → {target_uid} (id={emote_id}, delay={delay}s)[/bold magenta]")
                return True
        except Exception as e:
            console.print(f"[yellow]⚠ [{self.uid}] Error emote join: {e}[/yellow]")
        return False

    async def _send_bundle_on_join(self):
        if not self.online_writer or not self.bot_uid: return False
        async with self._bundle_lock:
            now = time.time()
            if now - self.last_bundle_at < _BUNDLE_COOLDOWN: return False
            with web_config_lock:
                enabled = web_config.get("auto_bundle_on_join", True)
                count = web_config.get("bundle_count_on_join", 2)
            if not enabled: return False
            count = max(1, min(5, int(count)))
            sent = 0
            for i in range(count):
                try:
                    bid = random.choice(AUTO_BUNDLE_POOL)
                    pkt = await (Mahir_bundle_packet if i == 0 else Mahir_bundle_packet_2)(bid, self.key, self.iv, self.region or "bd")
                    if pkt:
                        self.online_writer.write(pkt); await self.online_writer.drain()
                        sent += 1; await asyncio.sleep(0.5)
                except: break
            self.last_bundle_at = time.time()
            if sent: console.print(f"[bold magenta]👗 [{self.uid}] Bundle × {sent}[/bold magenta]")
            return sent > 0

    # ✅ FIXED: _auto_kick_member — cek is_closing()
    async def _auto_kick_member(self, target_uid, target_name="Player"):
        try:
            with web_config_lock:
                enabled = web_config.get("auto_kick_on_join", False)
                delay = float(web_config.get("kick_delay_sec", 1.0))
                km = web_config.get("kick_msg", "")
            if not enabled:
                return False
            if not self.online_writer or self.online_writer.is_closing():
                return False
            await asyncio.sleep(max(0.05, delay))
            try:
                kick_pkt = await KickTarget(int(target_uid), self.key, self.iv)
                if kick_pkt and self.online_writer and not self.online_writer.is_closing():
                    self.online_writer.write(kick_pkt)
                    await self.online_writer.drain()
                    console.print(f"[bold red]🚫 [{self.uid}] Auto-kick → {target_name} ({target_uid})[/bold red]")
            except Exception as e:
                console.print(f"[yellow]⚠ Error pkt kick: {e}[/yellow]")
            try:
                km2 = str(km).replace("{user_name}", str(target_name)).replace("{user_id}", str(target_uid))
                sq_id = self.current_squad_id
                if sq_id and self.chat_writer and not self.chat_writer.is_closing() and self.bot_uid:
                    msg_pkt = await MAHIR_SendSquadMsg(
                        int(sq_id), km2, int(self.bot_uid), self.key, self.iv
                    )
                    if msg_pkt:
                        self.chat_writer.write(msg_pkt)
                        await self.chat_writer.drain()
            except Exception as e:
                console.print(f"[yellow]⚠ Error pesan kick: {e}[/yellow]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Error auto-kick: {e}[/red]")
            return False

    # ✅ FIXED: _auto_welcome_member — chat_writer.is_closing() + debug log
    async def _auto_welcome_member(self, squad_id, chat_code, target_uid, target_name="Player"):
        try:
            with web_config_lock:
                enabled = web_config.get("auto_welcome_on_join", True)
                delay = float(web_config.get("welcome_delay_sec", 0.5))
            if not enabled:
                return False
            if not self.chat_writer or self.chat_writer.is_closing():
                console.print(f"[yellow]⚠ [{self.uid}] Welcome skip: chat_writer None/closed[/yellow]")
                return False
            if not self.bot_uid:
                console.print(f"[yellow]⚠ [{self.uid}] Welcome skip: bot_uid kosong[/yellow]")
                return False
            if not squad_id:
                console.print(f"[yellow]⚠ [{self.uid}] Welcome skip: squad_id kosong[/yellow]")
                return False

            console.print(f"[cyan][DEBUG] Welcome → squad={squad_id} user={target_name} ({target_uid}) chat_code={str(chat_code)[:20] if chat_code else 'None'}[/cyan]")

            await asyncio.sleep(max(0.05, delay))
            try:
                if chat_code:
                    op = await MAHIR_OpenSquadChat(int(squad_id), str(chat_code), self.key, self.iv)
                    if op:
                        self.chat_writer.write(op)
                        await self.chat_writer.drain()
                        await asyncio.sleep(0.2)
                        console.print(f"[cyan][DEBUG] Chat opened for squad {squad_id}[/cyan]")
            except Exception as e:
                console.print(f"[yellow]⚠ Error buka chat: {e}[/yellow]")
            with web_config_lock:
                wt = web_config.get("welcome_msg", DEFAULT_WELCOME_MSG)
            wm = wt.replace("{user_name}", str(target_name))
            mp = await MAHIR_SendSquadMsg(
                int(squad_id), wm, int(self.bot_uid), self.key, self.iv
            )
            if mp:
                self.chat_writer.write(mp)
                await self.chat_writer.drain()
                console.print(f"[bold green]✅ [{self.uid}] Sambutan → {target_name}[/bold green]")
                return True
            console.print(f"[yellow]⚠ [{self.uid}] Welcome pkt None[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error sambutan: {e}[/red]")
            return False

    async def _bot_self_emote_loop(self):
        while self.is_running and self.is_online:
            try:
                with web_config_lock:
                    enabled = web_config.get("bot_self_emote_enabled", False)
                    pool = list(web_config.get("bot_self_emote_pool", DEFAULT_JOIN_EMOTES))
                    interval = float(web_config.get("bot_self_emote_interval", 8.0))
                if not enabled or not pool:
                    await asyncio.sleep(2); continue
                if not self.online_writer or not self.bot_uid:
                    await asyncio.sleep(2); continue
                emote_id = random.choice(pool)
                pkt = await Emote_k(int(self.bot_uid), int(emote_id), self.key, self.iv, self.region or "bd")
                if pkt and self.online_writer and not self.online_writer.is_closing():
                    self.online_writer.write(pkt); await self.online_writer.drain()
                    console.print(f"[bold cyan]🤖 [{self.uid}] Emote Sendiri ({emote_id})[/bold cyan]")
                await asyncio.sleep(max(2.0, interval))
            except asyncio.CancelledError: break
            except: await asyncio.sleep(5)

    async def _send_world_recruit(self, reason="manual", count=None):
        if not self.online_writer or not self.bot_uid: return False
        async with self._recruit_lock:
            with web_config_lock:
                dc = web_config.get("world_recruit_count", 3)
                rt = web_config.get("world_recruit_type", "1")
            n = count if count is not None else dc
            n = max(1, min(10, int(n)))
            now = time.time()
            if now - self.last_recruit_at < 2.0 and reason != "initial": return False
            s1, s2 = 0, 0
            for i in range(n):
                try:
                    ut = rt if rt in ("1", "2") else ("1" if rt == "half" and i % 2 == 0 else "2" if rt == "half" else random.choice(["1","2"]))
                    pkt = await (MAHIR_World_Recruit if ut == "1" else MAHIR_World_Recruit2)(self.bot_uid, self.key, self.iv)
                    if pkt:
                        self.online_writer.write(pkt); await self.online_writer.drain()
                        if ut == "1": s1 += 1
                        else: s2 += 1
                        await asyncio.sleep(0.35)
                except: break
            self.last_recruit_at = time.time()
            total = s1 + s2
            if total:
                icon = {"join":"🟢","leave":"🔴","initial":"🚀","manual":"📢"}.get(reason, "📢")
                console.print(f"[cyan]{icon} [{self.uid}] Recruit × {total} (T1={s1} T2={s2} | {reason})[/cyan]")
            return total > 0

    async def _build_and_send_squad(self):
        try:
            with web_config_lock:
                sc = web_config.get("squad_size", 4)
                rcc = web_config.get("world_recruit_count", 3)
            op = await MAHIR_OPenSq(self.key, self.iv, self.region, FREEFIRE_VERSION_NAME)
            if not op or not self.online_writer: return False
            self.online_writer.write(op); await self.online_writer.drain()
            await asyncio.sleep(0.4)
            console.print(f"[cyan]ℹ [{self.uid}] Squad Dibuat ✅[/cyan]")
            try:
                op2 = await MAHIR_OPenSq(self.key, self.iv, self.region, FREEFIRE_VERSION_NAME)
                self.online_writer.write(op2); await self.online_writer.drain()
                await asyncio.sleep(0.3)
            except: pass
            try:
                sp = await MAHIR_cHSq22(sc, self.bot_uid, self.key, self.iv, self.region)
                self.online_writer.write(sp); await self.online_writer.drain()
                await asyncio.sleep(0.3)
            except: pass
            await self._send_world_recruit(reason="initial", count=rcc)
            self.squad_created = True
            self.squad_created_at = time.time()
            self.squad_members.clear()
            self.member_names.clear()
            update_bot_info(self.uid, status="✅ Squad Aktif", squad_active=True)
            return True
        except Exception as e:
            console.print(f"[red]Error buat squad [{self.uid}]: {e}[/red]"); return False

    async def _do_recreate(self):
        if self._recreate_lock.locked(): return False
        async with self._recreate_lock:
            try:
                console.print(f"[yellow]🔄 [{self.uid}] Membuat ulang squad...[/yellow]")
                if self.online_writer and self.bot_uid:
                    try:
                        ep = await MAHIR_LeaveSquad(self.key, self.iv, self.region, self.bot_uid)
                        if ep:
                            self.online_writer.write(ep); await self.online_writer.drain()
                            console.print(f"[red]🚪 [{self.uid}] Keluar[/red]")
                    except: pass
                self.squad_members.clear(); self.member_names.clear()
                self.current_squad_id = self.current_chat_code = None
                self.squad_created = False
                update_active_account(self.uid, squad_id='Menunggu...', squad_members='0/0')
                await asyncio.sleep(0.5)
                return await self._build_and_send_squad()
            except Exception as e:
                console.print(f"[red]Error recreate [{self.uid}]: {e}[/red]")
            return False

    async def send_team_msg(self, message: str, squad_id=None):
        try:
            if not self.chat_writer or self.chat_writer.is_closing():
                return False
            if not self.bot_uid:
                return False
            sq_id = squad_id or self.current_squad_id
            if not sq_id:
                return False
            pkt = await MAHIR_SendSquadMsg(
                int(sq_id), message, int(self.bot_uid), self.key, self.iv
            )
            if pkt:
                self.chat_writer.write(pkt)
                await self.chat_writer.drain()
                return True
        except Exception as e:
            console.print(f"[yellow]⚠ [{self.uid}] Error send_team_msg: {e}[/yellow]")
        return False

    async def handle_team_command(self, cmd_raw: str, sender_uid, sender_name="Player"):
        try:
            cl = cmd_raw.strip().lower()
            if cl in ("/help", "help"):
                for p in await build_help_menu(nickname=sender_name, bot_uid=str(sender_uid)):
                    await self.send_team_msg(p); await asyncio.sleep(0.5)
                return True
            if cl in ("/app", "app"):
                await self.send_team_msg("[B][C][00FFFF]APP NM.CDX TCP RESMI\n[FFFFFF]Link download di bawah")
                await asyncio.sleep(0.4)
                await self.send_team_msg("https://www.mediafire.com/file/lvykrek51q17hae/NMCDX_TCP.apk")
                return True
            if cl in ("/store", "store"):
                await self.send_team_msg("[C][FFD700]⚡ TOKO NM.CDX ⚡\n[C][00FF00]🤖 TCP BOT: [FFFF00]500 BDT\n[C][00FF00]🌐 Website: [FFFF00]nmcdx.xo.je\n[C][00FF00]👤 Owner: [FFFF00]@NMCDX")
                return True
            if cl == "hi":
                await self.send_team_msg("[00FFFF][b][c]😊 Hai! Gimana harimu?\n[FFD700]Telegram: @NMCDX\n[FFD700]TikTok: @NM.CDX")
                return True
            if cl == ".time":
                await self.send_team_msg(f"[B][C][00FFFF]╔═══════════════╗\n[B][C][FFFFFF]🕒 WAKTU: [00FF00]{datetime.now().strftime('%I:%M %p')}\n[B][C][00FFFF]╚═══════════╝")
                return True
            if cl == "my id":
                await self.send_team_msg(f"[B][C][00FFFF]👤 INFO ANDA\n[B][C][FFFFFF]Nama: [00FF00]{sender_name}\n[B][C][FFFFFF]UID : [FFFF00]{sender_uid}")
                return True
            with web_config_lock:
                cmds = dict(web_config.get("commands", {}))
            for trig, cfg in cmds.items():
                if not cfg.get("enabled", True): continue
                mm = cfg.get("match", "contains")
                t, m = trig.lower(), cl
                matched = (mm == "exact" and m == t) or (mm == "startswith" and m.startswith(t)) or (mm == "contains" and t in m)
                if matched:
                    ct = cfg.get("type", "message")
                    if ct == "message":
                        await self.send_team_msg(cfg.get("response", "").replace("{user_name}", str(sender_name)))
                        return True
                    elif ct == "recruit_squad":
                        await self._send_world_recruit(reason="manual"); return True
            return False
        except Exception as e:
            console.print(f"[red]Error handle_team_command: {e}[/red]"); return False

    # ✅ FIXED: tcp_online — pakai extract_chat_code + sq_id fallback
    async def tcp_online(self, ip, port, auth_token):
        self.current_squad_id = None
        self.squad_members = set()
        self.member_names = {}
        self.seen_recreate_ts = get_recreate_timestamp()
        while self.is_running:
            if is_stopped(): break
            try:
                reader, writer = await asyncio.open_connection(ip, int(port))
                writer.write(bytes.fromhex(auth_token)); await writer.drain()
                self.reader, self.online_writer = reader, writer
                self.is_online = True
                update_bot_info(self.uid, status="✅ Online")
                console.print(f"[cyan]ℹ [{self.uid}] ONLINE Terhubung ✅[/cyan]")
                if not await self._build_and_send_squad():
                    self.is_online = False; await asyncio.sleep(10); continue
                if self._animation_task and not self._animation_task.done(): self._animation_task.cancel()
                self._animation_task = asyncio.create_task(self._animation_loop())
                if self._self_emote_task and not self._self_emote_task.done(): self._self_emote_task.cancel()
                self._self_emote_task = asyncio.create_task(self._bot_self_emote_loop())

                while self.is_running and self.is_online:
                    if is_stopped(): break
                    cur_ts = get_recreate_timestamp()
                    if cur_ts > self.seen_recreate_ts:
                        self.seen_recreate_ts = cur_ts
                        await self._do_recreate(); continue
                    with web_config_lock:
                        ar = web_config.get("auto_recreate", True)
                        lt = web_config.get("squad_lifetime_sec", 10)
                    if ar and self.squad_created and (time.time() - self.squad_created_at > lt):
                        console.print(f"[yellow]⏰ [{self.uid}] Umur {lt}s → recreate[/yellow]")
                        await self._do_recreate(); continue
                    try:
                        data = await asyncio.wait_for(self.reader.read(65536), timeout=1.0)
                        if not data: break
                        data_hex = data.hex()
                        if data_hex.startswith("0e00") or data_hex.startswith("0500"):
                            decoded = DeCode_PackEt(data_hex[10:])
                            if decoded:
                                try:
                                    pj = json.loads(decoded)
                                    f5 = pj.get('5')
                                    if not isinstance(f5, dict): continue
                                    f5_data = f5.get('data')
                                    if not isinstance(f5_data, dict): continue
                                    soi = safe_get_int(f5_data.get('1'))
                                    so = str(soi) if soi is not None else None
                                    if so and so != str(self.bot_uid): self.current_squad_id = so
                                    # ✅ FIX #2: extract_chat_code
                                    c_code = extract_chat_code(f5_data)
                                    cm = {}
                                    for pk in ('6','2','3','5','7'):
                                        cand = safe_dict(f5_data.get(pk))
                                        if not cand: continue
                                        cu = safe_get_int(cand.get('1'))
                                        cn = safe_get_str(cand.get('2'))
                                        if cu and str(cu) != str(self.bot_uid) and len(str(cu)) > 8 and cn:
                                            us, pn = str(cu), cn
                                            cm[us] = pn
                                            if us not in self.squad_members:
                                                # ✅ FIX #3: sq_id fallback
                                                sq_id = None
                                                if self.current_squad_id:
                                                    try: sq_id = int(self.current_squad_id)
                                                    except: pass
                                                if not sq_id and soi:
                                                    try: sq_id = int(soi)
                                                    except: pass
                                                console.print(f"[cyan][{self.uid}][/cyan] [green]➜ Bergabung:[/green] [yellow]{pn}[/yellow] ({us})")
                                                asyncio.create_task(self._send_emote_on_join(us))
                                                asyncio.create_task(self._send_bundle_on_join())
                                                with web_config_lock:
                                                    kick_on = web_config.get("auto_kick_on_join", False)
                                                    welcome_on = web_config.get("auto_welcome_on_join", True)
                                                if kick_on:
                                                    asyncio.create_task(self._auto_kick_member(us, pn))
                                                if welcome_on and sq_id:
                                                    asyncio.create_task(self._auto_welcome_member(int(sq_id), c_code, us, target_name=pn))
                                            break
                                    if cm:
                                        jn = {u:n for u,n in cm.items() if u not in self.squad_members}
                                        if jn:
                                            for u, n in jn.items():
                                                self.squad_members.add(u); self.member_names[u] = n
                                            with web_config_lock:
                                                rj = web_config.get("auto_recruit_on_join", True)
                                                sz = web_config.get('squad_size', 4)
                                            if rj: asyncio.create_task(self._send_world_recruit(reason="join"))
                                            update_active_account(self.uid, **{'squad_members': f"{len(self.squad_members)}/{sz+1}"})
                                    nsq = safe_get_int(f5_data.get('1'))
                                    if nsq and 10000000 < nsq < 999999999:
                                        if str(nsq) != str(self.current_squad_id):
                                            self.current_squad_id = str(nsq)
                                            console.print(Panel(f"[green]🆔 ID Squad: [yellow]{self.current_squad_id}[/yellow]", title=f"[magenta]✨ TERBENTUK ({self.uid})[/magenta]", border_style="cyan"))
                                            update_bot_info(self.uid, last_squad_id=str(nsq), squad_active=True)
                                            with web_config_lock: sz = web_config.get('squad_size', 4)
                                            update_active_account(self.uid, **{'squad_id': self.current_squad_id, 'squad_members': f"0/{sz+1}"})
                                except Exception: pass
                    except asyncio.TimeoutError: continue
                    except Exception: break
            except Exception as e:
                if not is_stopped(): console.print(f"[red][{self.uid}] Error tcp_online: {e}[/red]")
                self.is_online = False
            for t in [self._animation_task, self._self_emote_task]:
                if t and not t.done(): t.cancel()
            if is_stopped(): break
            await asyncio.sleep(8)

    async def _animation_loop(self):
        while self.is_running and self.is_online:
            try:
                if is_stopped(): break
                with web_config_lock:
                    enabled = web_config.get("auto_animation", True)
                    interval = web_config.get("animation_interval_sec", 10)
                if not enabled or not self.online_writer or not self.bot_uid:
                    await asyncio.sleep(2); continue
                anim_id = random.choice(ANIMATION_POOL)
                pkt = await mahir_animation_packet(anim_id, self.key, self.iv)
                if pkt and self.online_writer and not self.online_writer.is_closing():
                    self.online_writer.write(pkt); await self.online_writer.drain()
                    console.print(f"[cyan]✨ [{self.uid}] Animasi ({anim_id})[/cyan]")
                await asyncio.sleep(max(5, int(interval)))
            except asyncio.CancelledError: break
            except: await asyncio.sleep(5)

    async def tcp_chat(self, ip, port, auth_token, key, iv, ready_event):
        while self.is_running:
            if is_stopped(): break
            try:
                reader, writer = await asyncio.open_connection(ip, int(port))
                writer.write(bytes.fromhex(auth_token)); await writer.drain()
                self.chat_reader, self.chat_writer = reader, writer
                ready_event.set()
                console.print(f"[cyan]ℹ [{self.uid}] CHAT Terhubung ✅[/cyan]")
                while self.is_running:
                    if is_stopped(): break
                    try:
                        data = await asyncio.wait_for(self.chat_reader.read(4096), timeout=5.0)
                        if not data: break
                        dh = data.hex()
                        if dh.startswith("1200"):
                            dec = DeCode_PackEt(dh[10:])
                            if dec:
                                try:
                                    pj = json.loads(dec)
                                    f5 = pj.get('5')
                                    if not isinstance(f5, dict): continue
                                    fd = f5.get('data')
                                    if not isinstance(fd, dict): continue
                                    mt = safe_get_str(fd.get('4')).strip()
                                    ci = safe_get_int(fd.get('2'))
                                    su = safe_get_int(fd.get('1'))
                                    f9 = safe_dict(fd.get('9'))
                                    sn = safe_get_str(f9.get('1'), "Player") if f9 else "Player"
                                    if not mt or not su: continue
                                    if str(su) == str(self.bot_uid): continue
                                    console.print(f"[cyan][{self.uid}][/cyan] [white]{sn}[/white]: [yellow]{mt}[/yellow]")
                                    await self.handle_team_command(mt, su, sn)
                                except: pass
                    except asyncio.TimeoutError: continue
                    except Exception: break
            except: pass
            if is_stopped(): break
            await asyncio.sleep(8)

    async def keep_online_forever(self):
        global online_count, BOT_OWN_ID
        while self.is_running:
            if is_stopped():
                console.print(f"[red]🛑 [{self.uid}] Dihentikan oleh pengguna[/red]"); break
            try:
                self.seen_restart_ts = get_restart_timestamp()
                self.tasks = []
                oi, at = await GeNeRaTeAccAccess(self.uid, self.password)
                if not oi: update_bot_info(self.uid, status="❌ Auth Gagal"); await asyncio.sleep(10); continue
                payload = await EncRypTMajoRLoGin(oi, at, FREEFIRE_VERSION_NAME)
                resp = await MajorLogin(payload)
                if not resp: update_bot_info(self.uid, status="❌ Login Gagal"); await asyncio.sleep(10); continue
                try: auth = await DecRypTMajoRLoGin(resp)
                except: update_bot_info(self.uid, status="❌ Dekripsi Gagal"); await asyncio.sleep(10); continue
                if not getattr(auth, 'token', None) or not getattr(auth, 'url', None):
                    update_bot_info(self.uid, status="❌ Auth Kosong"); await asyncio.sleep(10); continue
                ld = await GetLoginData(auth.url, payload, auth.token)
                if not ld: update_bot_info(self.uid, status="❌ Data Gagal"); await asyncio.sleep(10); continue
                from Pb2 import PorTs_pb2
                pd = PorTs_pb2.GetLoginData(); pd.ParseFromString(ld)
                self.key, self.iv = auth.key, auth.iv
                self.region, self.bot_uid = auth.region, auth.account_uid
                self.jwt_token = auth.token
                try: BOT_OWN_ID = int(auth.account_uid)
                except: pass
                en = extract_player_name(ld)
                if en and len(en) < 60: self.Nm = en
                else:
                    try:
                        dj = jwt.decode(auth.token, options={"verify_signature": False})
                        fb = dj.get('nickname')
                        self.Nm = str(fb) if fb and len(str(fb)) < 30 else f"Player_{str(auth.account_uid)[-4:]}"
                    except: self.Nm = f"Player_{str(auth.account_uid)[-4:]}"
                update_bot_info(self.uid, account_uid=str(auth.account_uid))
                oip, opp = pd.Online_IP_Port.split(":")
                cip, cpp = pd.AccountIP_Port.split(":")
                oa = create_auth_token_online(auth.account_uid, auth.token, auth.timestamp, auth.key, auth.iv)
                ca = create_auth_token_chat(auth.account_uid, auth.token, auth.timestamp, auth.key, auth.iv)
                if not oa or not ca: update_bot_info(self.uid, status="❌ Token Gagal"); await asyncio.sleep(10); continue
                console.print(f"[green]✔ Online: {self.Nm} | {self.region}[/green]")
                try: await equip_emote_on_login(auth.token, logger=lambda m: console.print(f"[cyan][{self.uid}] {m}[/cyan]"))
                except: pass
                with active_lock:
                    if not any(a['uid'] == self.uid for a in active_accounts):
                        online_count += 1
                        active_accounts.append({'uid': self.uid, 'bot_uid': str(auth.account_uid), 'name': self.Nm,
                            'region': self.region or 'BD', 'time': datetime.now().strftime('%H:%M:%S'),
                            'squad_id': 'Menunggu...', 'squad_members': '0/0'})
                update_bot_info(self.uid, status="✅ Online", account_uid=str(auth.account_uid), squad_active=True)
                ready = asyncio.Event()
                t1 = asyncio.create_task(self.tcp_chat(cip, cpp, ca, auth.key, auth.iv, ready))
                self.tasks.append(t1)
                await ready.wait()
                t2 = asyncio.create_task(self.tcp_online(oip, opp, oa))
                self.tasks.append(t2)
                monitor = asyncio.create_task(self._monitor_restart())
                try: await asyncio.gather(t1, t2, return_exceptions=True)
                finally:
                    if not monitor.done(): monitor.cancel()
            except Exception as e:
                if not is_stopped(): console.print(f"[red]❌ UID {self.uid} Error: {e}[/red]")
                update_bot_info(self.uid, status="❌ Error", squad_active=False)
            remove_active_account(self.uid)
            if is_stopped(): console.print(f"[red]🛑 [{self.uid}] Berhenti[/red]"); break
            if get_restart_timestamp() > self.seen_restart_ts:
                console.print(f"[green]♻️ [{self.uid}] Menyambung ulang...[/green]"); continue
            await asyncio.sleep(10)

    async def _monitor_restart(self):
        while self.is_running:
            await asyncio.sleep(2)
            if is_stopped():
                console.print(f"[red]🛑 [{self.uid}] Sinyal stop[/red]")
                for t in [self._animation_task, self._self_emote_task]:
                    if t and not t.done(): t.cancel()
                for t in self.tasks:
                    if not t.done(): t.cancel()
                return
            cur_ts = get_restart_timestamp()
            if cur_ts > self.seen_restart_ts:
                self.seen_restart_ts = cur_ts
                for t in [self._animation_task, self._self_emote_task]:
                    if t and not t.done(): t.cancel()
                for t in self.tasks:
                    if not t.done(): t.cancel()
                return

# ================================================================
#   WEB SERVER — DASHBOARD PREMIUM NM.CDX
# ================================================================
class BotHandler(BaseHTTPRequestHandler):
    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _text_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(data if isinstance(data, bytes) else data.encode('utf-8'))

    def _read_body(self):
        try:
            cl = int(self.headers.get('Content-Length', 0))
            return self.rfile.read(cl).decode('utf-8')
        except: return ""

    def _esc(self, s):
        return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with active_lock:
                cur_online, cur_total, cur_threads = online_count, total_accounts, len(active_accounts)
            with web_config_lock:
                cur_size = web_config.get("squad_size", 4)
                cur_recruit = web_config.get("world_recruit_count", 3)
                cur_recruit_type = web_config.get("world_recruit_type", "1")
                cur_lifetime = web_config.get("squad_lifetime_sec", 5)
                cur_auto = web_config.get("auto_recreate", True)
                rc_welcome = web_config.get("welcome_msg", DEFAULT_WELCOME_MSG)
                rc_join = web_config.get("auto_recruit_on_join", True)
                rc_leave = web_config.get("auto_recruit_on_leave", True)
                rc_delay = web_config.get("recruit_delay_sec", 1.5)
                rc_bundle = web_config.get("auto_bundle_on_join", True)
                rc_bundle_count = web_config.get("bundle_count_on_join", 2)
                cur_anim = web_config.get("auto_animation", True)
                cur_anim_int = web_config.get("animation_interval_sec", 10)
                cur_emote_join = web_config.get("auto_emote_on_join", True)
                cur_emote_delay = web_config.get("emote_join_delay_sec", 0.5)
                cur_kick_join = web_config.get("auto_kick_on_join", False)
                cur_kick_delay = web_config.get("kick_delay_sec", 1.0)
                kick_msg_raw = web_config.get("kick_msg", "")
                cur_welcome_join = web_config.get("auto_welcome_on_join", True)
                cur_welcome_delay = web_config.get("welcome_delay_sec", 0.5)
                cur_self_emote = web_config.get("bot_self_emote_enabled", False)
                cur_self_emote_int = web_config.get("bot_self_emote_interval", 8.0)
                join_emote_pool = list(web_config.get("join_emote_pool", DEFAULT_JOIN_EMOTES))
                self_emote_pool = list(web_config.get("bot_self_emote_pool", DEFAULT_JOIN_EMOTES))
            welcome_esc = self._esc(rc_welcome)
            kick_msg_esc = self._esc(kick_msg_raw)
            join_emote_csv = ",".join(str(x) for x in join_emote_pool)
            self_emote_csv = ",".join(str(x) for x in self_emote_pool)
            stopped_now = is_stopped()

            html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>NM.CDX · Squad Command Center</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23ffd76e'/%3E%3Cstop offset='100%25' stop-color='%23ff3d00'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='100' height='100' rx='24' fill='url(%23g)'/%3E%3Ctext x='50' y='74' font-family='Arial Black' font-size='62' font-weight='900' fill='%23100900' text-anchor='middle'%3EN%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&family=Cinzel:wght@700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
:root{{
  --bg:#05060c;--bg2:#0a0d1a;--panel:#0e1018;
  --line:rgba(255,255,255,0.06);--line2:rgba(255,255,255,0.1);
  --gold:#ffd76e;--gold2:#ffb800;--amber:#ff9500;--ember:#ff3d00;
  --emerald:#10b981;--emerald-lt:#34d399;--sky:#38bdf8;--violet:#a78bfa;--rose:#fb7185;--red:#ef4444;
  --t1:#f5f5f7;--t2:#a1a1aa;--t3:#71717a;--t4:#52525b;
  --r-xl:24px;--r-lg:18px;--r-md:13px;
  --sh1:0 4px 12px rgba(0,0,0,0.3);
  --sh2:0 12px 32px rgba(0,0,0,0.4);
}}
*{{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
body{{font-family:'Sora',sans-serif;background:var(--bg);color:var(--t1);min-height:100vh;overflow-x:hidden;-webkit-font-smoothing:antialiased;letter-spacing:-0.01em}}
body::before{{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 80% 50% at 15% 0%, rgba(255,184,0,0.10), transparent 55%),
    radial-gradient(ellipse 60% 50% at 90% 15%, rgba(255,106,0,0.08), transparent 55%),
    linear-gradient(180deg,#05060c,#0a0d1a 50%,#05060c);
}}
body::after{{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(255,184,0,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,184,0,0.025) 1px, transparent 1px);
  background-size:56px 56px;
  mask-image:radial-gradient(ellipse 90% 70% at 50% 40%, #000 20%, transparent 90%);
  -webkit-mask-image:radial-gradient(ellipse 90% 70% at 50% 40%, #000 20%, transparent 90%);
}}
.wrap{{position:relative;z-index:1;max-width:1560px;margin:0 auto;padding:24px}}
@keyframes pulseGold{{0%,100%{{box-shadow:0 0 24px rgba(255,184,0,0.35)}}50%{{box-shadow:0 0 40px rgba(255,184,0,0.6)}}}}
@keyframes radar{{0%{{transform:scale(0.5);opacity:1}}100%{{transform:scale(2.6);opacity:0}}}}
@keyframes lineSlide{{0%{{transform:translateX(-110%)}}100%{{transform:translateX(110%)}}}}
@keyframes shimmer{{0%{{background-position:200% 50%}}100%{{background-position:-200% 50%}}}}
@keyframes toastSlide{{from{{opacity:0;transform:translateX(60px) scale(0.9)}}to{{opacity:1;transform:translateX(0) scale(1)}}}}
@keyframes pulseRed{{0%,100%{{box-shadow:0 0 24px rgba(239,68,68,0.32)}}50%{{box-shadow:0 0 46px rgba(239,68,68,0.7)}}}}
@keyframes pulseGreen{{0%,100%{{box-shadow:0 0 24px rgba(16,185,129,0.32)}}50%{{box-shadow:0 0 46px rgba(16,185,129,0.7)}}}}

.topbar{{display:flex;align-items:center;justify-content:space-between;padding:24px 30px;background:linear-gradient(135deg,rgba(20,22,36,0.85),rgba(12,14,26,0.85));border:1px solid var(--line2);border-radius:var(--r-xl);backdrop-filter:blur(28px);box-shadow:var(--sh2);margin-bottom:26px;flex-wrap:wrap;gap:18px;position:relative;overflow:hidden}}
.topbar::before{{content:'';position:absolute;top:0;left:0;width:100%;height:1px;background:linear-gradient(90deg,transparent,var(--gold),var(--amber),var(--ember),transparent);animation:lineSlide 5s linear infinite}}
.brand{{display:flex;align-items:center;gap:18px;position:relative;z-index:1}}
.brand-mark{{width:62px;height:62px;border-radius:18px;background:linear-gradient(135deg,#ffd76e 0%,#ff9500 45%,#ff3d00 100%);display:flex;align-items:center;justify-content:center;font-family:'Cinzel',serif;font-size:28px;font-weight:900;color:#150900;box-shadow:0 8px 24px rgba(255,106,0,0.45),inset 0 2px 0 rgba(255,255,255,0.35);animation:pulseGold 3.5s ease-in-out infinite;flex-shrink:0}}
.brand-txt h1{{font-family:'Cinzel',serif;font-size:24px;font-weight:800;letter-spacing:0.08em;line-height:1.1;background:linear-gradient(120deg,#fff 0%,#ffd76e 40%,#ff9500 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.brand-txt .tag{{font-size:10.5px;font-weight:600;color:var(--t3);letter-spacing:0.28em;text-transform:uppercase;margin-top:5px}}
.chips{{display:flex;gap:8px;margin-top:9px;flex-wrap:wrap}}
.chip{{display:inline-flex;align-items:center;gap:7px;padding:4px 11px;border-radius:100px;font-size:10.5px;font-weight:700;letter-spacing:0.06em;background:rgba(255,255,255,0.03);border:1px solid var(--line2);color:var(--t2)}}
.chip.live{{background:rgba(16,185,129,0.1);border-color:rgba(16,185,129,0.35);color:var(--emerald-lt)}}
.chip.gold{{background:linear-gradient(135deg,rgba(255,215,110,0.12),rgba(255,106,0,0.08));border-color:rgba(255,184,0,0.4);color:var(--gold)}}
.chip.time{{font-family:'JetBrains Mono',monospace;font-weight:600;color:var(--sky);background:rgba(56,189,248,0.08);border-color:rgba(56,189,248,0.28)}}
.dot{{position:relative;width:7px;height:7px;border-radius:50%;background:currentColor;box-shadow:0 0 8px currentColor}}
.dot::after{{content:'';position:absolute;inset:-4px;border:2px solid currentColor;border-radius:50%;animation:radar 1.8s ease-out infinite}}
.tb-actions{{display:flex;gap:10px;flex-wrap:wrap;position:relative;z-index:1}}

.btn{{display:inline-flex;align-items:center;justify-content:center;gap:9px;padding:12px 20px;border-radius:var(--r-md);font-family:inherit;font-size:13px;font-weight:700;cursor:pointer;border:1px solid transparent;outline:none;user-select:none;white-space:nowrap;transition:all 0.25s cubic-bezier(0.34,1.56,0.64,1);position:relative;overflow:hidden}}
.btn:active{{transform:scale(0.95)}}
.btn-gold{{background:linear-gradient(135deg,#ffd76e 0%,#ff9500 50%,#ff5500 100%);color:#1a0800;box-shadow:0 6px 22px rgba(255,140,0,0.42);text-shadow:0 1px 0 rgba(255,255,255,0.25)}}
.btn-gold:hover{{transform:translateY(-2px);box-shadow:0 12px 32px rgba(255,140,0,0.55)}}
.btn-ghost{{background:rgba(255,255,255,0.03);border-color:var(--line2);color:var(--t1)}}
.btn-ghost:hover{{background:rgba(255,184,0,0.08);border-color:rgba(255,184,0,0.4);color:var(--gold);transform:translateY(-2px)}}
.btn-green{{background:linear-gradient(135deg,#34d399,#10b981);color:#062e1e;box-shadow:0 6px 22px rgba(16,185,129,0.4)}}
.btn-red{{background:linear-gradient(135deg,#f87171,#ef4444);color:#fff;box-shadow:0 6px 22px rgba(239,68,68,0.4)}}
.btn-amber{{background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#1a1200;box-shadow:0 6px 22px rgba(245,158,11,0.4)}}
.btn-pink{{background:linear-gradient(135deg,#ec4899,#be185d);color:#fff;box-shadow:0 6px 22px rgba(236,72,153,0.4)}}
.btn-blue{{background:linear-gradient(135deg,#38bdf8,#0284c7);color:#fff;box-shadow:0 6px 22px rgba(56,189,248,0.4)}}
.btn:disabled{{opacity:0.55;cursor:not-allowed}}

.stats{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-bottom:22px}}
.stat{{position:relative;padding:22px;background:linear-gradient(150deg,rgba(22,22,34,0.9),rgba(14,14,22,0.95));border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;transition:all 0.35s;box-shadow:var(--sh1);color:var(--gold)}}
.stat::before{{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:linear-gradient(90deg,transparent,currentColor,transparent);opacity:0.5}}
.stat::after{{content:'';position:absolute;bottom:-50px;right:-50px;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,currentColor 0%,transparent 65%);opacity:0.06}}
.stat:hover{{transform:translateY(-5px);border-color:rgba(255,184,0,0.3);box-shadow:0 20px 48px -14px rgba(255,140,0,0.22),var(--sh2)}}
.stat.emerald{{color:var(--emerald-lt)}}
.stat.sky{{color:var(--sky)}}
.stat.violet{{color:var(--violet)}}
.stat-row{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}}
.stat-ico{{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:17px;background:linear-gradient(135deg,rgba(255,184,0,0.14),rgba(255,106,0,0.08));border:1px solid rgba(255,184,0,0.3);color:var(--gold)}}
.stat.emerald .stat-ico{{background:linear-gradient(135deg,rgba(16,185,129,0.14),rgba(5,150,105,0.08));border-color:rgba(16,185,129,0.32);color:var(--emerald-lt)}}
.stat.sky .stat-ico{{background:linear-gradient(135deg,rgba(56,189,248,0.14),rgba(14,165,233,0.08));border-color:rgba(56,189,248,0.32);color:var(--sky)}}
.stat.violet .stat-ico{{background:linear-gradient(135deg,rgba(167,139,250,0.14),rgba(139,92,246,0.08));border-color:rgba(167,139,250,0.32);color:var(--violet)}}
.stat-badge{{font-family:'JetBrains Mono',monospace;font-size:9.5px;font-weight:700;padding:3px 9px;border-radius:100px;background:rgba(255,255,255,0.04);border:1px solid var(--line2);color:var(--t3);letter-spacing:0.08em}}
.stat-badge.good{{color:var(--emerald-lt);border-color:rgba(16,185,129,0.35);background:rgba(16,185,129,0.08)}}
.stat-val{{font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:800;line-height:1;letter-spacing:-0.03em;color:#fff;margin-bottom:8px}}
.stat-lbl{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;color:var(--t3)}}

.panel{{background:linear-gradient(180deg,rgba(20,20,32,0.7),rgba(12,12,20,0.85));border:1px solid var(--line);border-radius:var(--r-xl);backdrop-filter:blur(20px);box-shadow:var(--sh2);overflow:hidden;margin-bottom:22px;position:relative}}
.panel::before{{content:'';position:absolute;top:0;left:0;width:100%;height:1px;background:linear-gradient(90deg,transparent,rgba(255,184,0,0.4),transparent)}}
.panel-head{{padding:22px 26px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:linear-gradient(180deg,rgba(255,184,0,0.025),transparent)}}
.panel-title{{display:flex;align-items:center;gap:14px}}
.panel-ico{{width:40px;height:40px;border-radius:11px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,rgba(255,184,0,0.16),rgba(255,106,0,0.08));border:1px solid rgba(255,184,0,0.3);color:var(--gold);font-size:15px}}
.panel-ico.emerald{{background:linear-gradient(135deg,rgba(16,185,129,0.16),rgba(5,150,105,0.08));border-color:rgba(16,185,129,0.32);color:var(--emerald-lt)}}
.panel-ico.pink{{background:linear-gradient(135deg,rgba(236,72,153,0.16),rgba(190,24,93,0.08));border-color:rgba(236,72,153,0.32);color:#f9a8d4}}
.panel-ico.sky{{background:linear-gradient(135deg,rgba(56,189,248,0.16),rgba(14,165,233,0.08));border-color:rgba(56,189,248,0.32);color:var(--sky)}}
.panel-ico.red{{background:linear-gradient(135deg,rgba(239,68,68,0.16),rgba(185,28,28,0.08));border-color:rgba(239,68,68,0.32);color:#f87171}}
.panel-title h2{{font-size:16.5px;font-weight:800;letter-spacing:-0.02em;color:#fff}}
.panel-title .sub{{font-size:11px;color:var(--t3);font-weight:500;margin-top:3px}}
.pill{{font-family:'JetBrains Mono',monospace;font-size:11.5px;font-weight:700;padding:6px 14px;border-radius:100px;background:linear-gradient(135deg,rgba(255,215,110,0.12),rgba(255,106,0,0.08));border:1px solid rgba(255,184,0,0.35);color:var(--gold)}}
.panel-body{{padding:22px 26px}}

.actions{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}}
.action-btn{{display:flex;align-items:center;justify-content:flex-start;gap:16px;padding:20px 22px;border-radius:14px;min-height:82px;cursor:pointer;border:1px solid rgba(255,255,255,0.12);color:#fff;font-weight:700;transition:all 0.28s;text-align:left}}
.action-btn:hover{{transform:translateY(-3px);border-color:rgba(255,255,255,0.3);box-shadow:0 14px 36px rgba(0,0,0,0.4)}}
.action-btn.stop{{background:linear-gradient(135deg,#ef4444,#7f1d1d);animation:pulseRed 2.4s infinite}}
.action-btn.start{{background:linear-gradient(135deg,#10b981,#065f46);animation:pulseGreen 2.4s infinite}}
.action-btn.amber{{background:linear-gradient(135deg,#ff9500,#c2410c)}}
.action-btn.pink{{background:linear-gradient(135deg,#ec4899,#9d174d)}}
.action-btn .a-ico{{font-size:1.7em;flex-shrink:0}}
.action-btn .a-txt{{display:flex;flex-direction:column;gap:3px;min-width:0}}
.action-btn .a-main{{font-family:'JetBrains Mono',monospace;font-size:0.9em;font-weight:900;letter-spacing:1.2px;text-transform:uppercase}}
.action-btn .a-sub{{font-size:0.72em;font-weight:600;opacity:0.85}}

.field{{margin-bottom:16px}}
.field label{{display:block;font-size:11px;font-weight:800;color:var(--t2);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.14em}}
.field input,.field textarea,.field select{{width:100%;padding:13px 17px;background:rgba(6,6,10,0.7);border:1px solid var(--line2);border-radius:var(--r-md);color:var(--t1);font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:500;outline:none;transition:all 0.25s}}
.field input:focus,.field textarea:focus,.field select:focus{{border-color:rgba(255,184,0,0.55);background:rgba(255,184,0,0.05);box-shadow:0 0 0 4px rgba(255,184,0,0.1)}}
.field textarea{{resize:vertical;line-height:1.7;font-size:12.5px}}
.field select{{cursor:pointer;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23ffb800' d='M6 8.5L1.5 4h9z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 16px center;padding-right:40px}}
.field select option{{background:#0a0a12;color:#fff}}
.field input[type="file"]{{cursor:pointer;border-style:dashed;color:var(--t2);font-family:'Sora',sans-serif;font-weight:600}}
.field input[type="file"]:hover{{border-color:#f9a8d4;color:#f9a8d4}}

.chips-row{{display:flex;flex-wrap:wrap;gap:10px}}
.chip-tog{{display:inline-flex;align-items:center;gap:10px;padding:11px 15px;border-radius:12px;border:1px solid var(--line2);background:rgba(6,6,10,0.6);color:var(--t2);font-weight:600;font-size:0.85em;cursor:pointer;user-select:none;transition:all 0.24s}}
.chip-tog:hover{{border-color:var(--gold);background:rgba(255,184,0,0.08);color:var(--t1);transform:translateY(-2px)}}
.chip-tog:has(input:checked){{border-color:var(--gold);background:linear-gradient(135deg,rgba(255,215,110,0.14),rgba(255,106,0,0.1));color:var(--t1);box-shadow:0 0 22px rgba(255,184,0,0.22)}}
.chip-tog input{{width:16px;height:16px;accent-color:var(--gold);cursor:pointer}}

.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr auto;gap:12px;align-items:end}}

.acc-box{{padding:20px;border-radius:14px;border:1px solid var(--line);background:linear-gradient(135deg,rgba(6,6,10,0.5),rgba(15,22,40,0.4))}}
.acc-box.gold{{border-color:rgba(255,184,0,0.3)}}
.acc-box.pink{{border-color:rgba(236,72,153,0.3)}}
.acc-box.sky{{border-color:rgba(56,189,248,0.3)}}
.acc-box.violet{{border-color:rgba(167,139,250,0.3)}}
.acc-box.emerald{{border-color:rgba(16,185,129,0.3)}}
.box-title{{display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;font-size:0.85em;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:14px}}
.box-title.gold{{color:var(--gold)}}
.box-title.pink{{color:#f9a8d4}}
.box-title.sky{{color:var(--sky)}}
.box-title.violet{{color:var(--violet)}}
.box-title.emerald{{color:var(--emerald-lt)}}
.hint{{color:var(--t4);font-size:0.76em;line-height:1.65;margin-top:6px}}
.hint b{{color:var(--amber)}}
.hint code{{background:rgba(167,139,250,0.15);color:#c4b5fd;padding:2px 7px;border-radius:5px;font-family:'JetBrains Mono',monospace;font-size:0.9em}}

.table-wrap{{overflow-x:auto;max-height:520px;overflow-y:auto;border-radius:12px;border:1px solid var(--line);background:rgba(6,6,10,0.55)}}
table{{width:100%;border-collapse:collapse;text-align:left}}
th,td{{padding:14px 16px;border-bottom:1px solid var(--line);font-size:0.86em;white-space:nowrap}}
th{{position:sticky;top:0;background:linear-gradient(180deg,rgba(24,24,38,0.98),rgba(14,14,22,0.98));color:var(--gold);font-family:'JetBrains Mono',monospace;font-size:0.7em;font-weight:700;letter-spacing:1.6px;text-transform:uppercase}}
tbody tr:hover{{background:rgba(255,184,0,0.06)}}
.badge-live{{display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border-radius:100px;background:rgba(16,185,129,0.14);color:var(--emerald-lt);font-size:0.7em;font-weight:700;letter-spacing:1px;border:1px solid rgba(16,185,129,0.35)}}
.badge-live::before{{content:'';width:6px;height:6px;border-radius:50%;background:var(--emerald-lt);box-shadow:0 0 8px var(--emerald-lt);animation:radar 1.6s infinite}}
.empty-row td{{text-align:center;padding:44px 20px;color:var(--t4);font-style:italic}}

.log-box{{height:420px;overflow-y:auto;padding:18px;border-radius:12px;border:1px solid rgba(255,184,0,0.12);background:#04040a;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.8;color:#34d399}}
.log-box::-webkit-scrollbar{{width:9px}}
.log-box::-webkit-scrollbar-thumb{{background:linear-gradient(180deg,rgba(255,184,0,0.35),rgba(255,106,0,0.25));border-radius:5px}}
.log-box > div{{padding:3px 10px;border-left:2px solid transparent;word-break:break-word}}
.log-box > div:hover{{background:rgba(255,184,0,0.06);border-left-color:var(--gold)}}

.banner{{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:14px;padding:18px 24px;border-radius:var(--r-lg);margin-bottom:22px;font-family:'JetBrains Mono',monospace;font-weight:900;letter-spacing:3px;font-size:1em;color:#fff;border:1px solid rgba(255,255,255,0.15);text-transform:uppercase;transition:background 0.4s}}
.banner::after{{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.2),transparent);animation:lineSlide 3.5s linear infinite;pointer-events:none}}

.foot{{text-align:center;padding:26px;color:var(--t4);font-size:0.8em;letter-spacing:1.6px;border-top:1px solid var(--line);margin-top:14px}}
.foot b{{color:var(--gold)}}

.toasts{{position:fixed;top:24px;right:24px;z-index:500;display:flex;flex-direction:column;gap:10px;pointer-events:none;max-width:400px}}
.toast{{background:linear-gradient(135deg,#14141f,#0a0a12);border:1px solid var(--line2);border-radius:var(--r-md);padding:14px 18px;font-size:13px;font-weight:600;box-shadow:0 16px 40px rgba(0,0,0,0.65);display:flex;align-items:center;gap:12px;pointer-events:auto;animation:toastSlide 0.35s cubic-bezier(0.34,1.56,0.64,1);color:#fff;max-width:400px}}
.toast.success{{border-color:rgba(16,185,129,0.5);color:var(--emerald-lt)}}
.toast.error{{border-color:rgba(239,68,68,0.5);color:#f87171}}
.toast.info{{border-color:rgba(56,189,248,0.5);color:var(--sky)}}
.toast.warn{{border-color:rgba(245,158,11,0.5);color:#fbbf24}}
.t-ico{{width:32px;height:32px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;background:rgba(255,255,255,0.05);border:1px solid var(--line2)}}

.sb-links{{display:flex;gap:8px;overflow-x:auto;padding:12px 0;margin-bottom:14px;border-bottom:1px solid var(--line);scrollbar-width:none}}
.sb-links::-webkit-scrollbar{{display:none}}
.sb-link{{flex-shrink:0;padding:8px 16px;border-radius:100px;background:rgba(255,255,255,0.03);border:1px solid var(--line2);color:var(--t2);font-size:12px;font-weight:700;cursor:pointer;text-decoration:none;transition:all 0.22s}}
.sb-link:hover{{background:rgba(255,184,0,0.08);color:var(--gold);border-color:rgba(255,184,0,0.4)}}
.sb-link.active{{background:linear-gradient(135deg,rgba(255,215,110,0.16),rgba(255,106,0,0.1));color:var(--gold);border-color:rgba(255,184,0,0.5)}}

@media (max-width:1024px){{.stats{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media (max-width:768px){{
  .wrap{{padding:14px}}
  .topbar{{padding:18px}}
  .brand-mark{{width:48px;height:48px;font-size:22px;border-radius:14px}}
  .brand-txt h1{{font-size:18px}}
  .brand-txt .tag{{font-size:9px;letter-spacing:0.2em}}
  .grid2,.grid3{{grid-template-columns:1fr}}
  .stats{{grid-template-columns:1fr 1fr;gap:10px}}
  .stat{{padding:16px;border-radius:14px}}
  .stat-ico{{width:38px;height:38px;font-size:15px}}
  .stat-val{{font-size:20px}}
  .stat-lbl{{font-size:9.5px;letter-spacing:0.1em}}
  .panel-head{{padding:16px 18px}}
  .panel-body{{padding:18px}}
  .toasts{{top:12px;left:12px;right:12px;max-width:none}}
  .toast{{max-width:100%}}
  .action-btn{{min-height:70px;padding:16px 18px}}
  .action-btn .a-ico{{font-size:1.4em}}
  .action-btn .a-main{{font-size:0.85em}}
}}
</style>
</head>
<body>

<div class="toasts" id="toasts"></div>

<div class="wrap">
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark">N</div>
      <div class="brand-txt">
        <h1>NM.CDX</h1>
        <p class="tag">SQUAD COMMAND CENTER</p>
        <div class="chips">
          <span class="chip live"><span class="dot"></span> SISTEM AKTIF</span>
          <span class="chip gold"><i class="fa-solid fa-users"></i> BOT SQUAD</span>
          <span class="chip time"><i class="fa-regular fa-clock"></i> <span id="uptimeTop">00:00:00</span></span>
        </div>
      </div>
    </div>
    <div class="tb-actions">
      <button class="btn btn-ghost" onclick="doRefresh()"><i class="fa-solid fa-rotate"></i> Segarkan</button>
      <button class="btn btn-ghost" onclick="doRestartAll()"><i class="fa-solid fa-power-off"></i> Restart Akun</button>
      <button class="btn btn-gold" onclick="doSquadRecreate()"><i class="fa-solid fa-sync"></i> Recreate Squad</button>
    </div>
  </header>

  <div class="banner" id="banner" style="background:{'linear-gradient(135deg,#ef4444,#7f1d1d)' if stopped_now else 'linear-gradient(135deg,#10b981,#065f46)'};">
    <span id="bannerTxt">{'🛑 BOT DIHENTIKAN' if stopped_now else '🟢 BOT BERJALAN'}</span>
  </div>

  <section class="panel">
    <div class="panel-head">
      <div class="panel-title">
        <div class="panel-ico"><i class="fa-solid fa-bolt"></i></div>
        <div><h2>Aksi Cepat</h2><div class="sub">Kontrol semua bot dalam sekali klik</div></div>
      </div>
      <span class="pill"><span class="dot"></span> LIVE</span>
    </div>
    <div class="panel-body">
      <div class="actions">
        <button class="btn action-btn stop" id="btnStopAll" onclick="doStopAll()" style="display:{'none' if stopped_now else 'flex'};">
          <span class="a-ico">🛑</span>
          <span class="a-txt"><span class="a-main">Stop Semua Bot</span><span class="a-sub">Putuskan semua bot</span></span>
        </button>
        <button class="btn action-btn start" id="btnStartAll" onclick="doStartAll()" style="display:{'flex' if stopped_now else 'none'};">
          <span class="a-ico">🚀</span>
          <span class="a-txt"><span class="a-main">Start Semua Bot</span><span class="a-sub">Jalankan ulang bot</span></span>
        </button>
        <button class="btn action-btn amber" onclick="doRestartAll()">
          <span class="a-ico">♻️</span>
          <span class="a-txt"><span class="a-main">Restart Akun</span><span class="a-sub">Reconnect semua bot</span></span>
        </button>
        <button class="btn action-btn pink" onclick="doSquadRecreate()">
          <span class="a-ico">🔄</span>
          <span class="a-txt"><span class="a-main">Recreate Squad</span><span class="a-sub">Bentuk ulang setiap squad</span></span>
        </button>
      </div>
    </div>
  </section>

  <section class="stats">
    <div class="stat emerald">
      <div class="stat-row"><div class="stat-ico"><i class="fa-solid fa-signal"></i></div><span class="stat-badge good" id="stat-threads-badge">0 Aktif</span></div>
      <div class="stat-val"><span id="stat-online">{cur_online}</span></div>
      <div class="stat-lbl">Bot Online</div>
    </div>
    <div class="stat sky">
      <div class="stat-row"><div class="stat-ico"><i class="fa-solid fa-users"></i></div><span class="stat-badge">TOTAL</span></div>
      <div class="stat-val"><span id="stat-total">{cur_total}</span></div>
      <div class="stat-lbl">Total Akun</div>
    </div>
    <div class="stat violet">
      <div class="stat-row"><div class="stat-ico"><i class="fa-solid fa-server"></i></div><span class="stat-badge">THREAD</span></div>
      <div class="stat-val"><span id="stat-threads">{cur_threads}</span></div>
      <div class="stat-lbl">Thread Aktif</div>
    </div>
    <div class="stat">
      <div class="stat-row"><div class="stat-ico"><i class="fa-solid fa-cube"></i></div><span class="stat-badge good">{CURRENT_OB}</span></div>
      <div class="stat-val" style="font-size:16px;"><span id="stat-version">{FREEFIRE_VERSION_NAME}</span></div>
      <div class="stat-lbl">Versi Game</div>
    </div>
  </section>

  <div class="sb-links">
    <a class="sb-link active" href="#sec-akun" onclick="navTo(this)">👥 Akun</a>
    <a class="sb-link" href="#sec-squad" onclick="navTo(this)">⚙️ Squad</a>
    <a class="sb-link" href="#sec-emote" onclick="navTo(this)">🎭 Emote</a>
    <a class="sb-link" href="#sec-bot" onclick="navTo(this)">📋 Bot Aktif</a>
    <a class="sb-link" href="#sec-log" onclick="navTo(this)">📜 Log</a>
  </div>

  <section class="panel" id="sec-akun">
    <div class="panel-head">
      <div class="panel-title">
        <div class="panel-ico emerald"><i class="fa-solid fa-users"></i></div>
        <div><h2>Manajer Akun</h2><div class="sub">Tambah, edit, dan kelola semua akun</div></div>
      </div>
      <span class="pill" id="acc-count-pill">0 Akun</span>
    </div>
    <div class="panel-body" style="display:flex;flex-direction:column;gap:16px;">
      <div class="acc-box gold">
        <div class="box-title gold"><i class="fa-solid fa-plus"></i> Tambah Akun Tunggal</div>
        <div class="grid3">
          <div class="field" style="margin:0;"><label>UID</label><input type="text" id="new-uid" placeholder="contoh: 1234567890"></div>
          <div class="field" style="margin:0;"><label>Password</label><input type="text" id="new-pwd" placeholder="Password akun"></div>
          <button class="btn btn-green" onclick="addSingleAccount()" style="height:47px;"><i class="fa-solid fa-plus"></i> Tambah</button>
        </div>
      </div>
      <div class="acc-box pink">
        <div class="box-title pink"><i class="fa-solid fa-file-import"></i> Upload TXT (Massal)</div>
        <div class="hint">Format: setiap baris <b>uid:password</b> atau <b>uid|password</b></div>
        <div class="grid2" style="grid-template-columns:1fr auto;margin-top:10px;">
          <input type="file" id="acc-file" accept=".txt">
          <button class="btn btn-pink" onclick="uploadAccFile()"><i class="fa-solid fa-cloud-arrow-up"></i> Upload</button>
        </div>
      </div>
      <div class="acc-box violet">
        <div class="box-title violet"><i class="fa-solid fa-pen-to-square"></i> Edit / Lihat Semua Akun</div>
        <textarea id="acc-content" style="height:240px;color:#34d399;background:#04040a;" spellcheck="false"></textarea>
        <div class="hint">Format: <b>uid:password</b> per baris · <code>#</code> untuk komentar</div>
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:14px;">
          <button class="btn btn-green" onclick="saveAllAccounts()" id="acc-save-btn"><i class="fa-solid fa-floppy-disk"></i> Simpan</button>
          <button class="btn btn-amber" onclick="reloadAccounts()"><i class="fa-solid fa-rotate"></i> Muat Ulang</button>
          <button class="btn btn-blue" onclick="downloadAccounts()"><i class="fa-solid fa-download"></i> Unduh</button>
        </div>
      </div>
    </div>
  </section>

  <section class="panel" id="sec-squad">
    <div class="panel-head">
      <div class="panel-title">
        <div class="panel-ico"><i class="fa-solid fa-users-gear"></i></div>
        <div><h2>Konfigurasi Squad</h2><div class="sub">Pengaturan otomatisasi bot squad</div></div>
      </div>
      <span class="pill"><span class="dot"></span> Auto Save</span>
    </div>
    <div class="panel-body">
      <form id="squad-form" onsubmit="saveSquadConfig(event)">
        <div class="field">
          <label>👥 Ukuran Squad</label>
          <div class="chips-row">
            <label class="chip-tog"><input type="radio" name="squad_size" value="3" {'checked' if cur_size==3 else ''}><span>4 Pemain</span></label>
            <label class="chip-tog"><input type="radio" name="squad_size" value="4" {'checked' if cur_size==4 else ''}><span>5 Pemain</span></label>
            <label class="chip-tog"><input type="radio" name="squad_size" value="5" {'checked' if cur_size==5 else ''}><span>6 Pemain</span></label>
          </div>
        </div>
        <div class="field">
          <label>📢 Tipe Recruit Dunia</label>
          <div class="chips-row">
            <label class="chip-tog"><input type="radio" name="world_recruit_type" value="1" {'checked' if cur_recruit_type=="1" else ''}><span>Tipe 1</span></label>
            <label class="chip-tog"><input type="radio" name="world_recruit_type" value="2" {'checked' if cur_recruit_type=="2" else ''}><span>Tipe 2</span></label>
            <label class="chip-tog"><input type="radio" name="world_recruit_type" value="half" {'checked' if cur_recruit_type=="half" else ''}><span>Setengah</span></label>
            <label class="chip-tog"><input type="radio" name="world_recruit_type" value="random" {'checked' if cur_recruit_type=="random" else ''}><span>Acak</span></label>
          </div>
        </div>
        <div class="grid2">
          <div class="field"><label>📢 Jumlah Recruit</label><input type="number" min="1" max="10" id="world_recruit_count" value="{cur_recruit}"></div>
          <div class="field"><label>⏱️ Umur Squad (detik)</label><input type="number" min="5" max="3600" id="squad_lifetime_sec" value="{cur_lifetime}"></div>
        </div>
        <div class="grid2">
          <div class="field"><label>✨ Interval Animasi (detik)</label><input type="number" min="5" max="300" id="animation_interval_sec" value="{cur_anim_int}"></div>
          <div class="field"><label>👗 Jumlah Bundle</label><input type="number" min="1" max="5" id="bundle_count_on_join" value="{rc_bundle_count}"></div>
        </div>
        <div class="grid2">
          <div class="field"><label>⏱️ Jeda Recruit (detik)</label><input type="number" min="0.5" max="30" step="0.5" id="recruit_delay_sec" value="{rc_delay}"></div>
          <div class="field"><label>🎭 Jeda Emote (detik)</label><input type="number" min="0.1" max="30" step="0.1" id="emote_join_delay_sec" value="{cur_emote_delay}"></div>
        </div>
        <div class="grid2">
          <div class="field"><label>💬 Jeda Sambutan (detik)</label><input type="number" min="0.1" max="30" step="0.1" id="welcome_delay_sec" value="{cur_welcome_delay}"></div>
          <div class="field"><label>🚫 Jeda Kick (detik)</label><input type="number" min="0.1" max="30" step="0.1" id="kick_delay_sec" value="{cur_kick_delay}"></div>
        </div>
        <div class="field"><label>🚫 Pesan Kick</label><input type="text" id="kick_msg" value="{kick_msg_esc}"></div>
        <div class="field">
          <label>🔧 Fitur Otomatis</label>
          <div class="chips-row">
            <label class="chip-tog"><input type="checkbox" id="auto_recreate_chk" {'checked' if cur_auto else ''}><span>🔁 Auto Recreate</span></label>
            <label class="chip-tog"><input type="checkbox" id="auto_recruit_on_join_chk" {'checked' if rc_join else ''}><span>🟢 Recruit Join</span></label>
            <label class="chip-tog"><input type="checkbox" id="auto_recruit_on_leave_chk" {'checked' if rc_leave else ''}><span>🔴 Recruit Leave</span></label>
            <label class="chip-tog"><input type="checkbox" id="auto_bundle_on_join_chk" {'checked' if rc_bundle else ''}><span>👗 Bundle Join</span></label>
            <label class="chip-tog"><input type="checkbox" id="auto_emote_on_join_chk" {'checked' if cur_emote_join else ''}><span>🎭 Emote Join</span></label>
            <label class="chip-tog"><input type="checkbox" id="auto_animation_chk" {'checked' if cur_anim else ''}><span>✨ Animasi</span></label>
            <label class="chip-tog"><input type="checkbox" id="auto_welcome_on_join_chk" {'checked' if cur_welcome_join else ''}><span>💬 Sambutan</span></label>
            <label class="chip-tog"><input type="checkbox" id="auto_kick_on_join_chk" {'checked' if cur_kick_join else ''}><span>🚫 Auto Kick</span></label>
          </div>
        </div>
        <div class="field">
          <label>💬 Pesan Sambutan</label>
          <textarea id="welcome_msg_ta" style="height:170px;color:#fbbf24;" spellcheck="false">{welcome_esc}</textarea>
          <div class="hint">Placeholder: <b>{{user_name}}</b></div>
        </div>
        <button type="submit" class="btn btn-green" id="squad-save-btn" style="width:100%;padding:15px;"><i class="fa-solid fa-floppy-disk"></i> Simpan Konfigurasi Squad</button>
      </form>
    </div>
  </section>

  <section class="panel" id="sec-emote">
    <div class="panel-head">
      <div class="panel-title">
        <div class="panel-ico pink"><i class="fa-solid fa-face-grin-stars"></i></div>
        <div><h2>Manajer Emote</h2><div class="sub">Emote saat join & emote sendiri</div></div>
      </div>
      <span class="pill"><span class="dot"></span> Bisa Diedit</span>
    </div>
    <div class="panel-body" style="display:flex;flex-direction:column;gap:16px;">
      <div class="acc-box sky">
        <div class="box-title sky"><i class="fa-solid fa-face-laugh-squint"></i> Kumpulan Emote Join</div>
        <div class="hint">Saat member join, salah satu emote ini dipilih acak. Pisahkan dengan koma.</div>
        <textarea id="join_emote_pool" style="height:80px;color:#38bdf8;margin-top:10px;" spellcheck="false" placeholder="909049013,909045010,909000020">{join_emote_csv}</textarea>
        <div class="hint">Contoh: <code>909049013, 909045010, 909000020</code></div>
      </div>
      <div class="acc-box emerald">
        <div class="box-title emerald"><i class="fa-solid fa-robot"></i> Emote Sendiri Bot</div>
        <div class="hint">Bot akan mengirim emote ke dirinya sendiri secara berkala.</div>
        <div class="chips-row" style="margin-top:10px;">
          <label class="chip-tog"><input type="checkbox" id="bot_self_emote_enabled" {'checked' if cur_self_emote else ''}><span>🤖 Aktifkan</span></label>
        </div>
        <div class="field" style="margin-top:12px;">
          <label>⏱️ Interval (detik)</label>
          <input type="number" min="1" max="300" step="0.5" id="bot_self_emote_interval" value="{cur_self_emote_int}">
        </div>
        <div class="field" style="margin-top:12px;">
          <label>🎭 Kumpulan Emote Sendiri</label>
          <textarea id="bot_self_emote_pool" style="height:80px;color:#34d399;" spellcheck="false" placeholder="909049013,909045010">{self_emote_csv}</textarea>
        </div>
      </div>
      <button type="button" class="btn btn-pink" onclick="saveEmotePool()" id="emote-save-btn" style="padding:15px;width:100%;"><i class="fa-solid fa-floppy-disk"></i> Simpan Emote</button>
    </div>
  </section>

  <section class="panel" id="sec-bot">
    <div class="panel-head">
      <div class="panel-title">
        <div class="panel-ico sky"><i class="fa-solid fa-list"></i></div>
        <div><h2>Bot Aktif</h2><div class="sub">Daftar bot yang sedang berjalan</div></div>
      </div>
      <span class="pill"><span class="dot"></span> LIVE</span>
    </div>
    <div class="panel-body" style="padding-top:0;">
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>UID Bot</th><th>UID</th><th>Nama</th><th>Region</th>
            <th>ID Squad</th><th>Anggota</th><th>Waktu</th><th>Status</th>
          </tr></thead>
          <tbody id="accounts-tbody">
            <tr class="empty-row"><td colspan="8">🔄 Memuat...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="panel" id="sec-log">
    <div class="panel-head">
      <div class="panel-title">
        <div class="panel-ico red"><i class="fa-solid fa-terminal"></i></div>
        <div><h2>Log Live</h2><div class="sub">Streaming aktivitas bot</div></div>
      </div>
      <div style="display:flex;gap:10px;align-items:center;">
        <button class="btn btn-ghost" onclick="clearLogView()" style="padding:9px 16px;font-size:12px;"><i class="fa-solid fa-trash"></i> Bersihkan</button>
        <span class="pill"><span class="dot"></span> Auto-Sync</span>
      </div>
    </div>
    <div class="panel-body" style="padding-top:0;">
      <div id="live-log" class="log-box">📡 Menunggu log...</div>
    </div>
  </section>

  <footer class="foot">© 2026 <b>NM.CDX</b> · Squad Command Center · Premium Edition</footer>
</div>

<script>
let CURRENT_STOPPED = {str(stopped_now).lower()};

function navTo(el){{
  document.querySelectorAll('.sb-link').forEach(a => a.classList.remove('active'));
  el.classList.add('active');
}}
function toast(msg, type='info'){{
  const w = document.getElementById('toasts');
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  const icons = {{success:'fa-circle-check', error:'fa-circle-exclamation', warn:'fa-triangle-exclamation', info:'fa-circle-info'}};
  t.innerHTML = `<div class="t-ico"><i class="fa-solid ${{icons[type]||icons.info}}"></i></div><span>${{msg}}</span>`;
  w.appendChild(t);
  setTimeout(() => {{
    t.style.opacity = '0'; t.style.transform = 'translateX(60px)';
    t.style.transition = 'all 0.3s'; setTimeout(() => t.remove(), 320);
  }}, 3400);
}}
async function doStopAll(){{
  if (!confirm('🛑 Stop SEMUA bot?')) return;
  const b = document.getElementById('btnStopAll'); b.disabled = true;
  try {{
    const r = await fetch('/stop_all_bots', {{method:'POST'}});
    if (r.ok) {{ toast('🛑 Semua bot dihentikan!', 'error'); await refreshStatus(); }}
  }} catch(e) {{ toast('❌ Error', 'error'); }}
  b.disabled = false;
}}
async function doStartAll(){{
  if (!confirm('🚀 Start SEMUA bot?')) return;
  const b = document.getElementById('btnStartAll'); b.disabled = true;
  try {{
    const r = await fetch('/start_all_bots', {{method:'POST'}});
    if (r.ok) {{ toast('🚀 Semua bot dijalankan!', 'success'); await refreshStatus(); }}
  }} catch(e) {{ toast('❌ Error', 'error'); }}
  b.disabled = false;
}}
async function refreshStatus(){{
  try {{
    const r = await fetch('/api/status');
    if (!r.ok) return;
    const d = await r.json();
    CURRENT_STOPPED = d.stopped;
    updateStatusUI();
  }} catch(e) {{}}
}}
function updateStatusUI(){{
  const banner = document.getElementById('banner');
  const txt = document.getElementById('bannerTxt');
  const sb = document.getElementById('btnStopAll');
  const stb = document.getElementById('btnStartAll');
  if (CURRENT_STOPPED) {{
    txt.innerText = '🛑 BOT DIHENTIKAN';
    banner.style.background = 'linear-gradient(135deg,#ef4444,#7f1d1d)';
    sb.style.display = 'none'; stb.style.display = 'flex';
  }} else {{
    txt.innerText = '🟢 BOT BERJALAN';
    banner.style.background = 'linear-gradient(135deg,#10b981,#065f46)';
    sb.style.display = 'flex'; stb.style.display = 'none';
  }}
}}
async function doRestartAll(){{
  if (!confirm('♻️ Restart SEMUA akun?')) return;
  try {{
    const r = await fetch('/restart_accounts', {{method:'POST'}});
    if (r.ok) toast('♻️ Restart dijalankan!', 'warn');
  }} catch(e) {{ toast('❌ Error', 'error'); }}
}}
async function doSquadRecreate(){{
  if (!confirm('🔄 Recreate SEMUA squad?')) return;
  try {{
    const r = await fetch('/recreate_squads', {{method:'POST'}});
    if (r.ok) toast('🔄 Recreate dijalankan!', 'info');
  }} catch(e) {{ toast('❌ Error', 'error'); }}
}}
async function saveSquadConfig(e){{
  e.preventDefault();
  const btn = document.getElementById('squad-save-btn');
  btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Menyimpan...';
  const form = document.getElementById('squad-form');
  const size = form.querySelector('input[name="squad_size"]:checked').value;
  const rtype = form.querySelector('input[name="world_recruit_type"]:checked').value;
  const body = new URLSearchParams();
  body.append('squad_size', size);
  body.append('world_recruit_type', rtype);
  body.append('world_recruit_count', document.getElementById('world_recruit_count').value);
  body.append('squad_lifetime_sec', document.getElementById('squad_lifetime_sec').value);
  body.append('animation_interval_sec', document.getElementById('animation_interval_sec').value);
  body.append('bundle_count_on_join', document.getElementById('bundle_count_on_join').value);
  body.append('recruit_delay_sec', document.getElementById('recruit_delay_sec').value);
  body.append('emote_join_delay_sec', document.getElementById('emote_join_delay_sec').value);
  body.append('welcome_delay_sec', document.getElementById('welcome_delay_sec').value);
  body.append('kick_delay_sec', document.getElementById('kick_delay_sec').value);
  body.append('kick_msg', document.getElementById('kick_msg').value);
  body.append('auto_recreate', document.getElementById('auto_recreate_chk').checked ? '1' : '0');
  body.append('auto_recruit_on_join', document.getElementById('auto_recruit_on_join_chk').checked ? '1' : '0');
  body.append('auto_recruit_on_leave', document.getElementById('auto_recruit_on_leave_chk').checked ? '1' : '0');
  body.append('auto_bundle_on_join', document.getElementById('auto_bundle_on_join_chk').checked ? '1' : '0');
  body.append('auto_emote_on_join', document.getElementById('auto_emote_on_join_chk').checked ? '1' : '0');
  body.append('auto_animation', document.getElementById('auto_animation_chk').checked ? '1' : '0');
  body.append('auto_welcome_on_join', document.getElementById('auto_welcome_on_join_chk').checked ? '1' : '0');
  body.append('auto_kick_on_join', document.getElementById('auto_kick_on_join_chk').checked ? '1' : '0');
  body.append('welcome_msg', document.getElementById('welcome_msg_ta').value);
  try {{
    const r = await fetch('/save_squad_config', {{method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}}, body: body.toString()}});
    if (r.ok) toast('⚙️ Tersimpan!', 'success');
  }} catch(err) {{ toast('❌ Error', 'error'); }}
  btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Simpan Konfigurasi Squad';
}}
async function saveEmotePool(){{
  const btn = document.getElementById('emote-save-btn');
  btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Menyimpan...';
  const body = new URLSearchParams();
  body.append('join_emote_pool', document.getElementById('join_emote_pool').value);
  body.append('bot_self_emote_pool', document.getElementById('bot_self_emote_pool').value);
  body.append('bot_self_emote_enabled', document.getElementById('bot_self_emote_enabled').checked ? '1' : '0');
  body.append('bot_self_emote_interval', document.getElementById('bot_self_emote_interval').value);
  try {{
    const r = await fetch('/save_emote_pool', {{method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}}, body: body.toString()}});
    if (r.ok) toast('🎭 Emote disimpan!', 'success');
  }} catch(e) {{ toast('❌ Error', 'error'); }}
  btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Simpan Emote';
}}
async function loadAccountsList(){{
  try {{
    const r = await fetch('/api/accounts');
    if (!r.ok) return;
    const d = await r.json();
    document.getElementById('acc-content').value = d.content || '';
    document.getElementById('acc-count-pill').innerText = (d.count || 0) + ' Akun';
  }} catch(e) {{}}
}}
async function addSingleAccount(){{
  const uid = document.getElementById('new-uid').value.trim();
  const pwd = document.getElementById('new-pwd').value.trim();
  if (!uid || !pwd) {{ toast('❌ UID / Password wajib', 'error'); return; }}
  if (!/^[0-9]+$/.test(uid)) {{ toast('❌ UID harus angka', 'error'); return; }}
  try {{
    const body = new URLSearchParams();
    body.append('uid', uid); body.append('password', pwd);
    const r = await fetch('/add_account', {{method:'POST', body: body.toString()}});
    if (r.ok) {{
      toast('✅ Akun ditambahkan!', 'success');
      document.getElementById('new-uid').value = '';
      document.getElementById('new-pwd').value = '';
      await loadAccountsList();
    }}
  }} catch(e) {{ toast('❌ Error', 'error'); }}
}}
async function saveAllAccounts(){{
  const content = document.getElementById('acc-content').value;
  const btn = document.getElementById('acc-save-btn');
  btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
  try {{
    const body = new URLSearchParams();
    body.append('content', content);
    const r = await fetch('/save_accounts', {{method:'POST', body: body.toString()}});
    if (r.ok) {{
      const res = await r.text();
      toast('💾 ' + res, 'success');
      await loadAccountsList();
    }}
  }} catch(e) {{ toast('❌ Error', 'error'); }}
  btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Simpan';
}}
async function reloadAccounts(){{ await loadAccountsList(); toast('🔄 Dimuat ulang', 'info'); }}
function downloadAccounts(){{
  const content = document.getElementById('acc-content').value;
  const blob = new Blob([content], {{type: 'text/plain'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'accounts.txt'; a.click();
  URL.revokeObjectURL(a.href);
  toast('📥 Diunduh!', 'success');
}}
async function uploadAccFile(){{
  const fi = document.getElementById('acc-file');
  if (!fi.files || !fi.files[0]) {{ toast('❌ Pilih file', 'error'); return; }}
  const reader = new FileReader();
  reader.onload = async (e) => {{
    const content = e.target.result;
    document.getElementById('acc-content').value = content;
    try {{
      const body = new URLSearchParams();
      body.append('content', content);
      const r = await fetch('/save_accounts', {{method:'POST', body: body.toString()}});
      if (r.ok) {{
        const res = await r.text();
        toast('📤 ' + res, 'success');
        await loadAccountsList();
        fi.value = '';
      }}
    }} catch(err) {{ toast('❌ Error', 'error'); }}
  }};
  reader.readAsText(fi.files[0]);
}}
function doRefresh(){{ fetchStats(); fetchLogs(); toast('🔄 Diperbarui', 'info'); }}

async function fetchStats(){{
  try {{
    const r = await fetch('/api/stats');
    if (!r.ok) return;
    const d = await r.json();
    document.getElementById('stat-online').innerText = d.online;
    document.getElementById('stat-total').innerText = d.total;
    document.getElementById('stat-threads').innerText = d.threads;
    document.getElementById('stat-threads-badge').innerText = d.threads + ' Aktif';
    document.getElementById('stat-version').innerText = d.version;
    const tb = document.getElementById('accounts-tbody');
    if (d.accounts && d.accounts.length) {{
      tb.innerHTML = d.accounts.map(a => `<tr>
        <td style="font-family:'JetBrains Mono',monospace;color:var(--t2);">${{a.bot_uid}}</td>
        <td style="font-family:'JetBrains Mono',monospace;color:var(--t2);">${{a.uid}}</td>
        <td style="color:var(--gold);font-weight:700;">${{a.name}}</td>
        <td><span style="color:var(--amber);font-weight:700;">${{a.region}}</span></td>
        <td style="color:#facc15;font-family:'JetBrains Mono',monospace;font-weight:600;">${{a.squad_id||'Menunggu...'}}</td>
        <td style="color:var(--violet);font-weight:700;">${{a.squad_members||'0/0'}}</td>
        <td style="color:var(--t4);font-family:'JetBrains Mono',monospace;">${{a.time}}</td>
        <td><span class="badge-live">ONLINE</span></td>
      </tr>`).join('');
    }} else {{
      tb.innerHTML = '<tr class="empty-row"><td colspan="8">⚠️ Tidak ada bot aktif</td></tr>';
    }}
  }} catch(e) {{}}
}}
async function fetchLogs(){{
  try {{
    const r = await fetch('/api/logs');
    if (!r.ok) return;
    const d = await r.json();
    const el = document.getElementById('live-log');
    const logs = d.logs || [];
    if (!logs.length) {{ el.innerHTML = '📡 Menunggu log...'; return; }}
    const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 30;
    el.innerHTML = logs.map(l => `<div>${{l.replace(/&/g,'&amp;').replace(/</g,'&lt;')}}</div>`).join('');
    if (atBottom) el.scrollTop = el.scrollHeight;
  }} catch(e) {{}}
}}
function clearLogView(){{
  document.getElementById('live-log').innerHTML = '📡 Dibersihkan.';
  toast('🗑️ Log dibersihkan', 'warn');
}}

setInterval(() => {{
  const t = new Date();
  document.getElementById('uptimeTop').innerText = 
    String(t.getHours()).padStart(2,'0') + ':' +
    String(t.getMinutes()).padStart(2,'0') + ':' +
    String(t.getSeconds()).padStart(2,'0');
}}, 1000);

loadAccountsList(); setInterval(loadAccountsList, 15000);
fetchStats();       setInterval(fetchStats, 2000);
fetchLogs();        setInterval(fetchLogs, 2500);
refreshStatus();    setInterval(refreshStatus, 3000);
</script>
</body>
</html>"""
            self.wfile.write(html.encode('utf-8'))
            return

        if self.path == '/api/stats':
            with active_lock:
                accs = list(active_accounts); oc = online_count
            try: total = len(load_accounts())
            except: total = 0
            self._json_response({'online': oc, 'total': total, 'threads': len(accs),
                'version': FREEFIRE_VERSION_NAME or "loading...",
                'release': CURRENT_OB or "loading...", 'accounts': accs})
            return

        if self.path == '/api/logs':
            with log_lock: logs = list(log_buffer)
            self._json_response({'logs': logs}); return

        if self.path == '/api/accounts':
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f: content = f.read()
            except: content = ""
            accs = load_accounts()
            self._json_response({'content': content, 'count': len(accs),
                'accounts': [{'uid': u, 'password': p} for u, p in accs.items()]})
            return

        if self.path == '/api/status':
            self._json_response({'stopped': is_stopped(), 'online': online_count, 'total': total_accounts})
            return

        if self.path == '/health':
            self._text_response('OK')
            return

        self.send_response(404); self.end_headers()

    def do_POST(self):
        raw = self._read_body()

        if self.path == '/restart_accounts':
            trigger_restart_all()
            console.print("[yellow]♻️ Restart akun dipicu[/yellow]")
            self._text_response('OK'); return

        if self.path == '/recreate_squads':
            trigger_recreate_all()
            console.print("[yellow]🔄 Recreate squad dipicu[/yellow]")
            self._text_response('OK'); return

        if self.path == '/stop_all_bots':
            set_stop_all(True)
            console.print("[red]🛑 STOP SEMUA BOT DIPICU[/red]")
            self._text_response('OK'); return

        if self.path == '/start_all_bots':
            set_stop_all(False)
            console.print("[green]🚀 START SEMUA BOT DIPICU[/green]")
            self._text_response('OK'); return

        if self.path == '/save_accounts':
            params = parse_qs(raw)
            new_content = params.get('content', [''])[0]
            try:
                save_accounts_raw(new_content)
                cnt = len(load_accounts())
                console.print(f"[green]💾 Akun disimpan ({cnt})[/green]")
                self._text_response(f'OK:{cnt}')
            except Exception as e:
                self._text_response(f'Error: {e}', 500)
            return

        if self.path == '/add_account':
            params = parse_qs(raw)
            uid = params.get('uid', [''])[0].strip()
            pwd = params.get('password', [''])[0].strip()
            if not uid.isdigit() or not pwd:
                self._text_response('Invalid', 400); return
            try:
                accs = load_accounts(); accs[uid] = pwd; save_accounts(accs)
                console.print(f"[green]➕ Akun ditambahkan: {uid}[/green]")
                self._text_response('OK')
            except Exception as e:
                self._text_response(f'Error: {e}', 500)
            return

        if self.path == '/save_squad_config':
            params = parse_qs(raw)
            try:
                size = int(params.get('squad_size', ['4'])[0])
                if size not in (3, 4, 5): size = 4
                rc = int(params.get('world_recruit_count', ['3'])[0])
                if rc < 1 or rc > 10: rc = 3
                wrt = params.get('world_recruit_type', ['1'])[0]
                if wrt not in ('1', '2', 'half', 'random'): wrt = '1'
                lt = int(params.get('squad_lifetime_sec', ['5'])[0])
                if lt < 5 or lt > 3600: lt = 5
                ar  = params.get('auto_recreate', ['0'])[0] == '1'
                ajo = params.get('auto_recruit_on_join', ['0'])[0] == '1'
                alv = params.get('auto_recruit_on_leave', ['0'])[0] == '1'
                abj = params.get('auto_bundle_on_join', ['0'])[0] == '1'
                aej = params.get('auto_emote_on_join', ['0'])[0] == '1'
                aan = params.get('auto_animation', ['0'])[0] == '1'
                awj = params.get('auto_welcome_on_join', ['0'])[0] == '1'
                ako = params.get('auto_kick_on_join', ['0'])[0] == '1'
                bcj = int(params.get('bundle_count_on_join', ['2'])[0])
                if bcj < 1 or bcj > 5: bcj = 2
                ais = int(params.get('animation_interval_sec', ['10'])[0])
                if ais < 5 or ais > 300: ais = 10
                rds = float(params.get('recruit_delay_sec', ['1.5'])[0] or 1.5)
                if rds < 0.5 or rds > 30: rds = 1.5
                ejd = float(params.get('emote_join_delay_sec', ['0.5'])[0] or 0.5)
                if ejd < 0.1 or ejd > 30: ejd = 0.5
                wds = float(params.get('welcome_delay_sec', ['0.5'])[0] or 0.5)
                if wds < 0.1 or wds > 30: wds = 0.5
                kds = float(params.get('kick_delay_sec', ['1.0'])[0] or 1.0)
                if kds < 0.1 or kds > 30: kds = 1.0
                km = params.get('kick_msg', [''])[0] or "[B][C][FF0000]🚫 Auto-Kicked!"
                wm = params.get('welcome_msg', [''])[0] or DEFAULT_WELCOME_MSG
                with web_config_lock:
                    web_config['squad_size'] = size
                    web_config['world_recruit_count'] = rc
                    web_config['world_recruit_type'] = wrt
                    web_config['squad_lifetime_sec'] = lt
                    web_config['auto_recreate'] = ar
                    web_config['auto_recruit_on_join'] = ajo
                    web_config['auto_recruit_on_leave'] = alv
                    web_config['auto_bundle_on_join'] = abj
                    web_config['auto_emote_on_join'] = aej
                    web_config['auto_animation'] = aan
                    web_config['animation_interval_sec'] = ais
                    web_config['bundle_count_on_join'] = bcj
                    web_config['recruit_delay_sec'] = rds
                    web_config['welcome_msg'] = wm
                    web_config['auto_welcome_on_join'] = awj
                    web_config['auto_kick_on_join'] = ako
                    web_config['emote_join_delay_sec'] = ejd
                    web_config['welcome_delay_sec'] = wds
                    web_config['kick_delay_sec'] = kds
                    web_config['kick_msg'] = km
                save_web_config()
                console.print(f"[green]⚙️ Konfigurasi Diperbarui[/green]")
                self._text_response('OK')
            except Exception as e:
                self._text_response(f"Error: {e}", 400)
            return

        if self.path == '/save_emote_pool':
            params = parse_qs(raw)
            try:
                join_raw = params.get('join_emote_pool', [''])[0]
                self_raw = params.get('bot_self_emote_pool', [''])[0]
                bse = params.get('bot_self_emote_enabled', ['0'])[0] == '1'
                bsi = float(params.get('bot_self_emote_interval', ['8.0'])[0] or 8.0)
                if bsi < 1 or bsi > 300: bsi = 8.0

                def parse_ids(text):
                    ids = []
                    for part in re.split(r'[,\s\n;|]+', text or ''):
                        part = part.strip()
                        if part.isdigit():
                            v = int(part)
                            if 100000000 <= v <= 999999999:
                                ids.append(v)
                    return ids

                jids = parse_ids(join_raw)
                sids = parse_ids(self_raw)
                if not jids: jids = DEFAULT_JOIN_EMOTES[:]
                if not sids: sids = DEFAULT_JOIN_EMOTES[:]

                with web_config_lock:
                    web_config['join_emote_pool'] = jids
                    web_config['bot_self_emote_pool'] = sids
                    web_config['bot_self_emote_enabled'] = bse
                    web_config['bot_self_emote_interval'] = bsi

                save_web_config()
                console.print(f"[green]🎭 Emote Diperbarui (Join={len(jids)}, Self={len(sids)}, SelfOn={bse})[/green]")
                self._text_response('OK')
            except Exception as e:
                self._text_response(f'Error: {e}', 400)
            return

        self.send_response(404); self.end_headers()

    def log_message(self, format, *args): pass

# ================================================================
#   MAIN
# ================================================================
def start_web_server():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), BotHandler)
        console.print(f"[bold green]🌐 Dashboard NM.CDX: http://0.0.0.0:{port}[/bold green]")
        if not os.environ.get("RAILWAY_ENVIRONMENT"):
            try: webbrowser.open(f'http://localhost:{port}')
            except: pass
        server.serve_forever()
    except OSError:
        console.print(f"[bold red]❌ Port {port} sedang dipakai.[/bold red]")

async def main_async():
    print(render('NMCDX', colors=['white', 'red'], align='center'))
    load_web_config()
    threading.Thread(target=AuTo_ResTartinG, daemon=True).start()
    threading.Thread(target=start_web_server, daemon=True).start()
    await asyncio.sleep(1)
    asyncio.create_task(batch_account_loader())
    console.print(Panel(
        "[bold green]✅ Sistem Squad Aktif[/bold green]\n"
        f"[cyan]🌐 Port: {os.environ.get('PORT', 8080)}[/cyan]\n"
        f"[white]📦 {CURRENT_OB} | {FREEFIRE_VERSION_NAME}[/white]\n"
        "[magenta]👥 Squad: OpEnSq + cHSq22[/magenta]\n"
        "[yellow]📢 Recruit: Type 1 / 2 / Half / Random[/yellow]\n"
        "[bold magenta]👗 Auto Bundle · 🎭 Emote · ✨ Animasi[/bold magenta]\n"
        "[bold green]💬 Welcome FIXED ✅[/bold green]\n"
        "[bold red]🛑 STOP SEMUA BOT: 1-Klik ✅[/bold red]",
        title="[bold red]🔥 NM.CDX SQUAD BOT — PREMIUM 🔥[/bold red]",
        border_style="bright_red", expand=False))
    while True: await asyncio.sleep(3600)

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(main_async())
    except KeyboardInterrupt: console.print("\n[bold red]Dimatikan.[/bold red]")

if __name__ == "__main__":
    main()
