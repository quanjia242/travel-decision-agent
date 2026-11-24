"""
出行决策 Agent 工具集 —— 私有模块（下划线开头，不映射为公开路由）
================================================================

对应课程《EdgeOne Makers - WorkBuddy 智能体搭建手册》第四步「使用自然语言改造 Agent」。

设计约定：
1. 所有密钥只从环境变量读取（AMAP_API_KEY），不写进代码、日志、提示词或返回值。
2. 每个工具统一返回 JSON 字符串：
       {"ok": true,  "data": ...}
       {"ok": false, "error": "...", "hint": "..."}
   工具失败时必须把 error / hint 转述给用户，禁止编造地点、门店或距离。
3. 地点、门店、距离一律以高德 Web 服务返回为准，不由模型自行生成。

依赖：仅 Python 标准库（urllib），不引入额外第三方包，便于本地与 Makers 沙箱一致运行。
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Annotated

from agents import function_tool


AMAP_BASE = "https://restapi.amap.com"
HTTP_TIMEOUT = 8  # 秒


def _dumps(obj: object) -> str:
    """统一序列化，保证中文可读。"""
    return json.dumps(obj, ensure_ascii=False)


def _amap_get(path: str, params: dict) -> dict:
    """调用高德 Web 服务 API，统一处理网络异常与业务错误码。

    返回 {"ok": True, "data": 原始响应} 或 {"ok": False, "error": ..., "hint": ...}。
    绝不把 key 拼进错误信息。
    """
    key = os.getenv("AMAP_API_KEY", "").strip()
    if not key:
        return {
            "ok": False,
            "error": "AMAP_API_KEY 未配置",
            "hint": "请在本地 .env 或 EdgeOne Makers 项目环境变量中配置高德开放平台的「Web 服务」Key",
        }

    query = {**params, "key": key, "output": "json"}
    url = f"{AMAP_BASE}{path}?{urllib.parse.urlencode(query)}"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "travel-decision-agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # URLError / timeout / JSON 解析失败等
        return {
            "ok": False,
            "error": f"地图接口请求失败: {type(exc).__name__}",
            "hint": "检查网络出口是否可访问 restapi.amap.com、Key 是否有效、接口权限是否开通",
        }

    if payload.get("status") != "1":
        return {
            "ok": False,
            "error": f"地图接口返回错误: {payload.get('info', 'unknown')}",
            "code": payload.get("infocode"),
            "hint": "常见原因：Key 类型不是 Web 服务、账号未实名、服务未启用、当日配额用尽、参数不合法",
        }
    return {"ok": True, "data": payload}


def _poi_brief(poi: dict) -> dict:
    """把高德 POI 精简成 Agent 需要的字段。"""
    return {
        "name": poi.get("name"),
        "id": poi.get("id"),
        "address": poi.get("address"),
        "location": poi.get("location"),  # "lng,lat"
        "type": poi.get("type"),
        "distance_m": int(poi.get("distance") or 0),
    }


# ========== 工具 1：位置解析 ==========
@function_tool
def geocode_location(
    location: Annotated[str, "用户描述的位置，如『红莲南路地铁站』『国贸』『北京市海淀区』"],
    city: Annotated[str, "城市名，可留空；用于消除同名地点歧义，如『北京』"] = "",
) -> str:
    """把用户描述的位置转换成经纬度坐标。

    调用条件：凡是需要做「附近 / 距离」检索，必须先调用本工具拿到起点坐标。
    输出：location 为 'lng,lat' 字符串，后续工具都用它作为 origin。
    """
    result = _amap_get("/v3/geocode/geo", {"address": location, "city": city})
    if not result["ok"]:
        return _dumps(result)

    geocodes = result["data"].get("geocodes") or []
    if not geocodes:
        return _dumps({
            "ok": False,
            "error": f"未能解析位置『{location}』",
            "hint": "请向用户追问更具体的地点，或补充城市名后重试",
        })

    geo = geocodes[0]
    return _dumps({
        "ok": True,
        "data": {
            "location": geo.get("location"),
            "formatted_address": geo.get("formatted_address"),
            "city": geo.get("city"),
            "level": geo.get("level"),
        },
    })


# ========== 工具 2：检索附近商场 ==========
@function_tool
def search_nearby_malls(
    origin: Annotated[str, "起点经纬度，格式 'lng,lat'，来自 geocode_location"],
    radius: Annotated[int, "搜索半径（米），默认 5000，最大 50000"] = 5000,
    keywords: Annotated[str, "商场关键词，默认『商场|购物中心』；可留空表示不限"] = "商场|购物中心",
) -> str:
    """检索起点附近的商场 / 购物中心，返回名称、地址、经纬度与直线距离（米）。

    调用条件：已拿到起点坐标，需要生成候选商场列表。
    输出按距离由近到远排序；候选为空时可增大 radius 重试，并如实告知用户。
    """
    params = {
        "location": origin,
        "keywords": keywords,
        "radius": min(max(int(radius), 100), 50000),
        "sortrule": "distance",
        "offset": 20,
        "page": 1,
    }
    result = _amap_get("/v3/place/around", params)
    if not result["ok"]:
        return _dumps(result)

    pois = result["data"].get("pois") or []
    malls = [_poi_brief(poi) for poi in pois]
    return _dumps({
        "ok": True,
        "data": {
            "origin": origin,
            "radius_m": params["radius"],
            "count": len(malls),
            "malls": malls,
        },
        "hint": "未找到候选时请增大 radius 或去掉关键词后重试，不要编造商场" if not malls else None,
    })


# ========== 工具 3：核对品牌 / 门店匹配 ==========
@function_tool
def search_brands_in_mall(
    brands: Annotated[str, "要核对的品牌或门店名，多个用 | 分隔，如『倍轻松|西厅村屋』"],
    mall_location: Annotated[str, "商场经纬度 'lng,lat'，来自 search_nearby_malls"],
    mall_name: Annotated[str, "商场名称，仅用于结果展示"] = "",
    radius: Annotated[int, "在商场周边检索门店的半径（米），默认 1000"] = 1000,
) -> str:
    """核对某个商场内 / 周边是否存在用户指定的品牌门店，返回逐品牌匹配证据。

    调用条件：已有候选商场，且用户提出了品牌 / 门店偏好。
    输出：每个品牌的 matched 布尔值、匹配到的门店名称与地址、all_matched 总判定。
    注意：检索半径默认 1000 米，覆盖商场内部及紧邻街区；不要凭品牌常识推断 matched。
    """
    brand_list = [b.strip() for b in brands.split("|") if b.strip()]
    if not brand_list:
        return _dumps({"ok": False, "error": "brands 为空", "hint": "请传入至少一个品牌名"})

    checked = []
    for brand in brand_list:
        single = _amap_get("/v3/place/around", {
            "location": mall_location,
            "keywords": brand,
            "radius": min(max(int(radius), 100), 50000),
            "sortrule": "distance",
            "offset": 5,
            "page": 1,
        })
        if not single["ok"]:
            # 单个品牌查询失败不影响其它品牌，但必须如实记录
            checked.append({
                "brand": brand,
                "matched": False,
                "error": single["error"],
                "hint": single["hint"],
            })
            continue

        shops = [_poi_brief(poi) for poi in (single["data"].get("pois") or [])]
        checked.append({
            "brand": brand,
            "matched": bool(shops),
            "shops": shops[:5],
        })

    failed_brands = [item["brand"] for item in checked if "error" in item]
    if failed_brands and len(failed_brands) == len(checked):
        # 全部品牌查询都失败（通常是 Key / 网络 / 权限问题）：整体判为工具失败，
        # 让 Agent 转述原因，而不是把「没查到」误当成「没有这家店」。
        return _dumps({
            "ok": False,
            "error": f"品牌核对全部失败：{checked[0].get('error')}",
            "hint": checked[0].get("hint"),
            "failed_brands": failed_brands,
        })

    all_matched = all(item.get("matched") is True for item in checked)
    payload = {
        "ok": True,
        "data": {
            "mall": mall_name or "(未命名商场)",
            "mall_location": mall_location,
            "brands": checked,
            "all_matched": all_matched,
            "failed_brands": failed_brands,
        },
    }
    if failed_brands:
        payload["hint"] = "部分品牌核对失败，须向用户说明原因，且不能把失败等同于『没有该门店』"
    return _dumps(payload)


# ========== 工具 4：距离计算 ==========
@function_tool
def get_distance(
    origins: Annotated[str, "起点经纬度 'lng,lat'；多个起点用 | 分隔"],
    destination: Annotated[str, "终点（商场）经纬度 'lng,lat'"],
    mode: Annotated[str, "距离类型：0=直线距离（默认），1=驾车，2=步行，3=骑行"] = "0",
) -> str:
    """计算起点到商场的距离（米），用于按距离排序比较候选结果。

    调用条件：需要精确比较多个候选商场的远近时。
    输出：每条结果的 distance_m 与 duration_s（耗时，直线距离时可能为空）。
    """
    result = _amap_get("/v3/distance", {
        "origins": origins,
        "destination": destination,
        "type": mode,
    })
    if not result["ok"]:
        return _dumps(result)

    rows = result["data"].get("results") or []
    return _dumps({
        "ok": True,
        "data": {
            "destination": destination,
            "mode": mode,
            "items": [{
                "origin": row.get("origin"),
                "origin_id": row.get("origin_id"),
                "distance_m": int(row.get("distance") or 0),
                "duration_s": row.get("duration"),
            } for row in rows],
        },
    })
