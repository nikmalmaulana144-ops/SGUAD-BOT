# xC4.py — MERGED (CDX.py + xC4.py) by NM.CDX
# All packet-generating functions are ASYNC (matches main.py)

import time, requests, json, binascii, urllib3, base64, datetime, re, socket, threading, random, os, sys, asyncio
from protobuf_decoder.protobuf_decoder import Parser
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from random import choice

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================
#  KEYS
# ============================================================
Key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
Iv  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

SAFE_COLORS = [
    "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
    "[FFC0CB]", "[ADD8E6]", "[90EE90]", "[DC143C]", "[00CED1]", "[9400D3]", "[FF1493]",
    "[7CFC00]", "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[1E90FF]"
]

# ============================================================
#  UTIL HELPERS
# ============================================================
def ArA_CoLor():
    Tp = ["32CD32","00BFFF","00FA9A","90EE90","FF4500","FF6347","FF69B4","FF8C00","FFD700",
          "FFDAB9","F0F0F0","F0E68C","D3D3D3","A9A9A9","D2691E","CD853F","BC8F8F","6A5ACD",
          "483D8B","4682B4","9370DB","C71585","FFA07A"]
    return random.choice(Tp)

def random_badge():
    return random.choice(["902000306","1200000004","901000194","827001005","827001006",
                          "203000543","203000348","827001008","902000308"])

def random_channel():
    return random.choice(['en','ar','fr','br'])

def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i+3] for i in range(0, len(str(n)), 3))

async def xBunnEr():
    bN = [902000011, 902000013, 902047016, 902049015, 902000154, 902000127, 902000207,
          902000305, 902037031, 902042011, 902053016, 902053018]
    return random.choice(bN)

async def Ua():
    versions = ['4.0.18P6','4.0.19P7','4.0.20P1','4.1.0P3','4.1.5P2','4.2.1P8','4.2.3P1',
                '5.0.1B2','5.0.2P4','5.1.0P1','5.2.0B1','5.2.5P3','5.3.0B1','5.3.2P2',
                '5.4.0P1','5.4.3B2','5.5.0P1','5.5.2P3']
    models = ['SM-A125F','SM-A225F','SM-A325M','SM-A515F','SM-A725F','SM-M215F','SM-M325FV',
              'Redmi 9A','Redmi 9C','POCO M3','POCO M4 Pro','RMX2185','RMX3085','moto g(9) play',
              'CPH2239','V2027','OnePlus Nord','ASUS_Z01QD']
    android = random.choice(['9','10','11','12','13','14'])
    lang = random.choice(['en-US','es-MX','pt-BR','id-ID','ru-RU','hi-IN'])
    country = random.choice(['USA','MEX','BRA','IDN','RUS','IND'])
    return f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {android};{lang};{country};)"

def EnC_Uid(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0)); H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

def DEc_Uid(H):
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80: break
        s += 7
    return n

# ============================================================
#  CORE (ASYNC)
# ============================================================
async def EnC_AEs(HeX):
    return AES.new(Key, AES.MODE_CBC, Iv).encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()

async def DEc_AEs(HeX):
    return unpad(AES.new(Key, AES.MODE_CBC, Iv).decrypt(bytes.fromhex(HeX)), AES.block_size).hex()

async def EnC_PacKeT(HeX, K, V):
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

async def DEc_PacKeT(HeX, K, V):
    return unpad(AES.new(K, AES.MODE_CBC, V).decrypt(bytes.fromhex(HeX)), 16).hex()

async def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        b = N & 0x7F; N >>= 7
        if N: b |= 0x80
        H.append(b)
        if not N: break
    return bytes(H)

async def CrEaTe_VarianT(field_number, value):
    return await EnC_Vr((field_number << 3) | 0) + await EnC_Vr(value)

async def CrEaTe_LenGTh(field_number, value):
    ev = value.encode() if isinstance(value, str) else value
    return await EnC_Vr((field_number << 3) | 2) + await EnC_Vr(len(ev)) + ev

async def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(field, str):
            try: field = int(field)
            except: continue
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    packet.extend(await CrEaTe_LenGTh(field, await CrEaTe_ProTo(item)))
        elif isinstance(value, dict):
            packet.extend(await CrEaTe_LenGTh(field, await CrEaTe_ProTo(value)))
        elif isinstance(value, bool):
            packet.extend(await CrEaTe_VarianT(field, int(value)))
        elif isinstance(value, int):
            packet.extend(await CrEaTe_VarianT(field, value))
        elif isinstance(value, (str, bytes)):
            packet.extend(await CrEaTe_LenGTh(field, value))
    return bytes(packet)

async def DecodE_HeX(H):
    F = str(hex(H))[2:]
    return "0" + F if len(F) == 1 else F

async def GeneRaTePk(Pk, N, K, V):
    PkEnc = await EnC_PacKeT(Pk, K, V)
    _ = await DecodE_HeX(len(PkEnc) // 2)
    if   len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    else:             HeadEr = N + "0000"
    return bytes.fromhex(HeadEr + _ + PkEnc)

async def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        fd = {'wire_type': result.wire_type}
        if result.wire_type in ("varint", "string", "bytes"): fd['data'] = result.data
        elif result.wire_type == 'length_delimited': fd["data"] = await Fix_PackEt(result.data.results)
        result_dict[result.field] = fd
    return result_dict

async def DeCode_PackEt(input_text):
    try:
        return json.dumps(await Fix_PackEt(Parser().parse(input_text)))
    except Exception as e:
        print(f"error {e}")
        return None

# ============================================================
#  AUTH / GLOBAL
# ============================================================
async def AutH_GlobAl(K, V):
    fields = {1: 3, 2: {2: 5, 3: "en"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, V)

async def GLobaL(T, K, V):
    fields = {1: 3, 2: {2: 5, 3: f"{T}"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, V)

async def GenJoinGlobaL(owner, code, K, V):
    fields = {1: 4, 2: {1: owner, 6: 1, 8: 1, 13: "en", 15: code, 16: "OR"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

# ============================================================
#  SQUAD / GROUP PACKETS
# ============================================================
async def OpEnSq(K, V, region, version):
    fields = {
        1: 1,
        2: {
            2: "\u0001", 3: 43, 4: 1, 5: "en",
            8: [{1: "IDC2", 2: 171, 3: "BD"}],
            9: 1,
            10: ("rYUW\u0017\t\u0007NR\u000f\u0005\u0004\\W\u0002\u000fV\u0004TPQ\u0003\u000f\u0005\u0004]\u0005\u000b\u0000\u0002W\u0005\r\nVY\u0004\u0007\u0007\u0007\u0017\u0001\bNQ\fS\u0005\u000e\u0006\f\u0005\rT\u0002\r\u0000TS\u0007U\u0004X\u0006RY\u0005\u0003\u0003SW\u0000\u000eQ\u0000^\u0014\u0003\u0004JXS\u000f\u0000g{gqfePblEZJp{_xU\bmQW\f\u0007\u000f\u0015\u0007H\\U^CHXh@Ax`\u000f~\rPN~Nz\\\u001fr_ckPU\u000b\u0015\u0005\u0003Ekfp\u007fcY\u0001nWV\u0002\u0005azE~N\u0007HTg\u0007w}@\u0002{\t\u0013\u0001NeNP]DUf|]ugINs{\u0001\\rAgB_\u0004fA]\u0004\r\u001a\u0000HpOv\\\u0005|gS\u0019\\A\u007fWW\u0003\u007fTqFGi\u0004Qr\u0019dW\u0004\u0011\rD\u0002yeZ]A\u0016a\u0007Ungeg\u0007E\\P\u001b\u000b\u0004\u0005dd\ff\r\u000f\u0017\t\u000fNRyZd\u0012tZ\fe\u0007AGv\u007fw]{P\u001c\u007f\u000ff\u0005ZJK\u0004\u0005\u0014\u0001Jgq\u001frymsB\u0001\u000fd`\u001bj~[}\u0004SDZ|IxKB\u0000\n\u0011\u0002J^`tjYN\u0007WQdE[PQ\u0002_{VP`S\t\u007f\u001dP\n\u000f\u000f\u0015\u0004\u0004L{V\u0003@yP[rgJ{Hpk\u0001\u000bw\u0001Agt_\u0003HxPc\u000b\u0017\u0005E`y\ngWoy\u0006S{A\u001b``Y\u0002Xzw}dDWOKsg\t\u0013\u000eNf\u000e\\`\u0005AwJc\u0003BM\u0001^\u0000R\u0002Qoh]tbS~`G\r\u001a\u0004HibAQ\u000f^XNt~kDUWaeaNqcLQ]Py[G\u0004"),
            11: 1, 13: 1,
            14: {
                1: "08FAA33B035B3F16020859055555000200030001000000004AFA7572105C674946762514220104186fa2e8770e748c3f6a68ed75000000ff18470f0bcacfa16d",
                2: 681,
                3: {14: {11: "1106064f50055401030f03020403060155070d01540e060e020607540706030354530f041003064d715c46434b1f061f031e1205034a1c40677c5f554775755f504e677446185b584901534144685b67620f", 0: 72}},
                4: "x\\\\R", 6: 13, 7: {2: 80},
                8: version, 9: 2, 10: 1,
                11: "03626253513677542b504e4635416456324b796f566c576a326567507844414c33507138513031762b66536c626a587648434e3348414e376c472b72474637794165676e72436b553671626b694538706f534e5a582b2f7a44675a547475465650542b384d69565a507151312b444b53576f786f6d592f7156394f76755254482b7154486a78486f664169734267564970454d454e6b4c326a4763445a4a5176416d687947356b7669564e544d71515745754b32324d4e384e4931424d437445395532415156694b667948314574412b32644536464b53773132554155596363372b7753652b66676c393742756544446a58496d6e35666d45444a51535948326644484c5650676755472f51794b776e77545151324a505265352f72314830616d374264424f556b712f523246734d635475516d47364c684a547a4379345774444245795268305754366f68532f785a48736a4c7a4366506378372f386a534133352b67787642657450397a4f6f463639344945386e6e77336b507344357a6e6337593649776b4142435761776f6d572b6948594f5939686d647632706975584168416d6d6a74496f5945444c6e506e5738616f7153304f74486b732f5a3953543252447345507a3343655438774e6874756d57634b4438585445376649386c305173726a772f4a57514f76394b50307257644538593375422f2b495836757675452b487a6a4853466c75726f33515432536567595758535854714674495a61454d476c51314b7639666c59525539465047366c30663045314f7a2b2b36324339644b664c4d39315a782f6f625938726a6e682b77524a3962636e544e41715466486f72354b714d3d"
            },
            19: 329, 21: "374f5219", 24: {1: 21}, 27: "a_6534489873065906362"
        }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def OpEnSq11(K, V, region, version):
    if region.lower() == "bd":   header, idc, reg = '0519', "IDC3", "BD"
    elif region.lower() == "ind": header, idc, reg = '0514', "IDC2", "IND"
    else:                         header, idc, reg = '0515', "IDC1", "ME"
    fields = {1: 1, 2: {2: {}, 3: 1, 4: 1, 5: "en", 8: {1: idc, 2: 226, 3: reg},
                        9: 1, 11: 1, 13: 1, 14: {6: 11, 8: str(version), 9: 3, 10: 2}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), header, K, V)

async def cHSq(Nu, bot_uid, K, V, region):
    fields = {1: 17, 2: {1: int(bot_uid), 2: 1, 3: int(Nu), 4: 46, 5: "\x1a", 8: 12, 13: 330}}
    if   region.lower() == "ind": pt = '0514'
    elif region.lower() == "bd":  pt = "0519"
    else:                          pt = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pt, K, V)

async def cHSq22(Nu, bot_uid, K, V, region):
    fields = {1: 17, 2: {1: int(bot_uid), 2: 1, 3: 3, 4: 1, 5: "\x1a", 8: 1}}
    if   region.lower() == "ind": pt = '0514'
    elif region.lower() == "bd":  pt = "0519"
    else:                          pt = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pt, K, V)

async def SEnd_InV(Nu, Uid, K, V, region):
    fields = {1: 2, 2: {1: int(Uid), 2: region, 4: int(Nu)}}
    if   region.lower() == "ind": pt = '0514'
    elif region.lower() == "bd":  pt = "0519"
    else:                          pt = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pt, K, V)

async def ExiT(idT, K, V):
    try:
        fields = {1: 7, 2: {1: int(idT) if idT else 0}}
        return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)
    except Exception as e:
        print(f"ExiT err: {e}"); return b""

async def Join_Squad_Packet_TC(T, key, iv):
    fields = {1: 4, 2: {4: "\u0001\u0003\u0004\u0007\t\n\u000b\u0012\u000e\u0016\u0019\u001a \u001d'",
                        5: str(T), 6: 6, 8: 1,
                        9: {2: 3140, 3: "vX\\Q\u0016\u0005\bN\u0006R\b\u0001U\u0002\rR[\u0003TU\u0006\b\u0007U\u0004P\\\u0000RRRT\t\u0007\fP\n\nS\u0000\u0013\u0000\u0001HpYHFN\u001e\u0000\u001d\u0001\u001d\u0016\u0005\nN[U\u0006\u0003cwewhaSdeF^Fr}Q|V\u000edRS\u0000\u0005\t\u001b\u0003K^s`c^\u0005\u001fw\u0003\u0005@Bz\u0006\u0006\\{\bVbSR~J{La\u0005\u0011\u0006\u0005L[UNAwHZ_\u0019s~_Rvdy\u001d_uq\u001aCNRpM{\n\u0015\bMaBR[JQezTvcELuu\u0005_tHdFS\u0006`OY\u0007\u000b\u0013\u0003LYA\u0000AAzPWdqDy~Uj\\\u0005GgovQzrU\r\u0012\tHq[@Dr[\u0000`zS|MIZR\u0005r\u0006g\u0005pM\nPTrS\f\u0013\u0005\rHIwVRhAgfl\u000e]R\u0019EZ\\A@\fLHYN\u001bXW\t\u0016\u0007DjydvuG\u0001]MUO\u0005^[tBcS\u0013J@\u0002\\ZJ\f\b\u0017\fNyNaV}F~\rT\u0006Y\u000fBzyag\u0007@{BxU^WNV\t\u001b\u0000\u0007J\\\u0003d\u0003vBBQ^^\u001bCd\u0005\\M`F@C\t\u0007^sUS\u000f\u0014\u0003LRX`lzm_\u0004ovtxDwPr@`^B_Y\\`Mks\n",
                            4: "zW\\R", 6: 11, 7: "\u0014twqqq~\u0016\u0013", 8: "1.120.19", 9: 3, 10: 2},
                        13: "ar", 16: "7OR\u0019"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0501', key, iv)

async def GenJoinSquadsPacket(T, key, iv):
    """Join random squad packet (used by JOINER bots)"""
    fields = {1: 4, 2: {4: "\u0001\u0003\u0004\u0007\t\n\u000b\u0012\u000e\u0016\u0019\u001a \u001d'",
                        5: str(T), 6: 6, 8: 1,
                        9: {2: 3140, 3: "vX\\Q\u0016\u0005\bN\u0006R\b\u0001U\u0002\rR[\u0003TU\u0006\b\u0007U\u0004P\\\u0000RRRT\t\u0007\fP\n\nS\u0000\u0013\u0000\u0001HpYHFN\u001e\u0000\u001d\u0001\u001d\u0016\u0005\nN[U\u0006\u0003cwewhaSdeF^Fr}Q|V\u000edRS\u0000\u0005\t\u001b\u0003K^s`c^\u0005\u001fw\u0003\u0005@Bz\u0006\u0006\\{\bVbSR~J{La\u0005\u0011\u0006\u0005L[UNAwHZ_\u0019s~_Rvdy\u001d_uq\u001aCNRpM{\n\u0015\bMaBR[JQezTvcELuu\u0005_tHdFS\u0006`OY\u0007\u000b\u0013\u0003LYA\u0000AAzPWdqDy~Uj\\\u0005GgovQzrU\r\u0012\tHq[@Dr[\u0000`zS|MIZR\u0005r\u0006g\u0005pM\nPTrS\f\u0013\u0005\rHIwVRhAgfl\u000e]R\u0019EZ\\A@\fLHYN\u001bXW\t\u0016\u0007DjydvuG\u0001]MUO\u0005^[tBcS\u0013J@\u0002\\ZJ\f\b\u0017\fNyNaV}F~\rT\u0006Y\u000fBzyag\u0007@{BxU^WNV\t\u001b\u0000\u0007J\\\u0003d\u0003vBBQ^^\u001bCd\u0005\\M`F@C\t\u0007^sUS\u000f\u0014\u0003LRX`lzm_\u0004ovtxDwPr@`^B_Y\\`Mks\n",
                            4: "zW\\R", 6: 11, 7: "\u0014twqqq~\u0016\u0013", 8: "1.120.19", 9: 3, 10: 2},
                        13: "ar", 16: "7OR\u0019"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0501', key, iv)

async def JoinSquadByTeamCode(team_code, K, V, region="BD"):
    fields = {1: 4, 2: {4: "\u0001\u0007\t\n\u000b\u0012\u0019 '", 5: str(team_code), 6: 6, 8: 1,
                        9: {1: "08FFF3BE903F27DF0203110111110000006B0003006800169194106F13CF106E4676251411010404dfe9e8b5ca3ca4f96a3119c00000004f03060301cacfa16d",
                            2: 130, 3: "tY_S\u0013\b\u0001M\u0002\u0000T\u0000\u0005\u000e\b\t\u0002\u0000\u0003U\u0003\u0001V\u000fR\u000e\tRQ\u0002\u0004\u0005US\u0003XS\u0005\u0001\u0002\u0011\u0001\u0002JuTAEN\u001e\u0002\u001c\u0002\u001f\u0013\b\u0003M\u001cDbz_Q@}p_QOgsC\u001dYVI\u0004UAAj_ga\u0004\u0012\u0000K\u001d\u0007_t\u0019b\bCx\u0002UeGat\u001fTTCBLER`\u0006\u0001\r\f\u0012\u0006\u0005N^^\u0002acH~r\u0004_\u0003RO|\u000bcd_@~`Rnqrgh\n\u0015\nL\\Nh\u0000~G\u000et\u0000eb]VQ\u0006t^F[ZIGxCdZD\u000b\u0011\u0002OA~LP@\u000fcSDyATQApaT^{|wa]\\\u0001E\u000f\u0013\nJfxve}\u0004J\u0003c{YL\u0007^^yDYQf\bhe\u0005_wg\r\u0010\u0007\bEHpX@||\u0002Z\\uTGyA\u0001JP\u0005t~VkTE\u0000J\\\u000b\u0013\nMr\u0018zTzK}qE]vnvwROuheYvwduvQ\r\u001a\u0005M\u0006z\u001dfXfzvHFc~dXUz}O\u001aB\u0005t\u0002i\u001co_\u0004\u0012\u0003\u0007J\u0006b\u0003\u000eqlfvbEstgu~wB\u0001v@`yI\u0002ZPx\f\u0014\u0003NR\u0002yBZvuD_cd\u0004q]lH]\u0007bD}pCe\t\u0004t\n",
                            4: "w^_R", 6: 11, 7: "\u0014\u0004aqrg\u0015\u0013", 8: "1.126.7", 9: 3, 10: 2,
                            11: "\u0003bbSQ6wxegh9qAdV2KyoVleA17yPmYF+yTnOrl+JMknmppeUBe5ZsiHueP2mZZ4KOs6b2Ail1S9z3qIeU9hGFZ2M6PP39/zjIc/RFVPAkgDagySswMVmYaPhkzU5IqNPow2843fyQUz9xI10NdMhl1WiI4Y6wCXBotiUS9wSgujQ4j0fWXUyklCxBWo8r27hyoGSVrPdTPXFMnJJpPRRFFmWqc3fWvMg+BNfxSRJOZRSrkzG0nNvSIJ4uZB2pqAlHIPEYx7bI6zsgwUVDiLZJKTUTyuCGbOd1DegDUFfazFesTG1LJknT5WhgzCsrBIy+f2l+LeJe5DW7wEwNaHambM7ECXcJcLIhB9kJJsW0tFvXkk3HSdcQ8N1K6wjSKWhpkW0kV8Zrjj0jkhS/7AZ6T9GJRIA827YDtTorBvbx1UkXjYrqYI1nSa2GaMexGnqlurc5DE3v1R+mUBI9GqmjEPgTSYVBxyeCdQMHaMXGtspAhvkiO84ToU87sP45pylDEfFOVoc/rcmdzWeqlYPsv6txKRtIHcb0cO+MoVShoU8ZUVRDF3znbqzVrscPIfplBaa79lwvQqzRubLl9XY="},
                        11: {1: "IDC4", 2: 281, 3: "ME"}, 13: "fr", 16: "7OR\u0019",
                        20: "\b\u0015", 27: "\bH\u0010\u0003"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

# ============================================================
#  GHOST PACKETS
# ============================================================
async def ghost_pakcet(player_id, nm, secret_code, key, iv):
    fields = {1: 61, 2: {1: int(player_id),
                         2: {1: int(player_id), 2: 1159, 3: f"[b][c][{ArA_CoLor()}]{nm}",
                             5: 12, 6: 9999999, 7: 1, 8: {2: 1, 3: 1}, 9: 3},
                         3: secret_code}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), "0515", key, iv)

async def Ghost_Final_Packet(player_id, ghost_nm, secret_code, K, V):
    return await ghost_pakcet(player_id, ghost_nm, secret_code, K, V)

async def Send_GhosTs(Uid, Nm, sQ, K, V):
    return await ghost_pakcet(Uid, Nm, sQ, K, V)

# ============================================================
#  CHAT / MESSAGES
# ============================================================
async def AutH_Chat(T, uid, code, K, V):
    fields = {1: T, 2: {1: uid, 3: "en", 4: str(code)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, V)

async def yasser_Chat(uid, code, K, I):
    fields = {1: 3, 2: {1: uid, 3: "fr", 4: str(code)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, I)

async def yasser_quitcaht(uid, K, I):
    fields = {1: 4, 2: {1: uid, 3: "fr"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, I)

async def yasser_SendInv(bot_uid, uid, K, V):
    fields = {1: 33, 2: {1: int(uid), 2: "ME", 3: 1, 4: 1, 6: "yyt", 7: 330, 8: 1000, 9: 100,
                         10: "DZ", 12: 1, 13: int(uid), 16: 1, 17: {2: 159, 4: "y[WW", 6: 11,
                         8: "1.118.1", 9: 3, 10: 1}, 18: 306, 19: 18, 24: 902000306, 26: {},
                         27: {1: 11, 2: int(bot_uid), 3: 999}, 28: {}, 31: {1: 1, 2: 32768},
                         32: 32768, 34: {1: bot_uid, 2: 8,
                         3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def yasser_Msg(msg, owner, bot, K, I):
    fields = {1: 1, 2: 2, 2: {1: bot, 2: owner, 4: msg, 5: str(time.time()).split('.')[0],
                9: {1: "Fun1w5a2", 2: await xBunnEr(), 3: int(random_badge()), 4: 330,
                    5: int(random_badge()), 10: 1, 11: 1, 7: 2, 13: {1: 2},
                    14: {1: bot, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}},
                10: "fr", 13: {2: 1, 3: 1}, 14: {}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, I)

async def Msg_Sq(msg, owner, bot, K, V):
    fields = {1: 1, 2: 2, 2: {1: bot, 2: owner, 4: msg, 5: 1757799182,
                9: {1: "NM.CDX", 2: await xBunnEr(), 3: 909000024, 4: 330, 5: 909000024,
                    10: 1, 11: 1, 12: 0, 13: {1: 2},
                    14: {1: bot, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}},
                10: "ar", 13: {3: 1}, 14: ""}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, V)

async def send_room_chat_enhanced(Msg, room_id, key, iv, region, sender_uid=9280892890):
    fields = {1: 1, 2: {1: sender_uid, 2: int(room_id), 3: 3,
                        4: f"[{ArA_CoLor()}]{Msg}",
                        5: int(datetime.now().timestamp()),
                        9: {1: "RIJEXX", 2: int(await xBunnEr()), 4: 228, 7: 1},
                        10: "en", 13: {2: 1, 3: 1}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', key, iv)

async def xSEndMsg(Msg, Tp, Tp2, id_, K, V):
    fields = {1: id_, 2: Tp2, 3: Tp, 4: Msg, 5: 1735129800,
              9: {1: "[FFFFFF]NM.CDX", 2: int(await xBunnEr()), 3: 901048020, 4: 330,
                  5: 800000304, 8: "NM.CDX - C4", 10: 1, 11: 1, 13: {1: 2},
                  14: {1: 12484827014, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}, 12: 0},
              10: "en", 13: {3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)

async def xSEndMsgsQ(Msg, id_, K, V, region="BD"):
    avatar = await xBunnEr()
    fields = {1: id_, 2: id_, 4: Msg, 5: 1756580149, 8: 904990072,
              9: {1: "[FFFFFF]NM.CDX", 2: avatar, 3: 2, 4: 329, 5: 800000304, 6: 66, 7: 66,
                  8: "ONLY NM.CDX", 9: 66, 10: 66, 11: 1, 12: 66,
                  13: {1: 68, 2: 67},
                  14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0A\x0B\x15\x0C\x0F\x11\x04\x07\x02\x03\x0D\x0E\x12\x01\x05\x06"}},
              10: "en", 13: {3: 1},
              14: {11: {1: 3, 2: 7, 3: 170, 4: 999, 5: 1, 6: region, 8: 2, 9: 2}}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)

async def xSEndMsgsQq(Msg, id_, K, V, region="IND"):
    avatar = await xBunnEr()
    fields = {1: id_, 2: id_, 4: Msg, 5: 1756580149, 8: 904990072,
              9: {1: "NM.CDX", 2: avatar, 4: 330, 5: 800000304, 8: "ONLY NM.CDX",
                  10: 1, 11: 1, 13: {1: 2},
                  14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0A\x0B\x15\x0C\x0F\x11\x04\x07\x02\x03\x0D\x0E\x12\x01\x05\x06"}},
              10: "en", 13: {2: 2, 3: 1},
              14: {1: {1: random.choice([1, 4]), 2: 1, 3: random.randint(1, 180), 4: 1,
                       5: int(datetime.now().timestamp()), 6: region}}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)

# ============================================================
#  ROOM / OTHER
# ============================================================
async def openroom(K, V):
    fields = {1: 2, 2: {1: 1, 2: 15, 3: 1, 4: "NM.CDX", 5: "11", 6: 4, 7: 1, 8: 1, 9: 1, 11: 1,
                        12: 2, 14: 3030901227, 15: {1: "IDC3", 2: 126, 3: "BD"},
                        16: "\u0001\u0003\u0004\u0007\t\n\u000b\u0012\u000f\u000e\u0016\u0019\u001a \u001d",
                        18: 3030901002000, 27: 1, 34: "\u0000\u0001", 40: "en", 48: 1, 49: {1: 2}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0E15', K, V)

async def spmroom(K, V, uid):
    fields = {1: 22, 2: {1: int(uid)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0E15', K, V)

async def GeT_Status(Player_Uid, K, V):
    Player_Uid = EnC_Uid(Player_Uid, Tp='Uid')
    if   len(Player_Uid) == 8:  Pk = f'080112080a04{Player_Uid}1005'
    elif len(Player_Uid) == 10: Pk = f"080112090a05{Player_Uid}1005"
    else: return None
    return await GeneRaTePk(Pk, '0f15', K, V)

async def SPam_Room(Uid, Rm, Nm, K, V):
    fields = {1: 78, 2: {1: int(Rm), 2: f"[{ArA_CoLor()}]{Nm}", 3: {2: 1, 3: 1}, 4: 330, 5: 1,
                         6: 201, 10: await xBunnEr(), 11: int(Uid), 12: 1}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0e15', K, V)

async def AuthClan(CLan_Uid, AuTh, K, V):
    fields = {1: 3, 2: {1: int(CLan_Uid), 2: 1, 4: str(AuTh)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1201', K, V)

async def FS(key, iv, region="ind"):
    fields = {1: 9, 2: {1: 12480598706}}
    enc = await EnC_PacKeT((await CrEaTe_ProTo(fields)).hex(), key, iv)
    hlen = await DecodE_HeX(len(enc) // 2)
    if   region.lower() == "ind": pt = '0514'
    elif region.lower() == "bd":  pt = "0519"
    else:                          pt = "0515"
    pad_len = {2: "000000", 3: "00000", 4: "0000", 5: "000", 6: "00"}.get(len(hlen), "000000")
    return bytes.fromhex(pt + pad_len + hlen + enc)

async def GeTSQDaTa(D):
    try:
        if '5' in D and 'data' in D['5']:
            s = D['5']['data']
            if '1' in s and '17' in s and '31' in s:
                return s['1']['data'], s['17']['data'], s['31']['data']
        return None
    except: return None

async def ChaT_sQ(T, N, U, sQ, K, V):
    fields = {1: N, 2: {1: int(U), 3: f"{T}", 4: str(sQ)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, V)

async def ReFLeSH_Yr():
    fields = {4: 264304360}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', Key, Iv)

async def Join_Sq(K, V):
    fields = {
        1: 69,
        2: {
            2: random.choice(['tr']),
            7: 330, 8: 330, 9: "",
            10: "\u0001\t\n\u000b\u0012\u0019 '",
            11: 1,
            12: {1: "088B823A900F2FEF020101000000000200140001001100020E682E6B13949B6B46762514110000010594e97dca3ca4f96a3ba7bd0000004f00000100cacfa16d",
                 2: 31,
                 3: "tY_S\u0013\b\u0001MV\u0003\u0007\u0005\u0004W\u0005]\u0007\t\u0002\u0007\u0001\u0000\u0003\u0000T\fS\u0006\u0000W\u0004\u0003\u0002\u0000\b\r\u0000\u0001U\u0005\u0011\u0001\u0002JuTAEN\u001e\u0002\u001c\u0002\u001f\u0013\b\u0003M\u001cDbz_Q@}p_QOgsC\u001dYVI\u0004UAAj_ga\u0004\u0012\u0000K\u001d\u0007_t\u0019b\bCx\u0002UeGat\u001fTTCBLER\u0006\u0001\r\f\u0012\u0006\u0005NYaeA~ha\u000fZzr\u0006IZw|F}qf\u007f\u0001l\u0007t\n\u0015\nL\\Nh\u0000~G\u000et\u0000eb]VQ\u0006t^F[ZIGxCdZD\u000b\u0011\u0002OA\u0000\u000fgTtbgJcfq\u0001euAYAQKQtTsHD{\u000f\u0013\nJx^k^EO[c\u0005aTRw\u0002\u007fw@\u007f\u0002BX\ntY@@]\r\u0010\u0007\bES~N[kxUE\u0002o\u001eZ\\C@A{F[tvhN\u0003Qr\u000b\u0013\nMr\u0018zTzK}\u007fqE]vnvwROuheYvwduvQ\r\u001a\u0005M\u0006z\u001dfXfzvHFc~dXUz}O\u001aB\u0005t\u0002i\u001co_\u0004\u0012\u0003\u0007J\u0006b\u0003\u000eqlfvbEstgu~wB\u0001v@yI\u0002ZPx\f\u0014\u0003NR\u0002yBZvuD_cd\u0004q]lH]\u0007bD}pCe\t\u0004t\n",
                 4: "w^_R", 6: 11, 7: "\u0016xx`wc\u0015\u0013", 8: "1.128.15", 9: 3, 10: 2,
                 11: "0003626253513637456372725663416456324b796f566c586c6449716f4662743755656f5a4c633547475052557472782f7646515a4c54753272754d7432676d6875504f4d6c5a74444371496c4c5944447961546572366864394e6774365462364e754549774959395243614f3348793873666b47696c6444656b36394846426e3657442b31415430695566336e42714b41724b38315945743231393671617a4e61434144514f6772466c6e614358306f646849436b35625347476963687a6e61764850757264562b5a4365576d4a6470736f556961504d544c3039587662345530674b6453486d4a396b2b56476767432f6d525972613965476c52444d4a4d45566b36434a4458786e6a6263327a7a4c536e32576a5a4977646f7a305750796368415a4970636f61366c6d35794474636c734c3953514c74615055617370626549314f6b5a5a3265517062786837774152464e617a4642795661354a79546e675558425a796246566565464f656a6b6d53585a714e5764567a65314443583858737a414364795246636332624e6a7438476e4866396d61744d492b766a33577a6446526c537073655350582f364945714157546c45306a6958785674656144586a2f6878716b49312b6339695534736f52666578526e757548486d4f33583839476277475678695475774278764772746532616732582f4f4f51497a44314d644177475177386e364b584c646c4f44547274654f7448306170324174674e6d4634694d6a654c484e4c70504c366964694e5850594633413d3d"},
            16: 1, 17: "\u0001\u0002\u0003\u0004", 18: "\u0001\u0002\u0003\u0004\u0005",
            21: "\b\u0015", 28: "\bH\u0010\u0003", 29: 5
        }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def LeVe_C(cid, K, V):
    fields = {1: 4, 2: {1: int(cid), 2: 5}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1201', K, V)

async def Send_InV(N, U, K, V):
    fields = {1: 2, 2: {1: int(U), 2: "ME", 4: N}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def RefLeSh(K, V):
    fields = {1: 67, 2: {1: "ar", 6: 315, 7: 322, 10: 1, 12: 1, 13: {}, 14: {}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def Join_Sq1(T, U, rQ, K, V):
    fields = {1: 4, 2: {1: U, 4: "\u0001\u0003\u0004\u0007\t\n\u000b\u0012\u000f\u0019\u001a ",
                        6: 1, 8: 1,
                        9: {4: "y[WW", 6: 11, 7: "\u001d`at\u0005d\u001d\u0016",
                            8: "1.118.3", 9: 3, 10: 2},
                        13: "ar", 15: rQ, 16: "OR", 20: {1: 21}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def trydecyasser(pack):
    try:
        return pack['5']['data']['3']['data']['31']['data']
    except KeyError:
        try: return pack['5']['data']['31']['data']
        except: return None
    except: return None

async def reflesh(uid, K, V):
    fields = {1: 1, 2: {1: {1: uid, 2: 14, 4: 84}, 2: {6: 9},
                        3: {1: uid, 2: 5, 4: 68}, 4: {2: 1596891}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

def GeT_Time(timestamp):
    last_login = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    diff = now - last_login
    h, rem = divmod(diff.seconds, 3600)
    m, s = divmod(rem, 60)
    return h, m, s

def LogOuT(A):
    R = requests.Session().get(f'https://100067.connect.garena.com/oauth/logout?access_token={A}&refresh_token=')
    print('LoGOuT =>', R.text)
    return R.status_code == 200 and '0' in R.text

def ResTarTinG():
    print('\n  ResTartinG BoT ... !')
    time.sleep(0.5)
    python = sys.executable
    os.execl(python, python, *sys.argv)

def AuTo_ResTartinG():
    time.sleep(6 * 60 * 60)
    print('\n  AuTo ResTartinG The BoT ... !')
    python = sys.executable
    os.execl(python, python, *sys.argv)

# ============================================================
#  CRAFTLAND SHARE (Sync, uses global socket)
# ============================================================
def send_craftland_share_sync(sock, bot_uid, target_id, chat_type, map_code, key, iv):
    try:
        try: bot_uid_int = int(bot_uid)
        except (ValueError, TypeError):
            print(f"❌ Invalid bot_uid: {bot_uid}")
            return False
        craftland_json = json.dumps({"WorkshopCode": map_code, "type": "UGCMapShare"})
        fields = {
            1: 1,
            2: {1: bot_uid_int, 2: int(target_id), 3: 5, 5: int(time.time()), 7: 1,
                8: craftland_json,
                9: {1: "NM.CDX BOT", 2: xBunnEr_sync(), 4: 330, 5: 801046518, 8: "NM.CDX TEAM",
                    10: 1, 11: 1, 13: {1: 2},
                    14: {1: 1158053040, 2: 8,
                         3: "\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
                10: "en", 13: {2: 2, 3: 1}}
        }
        proto_bytes = create_proto_sync(fields)
        packet = generate_pk_sync(proto_bytes.hex(), '1215', key, iv)
        sock.send(packet)
        print(f"✅ CRAFTLAND MAP ({map_code}) SENT Successfully!")
        return True
    except Exception as e:
        print(f"❌ Craftland Error: {e}")
        return False

def xBunnEr_sync():
    return int(random.choice(['902000016','902000031','902000011','902000065','902000204',
                              '902000192','902000191','902000179','902000133','902045001',
                              '902038023','902048004','902039014','902000063','902000306','902047009']))

def encode_varint_sync(value):
    result = []
    if value < 0: value &= (1 << 64) - 1
    while True:
        byte = value & 0x7F; value >>= 7
        if value: byte |= 0x80
        result.append(byte)
        if not value: break
    return bytes(result)

def create_proto_sync(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested = create_proto_sync(value)
            packet.extend(encode_varint_sync((field << 3) | 2))
            packet.extend(encode_varint_sync(len(nested))); packet.extend(nested)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    nested = create_proto_sync(item)
                    packet.extend(encode_varint_sync((field << 3) | 2))
                    packet.extend(encode_varint_sync(len(nested))); packet.extend(nested)
        elif isinstance(value, bool):
            packet.extend(encode_varint_sync((field << 3) | 0)); packet.extend(encode_varint_sync(int(value)))
        elif isinstance(value, int):
            packet.extend(encode_varint_sync((field << 3) | 0)); packet.extend(encode_varint_sync(value))
        elif isinstance(value, str):
            encoded = value.encode('utf-8')
            packet.extend(encode_varint_sync((field << 3) | 2))
            packet.extend(encode_varint_sync(len(encoded))); packet.extend(encoded)
        elif isinstance(value, bytes):
            packet.extend(encode_varint_sync((field << 3) | 2))
            packet.extend(encode_varint_sync(len(value))); packet.extend(value)
    return bytes(packet)

def generate_pk_sync(Pk, N, K, V):
    PkEnc = AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(Pk), 16)).hex()
    L = str(hex(len(PkEnc) // 2))[2:]
    if len(L) == 1: L = "0" + L
    if   len(L) == 2: HeadEr = N + "000000"
    elif len(L) == 3: HeadEr = N + "00000"
    elif len(L) == 4: HeadEr = N + "0000"
    elif len(L) == 5: HeadEr = N + "000"
    else:             HeadEr = N + "0000"
    return bytes.fromhex(HeadEr + L + PkEnc)

# ============================================================
#  EMOTE SYSTEM
# ============================================================
def load_emotes_from_file(filename="emotes.json"):
    all_aliases = {}
    categorized_emotes = {}
    current_category = "Uncategorized"
    print(f"📦 '{filename}' LOADING EMOTES...")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if not line: continue
                if line.startswith("#"):
                    current_category = line.replace("#", "").strip()
                    categorized_emotes.setdefault(current_category, [])
                    continue
                match = re.search(r"'([^']+)':\s*(\d+)", line)
                if match:
                    alias = match.group(1).strip().lower()
                    emote_id = int(match.group(2))
                    all_aliases[alias] = emote_id
                    if not alias.isdigit():
                        categorized_emotes.setdefault(current_category, [])
                        if alias not in categorized_emotes[current_category]:
                            categorized_emotes[current_category].append(alias)
    except FileNotFoundError:
        print(f"❌ {filename} not found")
    except Exception as e:
        print(f"❌ Emote load error: {e}")
    print(f"✅ Loaded: {len(all_aliases)} emotes")
    return all_aliases, categorized_emotes

def get_menu_pages(categorized_emotes):
    pages = []
    current_msg = "[B][C][FF0000]🔥 ᎷAH!Ꮢ ᏋᎷOᎿᏋ ᎷᏋᏁᏌ 🔥\n[B][C][FFFFFF]━━━━━━━━━━━━━━━━━━\n"
    for category, emotes in categorized_emotes.items():
        if not emotes: continue
        header = f"\n[B][C][00FFFF]◈ {category.upper()} ◈\n"
        if len(current_msg) + len(header) > 420:
            pages.append(current_msg + "\n[B][C][00FF00]>>> Next Page...")
            current_msg = f"[B][C][00FFFF]◈ {category.upper()} (Cont) ◈\n"
        else:
            current_msg += header
        for name in emotes:
            color = random.choice(SAFE_COLORS)
            line_item = f"{color}➥ {name}\n"
            if len(current_msg) + len(line_item) > 450:
                pages.append(current_msg + "\n[B][C][00FF00]>>> Next Page...")
                current_msg = f"[B][C][00FFFF]◈ {category.upper()} (Cont) ◈\n" + line_item
            else:
                current_msg += line_item
    current_msg += "[B][C][FFFFFF]━━━━━━━━━━━━━━━━━━\n[B][C][FF0000]💡 Type name to play!"
    pages.append(current_msg)
    return pages