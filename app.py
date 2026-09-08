import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("AN_GIA_SECRET_KEY", "an-gia-local-ordering-secret-2026")
DB_FILE = "vietnam_food.db"
AI_RATE_LIMIT = {}
# One-day promotion: all menu items and selected add-ons are charged at 90%.
# The final amount is calculated again on the server; browser display alone
# can never decide an order total.
PROMOTION_DATE = "2026/08/16"
PROMOTION_RATE = Decimal("0.90")
POINT_VALUE_NTD = 5
CASH_POINT_VALUE_NTD = 1
NO_ADDONS_MARKER = "__an_gia_no_addons__"


def promotion_is_active(order_time=None):
    current_time = order_time or datetime.now()
    return current_time.strftime("%Y/%m/%d") == PROMOTION_DATE


def promotional_price(amount, order_time=None):
    """Return the one-item 9-discount price only on the promotion date."""
    if not promotion_is_active(order_time):
        return int(amount)
    return int((Decimal(str(amount)) * PROMOTION_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def reward_points_for_amount(amount):
    """Every NT$50 spent earns one point; fractions always round up."""
    amount = max(0, int(amount))
    return (amount + 49) // 50 if amount else 0


def parse_menu_addons(raw_value):
    """Read the per-dish add-ons saved by the administrator.

    The database stores a small JSON object, for example
    ``{"加蛋／Thêm trứng": 10}``.  Invalid legacy values safely fall back
    to no per-dish configuration, so the normal shop add-ons continue to work.
    """
    if not raw_value:
        return {}
    try:
        value = json.loads(raw_value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    parsed = {}
    for name, price in value.items():
        if name == NO_ADDONS_MARKER:
            continue
        if isinstance(name, str) and name.strip() and isinstance(price, int) and 0 <= price <= 1000:
            parsed[name.strip()] = price
    return parsed


def parse_menu_addon_rows(names, prices):
    """Validate the editable per-item add-on rows from the admin page."""
    if len(names) != len(prices) or len(names) > 20:
        abort(400, "加料資料格式錯誤")
    result = {}
    for name, price_text in zip(names, prices):
        name = name.strip()
        price_text = price_text.strip()
        if not name and not price_text:
            continue
        try:
            price = int(price_text)
        except ValueError:
            abort(400, "加料金額必須為整數。")
        if not name or name == NO_ADDONS_MARKER or price < 0 or price > 1000 or name in result:
            abort(400, "加料名稱或金額無效，且名稱不可重複。")
        result[name] = price
    return result


def parse_menu_addon_text(raw_text):
    """Convert the admin textarea (one ``名稱 | 金額`` per line) to JSON data."""
    if not raw_text.strip():
        return {}
    result = {}
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" not in line:
            abort(400, "加料格式錯誤，請使用「加料名稱／Tên thêm | 金額」。")
        name, price_text = (part.strip() for part in line.rsplit("|", 1))
        try:
            price = int(price_text)
        except ValueError:
            abort(400, "加料金額必須為整數。")
        if not name or price < 0 or price > 1000:
            abort(400, "加料名稱或金額無效。")
        result[name] = price
    return result


def menu_addon_text(raw_value):
    return "\n".join(f"{name} | {price}" for name, price in parse_menu_addons(raw_value).items())


def parse_hidden_addons(raw_value):
    """Read the per-item add-ons the administrator has hidden from customers."""
    if not raw_value:
        return set()
    try:
        values = json.loads(raw_value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return set()
    return {value.strip() for value in values if isinstance(value, str) and value.strip()}
PHO_DESCRIPTIONS = {
    "Phở bò ": "牛骨、牛腱與洋蔥慢熬清甜湯頭，配河粉、蔥花與香菜。",
    "Phở gà ": "雞骨熬湯搭配手撕雞肉、薑絲、蔥花與柔滑河粉。",
    "Phở bò chín": "熟牛肉片加入牛骨高湯，佐九層塔與豆芽增添清香。",
    "Phở bò viên": "彈牙牛肉丸、河粉與洋蔥片，湯頭濃郁而不膩口。",
    "Phở gân": "牛筋慢燉至軟嫩，搭配牛骨湯、河粉與新鮮香草。",
    "Bún chả ": "炭烤豬肉丸與五花肉，配米線、生菜及酸甜魚露沾汁。",
    "Bún nem ": "酥脆炸春捲、米線、薄荷與醃漬蔬菜，淋上清爽魚露。",
    "Bún gà Hà Nội": "嫩雞肉、米線、洋蔥與香菜，以清雞湯帶出自然甜味。",
    "Bún riêu ": "蟹肉番茄湯底加入豆腐、米線與紫蘇，酸香開胃。",
    "Bún mọc ": "豬肉丸、木耳、米線與骨湯，帶有胡椒與蔥香。",
    "Hủ Tiếu Nam Vang": "豬骨湯搭配蝦仁、豬肉、鵪鶉蛋與粿條，香甜豐富。",
    "Hủ Tiếu khô": "乾拌粿條以蒜酥、肉末與特製醬汁拌勻，另附清湯。",
    "Hủ Tiếu hải sản": "鮮蝦、花枝與魚片搭配粿條，湯頭清甜帶海味。",
    "Hủ Tiếu bò viên": "牛肉丸、豆芽與韭菜配粿條，適合喜歡清爽口感的人。",
    "Hủ Tiếu xá xíu": "蜜汁叉燒、豆芽與油蔥酥，讓粿條香氣更有層次。",
    "Bánh Canh giò heo": "米苔目配燉豬腳、蔥花與胡椒，湯頭濃厚滑順。",
    "Bánh Canh cua": "蟹肉、蟹味羹湯與米苔目，加入香菜和蔥酥提香。",
    "Bánh Canh cá lóc": "鱸魚片與米苔目，使用薑絲、蔥花熬出鮮甜魚湯。",
    "Bánh Canh hải sản": "蝦、花枝與魚片搭配米苔目，口感飽滿、海味清甜。",
    "Bánh Canh gà": "雞肉、米苔目和香菇，以雞骨湯煮出溫潤香氣。",
}
PHO_DESCRIPTIONS["Bún bò Huế"] = "牛骨湯加入香茅、辣椒與蝦醬熬煮，搭配嫩牛肉片、米線和新鮮香草。"
PHO_VI_DESCRIPTIONS = {
    "Phở bò Hà Nội": "Nước dùng xương bò, thịt bò, hành tây, bánh phở, hành lá và rau mùi.",
    "Phở gà Hà Nội": "Nước dùng gà trong, thịt gà xé, gừng, hành lá và bánh phở mềm.",
    "Phở bò chín": "Thịt bò chín, nước dùng xương bò, húng quế và giá đỗ tươi.",
    "Phở bò viên": "Bò viên dai ngon, bánh phở, hành tây và nước dùng đậm vị.",
    "Phở gân": "Gân bò hầm mềm, nước dùng xương bò, bánh phở và rau thơm.",
    "Bún chả Hà Nội": "Chả thịt nướng và ba chỉ nướng ăn cùng bún, rau sống, nước mắm chua ngọt.",
    "Bún nem Hà Nội": "Nem rán giòn, bún, bạc hà và rau ngâm chua dùng với nước mắm.",
    "Bún gà Hà Nội": "Thịt gà mềm, bún, hành tây, rau mùi và nước dùng gà thanh ngọt.",
    "Bún riêu cua Bắc": "Nước riêu cua cà chua, đậu hũ, bún và lá tía tô thơm.",
    "Bún mọc Hà Nội": "Mọc thịt, nấm mèo, bún và nước xương thơm mùi tiêu hành.",
    "Hủ Tiếu Nam Vang": "Nước xương ngọt với tôm, thịt heo, trứng cút và hủ tiếu.",
    "Hủ Tiếu khô": "Hủ tiếu trộn tỏi phi, thịt băm và nước sốt đặc biệt, ăn kèm nước dùng.",
    "Hủ Tiếu hải sản": "Tôm, mực, cá và hủ tiếu trong nước dùng ngọt vị biển.",
    "Hủ Tiếu bò viên": "Bò viên, giá, hẹ và hủ tiếu nhẹ nhàng, dễ ăn.",
    "Hủ Tiếu xá xíu": "Xá xíu mật ong, giá đỗ, hành phi và hủ tiếu thơm đậm đà.",
    "Bánh Canh giò heo": "Bánh canh sợi mềm cùng giò heo hầm, hành lá và tiêu.",
    "Bánh Canh cua": "Thịt cua, nước súp sánh nhẹ, bánh canh, rau mùi và hành phi.",
    "Bánh Canh cá lóc": "Cá lóc, gừng, hành lá và bánh canh trong nước dùng ngọt thanh.",
    "Bánh Canh hải sản": "Tôm, mực, cá và bánh canh đầy đặn, ngọt vị hải sản.",
    "Bánh Canh gà": "Thịt gà, nấm, bánh canh và nước dùng gà ấm áp.",
    "Bún bò Huế": "Nước xương bò nấu sả, ớt và mắm ruốc, dùng với thịt bò, bún và rau thơm.",
}
DRINKS_DESCRIPTIONS = {
    "Cà phê sữa đá": "越南滴漏咖啡加入香甜煉乳與冰塊，濃郁順口。",
    "Cà phê đen đá": "現沖滴漏黑咖啡加冰，保留咖啡豆的醇厚香氣。",
    "Cà phê dừa": "咖啡、椰奶與椰子冰沙交融，口感綿密清涼。",
    "Cà phê trứng": "濃縮咖啡覆上香滑蛋奶泡，甜香柔順。",
    "Cà phê muối": "鹹香奶霜平衡咖啡的微苦，層次細緻。",
    "Ca cao dừa": "可可與椰奶搭配冰塊，帶可可香與椰香。",
    "Chè lá dứa": "斑斕、椰奶與Q彈配料製成的清甜冰品。",
    "Chè ba màu": "紅豆、綠豆、斑斕凍與椰奶組成的三色甜品。",
    "Sữa bắp (sữa ngô)": "新鮮玉米（南越：bắp；北越：ngô）與牛奶調製，帶自然玉米香與柔順奶香。",
    "Nước me đá": "羅望子果肉、糖水與冰塊調製，酸甜開胃。",
    "Gỏi cuốn tôm": "鮮蝦、米線、生菜與香草包入米紙，佐魚露沾醬。",
    "Bánh tráng trộn": "米紙條拌入青芒果、蝦米、鵪鶉蛋、香草與酸甜醬汁，酸香開胃。",
    "Chả giò": "豬肉、木耳與蔬菜製成金黃酥脆的越南炸春捲。",
    "Bánh tôm": "鮮蝦裹上米漿油炸，外酥內鮮，附清爽沾醬。",
    "Bánh xèo": "薑黃米漿煎餅包入蝦仁、豬肉與豆芽，外脆內香。",
    "Bánh cuốn": "柔滑米皮包入豬肉末與木耳，搭配炸紅蔥頭與魚露醬。",
    "Bánh flan": "雞蛋、牛奶與焦糖蒸製，滑嫩香甜。",
    "Chè khoai mì": "木薯、椰奶與花生慢煮成濃郁甜湯。",
    "Sữa chua dâu": "草莓與優格搭配，酸甜清爽，適合作為餐後甜點。",
    "Chè khoai môn": "芋頭、椰奶與西米露熬煮，香濃綿密。",
}
DRINKS_VI_DESCRIPTIONS = {
    "Cà phê sữa đá": "Cà phê phin, sữa đặc và đá mát lạnh.",
    "Cà phê đen đá": "Cà phê phin đen đậm đà dùng cùng đá.",
    "Cà phê dừa": "Cà phê, nước cốt dừa và đá xay béo mịn.",
    "Cà phê trứng": "Cà phê đậm vị phủ kem trứng sữa béo thơm.",
    "Cà phê muối": "Cà phê với lớp kem mặn béo, cân bằng vị đắng dịu.",
    "Ca cao dừa": "Ca cao, nước cốt dừa và đá mát lạnh.",
    "Chè lá dứa": "Lá dứa, nước cốt dừa và topping dai ngon.",
    "Chè ba màu": "Đậu đỏ, đậu xanh, thạch lá dứa và nước cốt dừa.",
    "Sữa bắp (sữa ngô)": "Sữa bắp (miền Nam) / sữa ngô (miền Bắc) từ ngô tươi và sữa, ngọt dịu dễ uống.",
    "Nước me đá": "Me chín, nước đường và đá, chua ngọt dễ uống.",
    "Gỏi cuốn tôm": "Tôm tươi, bún, rau sống và rau thơm cuốn bánh tráng.",
    "Bánh tráng trộn": "Bánh tráng cắt sợi trộn xoài xanh, tôm khô, trứng cút, rau thơm và nước sốt chua ngọt.",
    "Chả giò": "Thịt heo, nấm mèo và rau củ cuốn chiên giòn.",
    "Bánh tôm": "Tôm tươi chiên giòn trong lớp bột gạo, dùng kèm nước chấm.",
    "Bánh xèo": "Bột gạo nghệ, tôm, thịt heo và giá đỗ chiên giòn.",
    "Bánh cuốn": "Bánh cuốn mềm với thịt heo băm, nấm mèo, hành phi và nước mắm.",
    "Bánh flan": "Trứng, sữa và caramel mềm mịn, thơm ngọt.",
    "Chè khoai mì": "Khoai mì, nước cốt dừa và đậu phộng béo thơm.",
    "Sữa chua dâu": "Dâu tây tươi và sữa chua mát lạnh, chua ngọt nhẹ nhàng.",
    "Chè khoai môn": "Khoai môn, nước cốt dừa và bột báng béo bùi.",
}
SHOP_ADDONS = {
    "pho": {"加肉 / Thêm thịt": 30, "加檸檬 / Thêm chanh": 0, "加辣椒 / Thêm ớt": 0},
    "banh-mi": {"加肉 / Thêm thịt": 30, "加辣椒 / Thêm ớt": 0, "加蛋 / Thêm trứng": 10},
    "drinks": {"加珍珠 / Trân châu": 15, "加椰子果凍 / Thạch dừa": 15, "加仙草凍 / Sương sáo": 15, "加椰果 / Nata de coco": 15, "加布丁 / Bánh flan": 15},
}
PAYMENT_METHODS = ("現金／Tiền mặt",)
ORDER_STATUSES = ("已接單", "製作中", "已完成可領取", "已領取")
REGION_OPTIONS = ("北越風味", "中越風味", "南越風味", "全越南常見")
RECOMMENDATION_OPTIONS = ("", "招牌", "老闆推薦")
AVAILABILITY_OPTIONS = ("供應中", "暫停供應")
MENU_CATEGORY_OPTIONS = {
    "pho": (
        ("河粉／Phở", "河粉／Phở"),
        ("米線／Bún", "米線／Bún"),
        ("粿條／Hủ Tiếu", "粿條／Hủ Tiếu"),
        ("米苔目／Bánh Canh", "米苔目／Bánh Canh"),
    ),
    "banh-mi": (
        ("越南法國麵包", "越南法國麵包／Bánh mì"),
        ("越南飲品", "越南飲品／Đồ uống Việt Nam"),
    ),
    "drinks": (
        ("越南咖啡", "越南咖啡／Cà phê Việt Nam"),
        ("特色飲品", "特色飲品／Đồ uống đặc biệt"),
        ("越南點心", "越南點心／Món ăn nhẹ Việt Nam"),
        ("越南甜點", "越南甜點／Tráng miệng Việt Nam"),
    ),
}
AVAILABILITY_VI_LABELS = {
    "供應中": "Còn hàng",
    "暫停供應": "Tạm hết hàng",
}
REGION_VI_LABELS = {
    "北越風味": "Phong vị miền Bắc",
    "中越風味": "Phong vị miền Trung",
    "南越風味": "Phong vị miền Nam",
    "全越南常見": "Phổ biến trên khắp Việt Nam",
}
RECOMMENDATION_VI_LABELS = {
    "": "Không hiển thị",
    "招牌": "Món đặc trưng",
    "老闆推薦": "Chủ quán đề cử",
}
SHOPS = {
    "pho": {"name": "安嘉河食", "vi_name": "An Gia Phở", "tagline": "北部河粉與米線｜南部粿條與米苔目", "icon": "🍜"},
    "banh-mi": {"name": "安嘉越南麵包", "vi_name": "Bánh Mì An Gia", "tagline": "越南法國麵包專賣店｜北部與南部風味", "icon": "🥖"},
    "drinks": {"name": "安嘉越南食世界", "vi_name": "An Gia – Thế Giới Ẩm Thực Việt", "tagline": "越南飲品與點心店", "icon": "☕"},
}

SHOP_ADDRESSES = {
    "pho": "新北市淡水區中正路 168 號｜Đường Zhongzheng 168, Quận Tamsui, Thành phố Tân Bắc",
    "banh-mi": "新北市淡水區學府路 88 號｜Đường Xuefu 88, Quận Tamsui, Thành phố Tân Bắc",
    "drinks": "新北市淡水區英專路 120 號｜Đường Yingzhuan 120, Quận Tamsui, Thành phố Tân Bắc",
}

def get_db():
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row; return conn


def get_point_value(conn=None):
    """Return the current NT-dollar value of one reward point.

    Administrators can change this value from the back office.  Keeping the
    fallback preserves existing orders and makes a fresh database usable.
    """
    close_after = conn is None
    if close_after:
        conn = get_db()
    try:
        row = conn.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key='point_value_ntd'"
        ).fetchone()
        value = int(row["setting_value"]) if row else POINT_VALUE_NTD
        return value if 1 <= value <= 1000 else POINT_VALUE_NTD
    except sqlite3.OperationalError:
        return POINT_VALUE_NTD
    finally:
        if close_after:
            conn.close()


def get_cash_point_value(conn=None):
    """Return the amount discounted by one point in the checkout field."""
    close_after = conn is None
    if close_after:
        conn = get_db()
    try:
        row = conn.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key='cash_point_value_ntd'"
        ).fetchone()
        value = int(row["setting_value"]) if row else CASH_POINT_VALUE_NTD
        return value if 1 <= value <= 1000 else CASH_POINT_VALUE_NTD
    except sqlite3.OperationalError:
        return CASH_POINT_VALUE_NTD
    finally:
        if close_after:
            conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,vi_name TEXT NOT NULL,price INTEGER NOT NULL,category TEXT NOT NULL,shop TEXT)")
        # 預設菜單被後台下架後，保留這筆記錄，避免系統下次啟動又自動補回。
        conn.execute("CREATE TABLE IF NOT EXISTS retired_menu_items (shop TEXT NOT NULL, vi_name TEXT NOT NULL, retired_at TEXT NOT NULL, PRIMARY KEY (shop, vi_name))")
        conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT,customer_name TEXT NOT NULL,item_name TEXT NOT NULL,addon_name TEXT NOT NULL,quantity INTEGER NOT NULL,total_price INTEGER NOT NULL,pay_method TEXT NOT NULL,status TEXT NOT NULL DEFAULT '已接單',created_at TEXT,shop_name TEXT)")
        for table, column in (("menu", "shop"), ("orders", "created_at"), ("orders", "shop_name")):
            if column not in [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]: conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT")
        conn.execute("CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER NOT NULL,menu_item_id INTEGER NOT NULL,item_name TEXT NOT NULL,addon_name TEXT NOT NULL,unit_price INTEGER NOT NULL,quantity INTEGER NOT NULL,line_total INTEGER NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS customer_accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, display_name TEXT NOT NULL, phone TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
        if "points" not in [r["name"] for r in conn.execute("PRAGMA table_info(customer_accounts)")]:
            conn.execute("ALTER TABLE customer_accounts ADD COLUMN points INTEGER NOT NULL DEFAULT 0")
        if "welcome_points_claimed" not in [r["name"] for r in conn.execute("PRAGMA table_info(customer_accounts)")]:
            # Existing members stay eligible for the same 10-point welcome gift.
            conn.execute("ALTER TABLE customer_accounts ADD COLUMN welcome_points_claimed INTEGER NOT NULL DEFAULT 0")
        conn.execute("UPDATE customer_accounts SET points=0 WHERE points IS NULL OR points<0")
        for column in ("description", "vi_description", "image_url", "region", "recommendation_tag"):
            if column not in [r["name"] for r in conn.execute("PRAGMA table_info(menu)")]:
                conn.execute(f"ALTER TABLE menu ADD COLUMN {column} TEXT")
        if "addon_config" not in [r["name"] for r in conn.execute("PRAGMA table_info(menu)")]:
            conn.execute("ALTER TABLE menu ADD COLUMN addon_config TEXT NOT NULL DEFAULT ''")
        if "hidden_addons" not in [r["name"] for r in conn.execute("PRAGMA table_info(menu)")]:
            conn.execute("ALTER TABLE menu ADD COLUMN hidden_addons TEXT NOT NULL DEFAULT '[]'")
        # 每道菜可由後台各別設定兌換所需點數；既有餐點一律先採 2 點。
        if "exchange_points" not in [r["name"] for r in conn.execute("PRAGMA table_info(menu)")]:
            conn.execute("ALTER TABLE menu ADD COLUMN exchange_points INTEGER NOT NULL DEFAULT 2")
        conn.execute("UPDATE menu SET exchange_points=2 WHERE exchange_points IS NULL OR exchange_points<1")
        if "availability_status" not in [r["name"] for r in conn.execute("PRAGMA table_info(menu)")]:
            conn.execute("ALTER TABLE menu ADD COLUMN availability_status TEXT NOT NULL DEFAULT '供應中'")
        conn.execute("UPDATE menu SET availability_status='暫停供應' WHERE availability_status='已賣完'")
        conn.execute("UPDATE menu SET availability_status='供應中' WHERE availability_status IS NULL OR availability_status NOT IN ('供應中','暫停供應')")
        if "updated_at" not in [r["name"] for r in conn.execute("PRAGMA table_info(menu)")]:
            conn.execute("ALTER TABLE menu ADD COLUMN updated_at TEXT")
        conn.execute("UPDATE menu SET updated_at=? WHERE updated_at IS NULL OR TRIM(updated_at)=''", (datetime.now().strftime("%Y/%m/%d %H:%M:%S"),))
        conn.execute("UPDATE menu SET region='全越南常見' WHERE region IS NULL OR TRIM(region)='' ")
        for column, default in (("phone", ""), ("payment_status", "待付款")):
            if column not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {column} TEXT NOT NULL DEFAULT '{default}'")
        for column in ("points_earned", "points_redeemed"):
            if column not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0")
        if "points_exchange_count" not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
            conn.execute("ALTER TABLE orders ADD COLUMN points_exchange_count INTEGER NOT NULL DEFAULT 0")
        if "points_exchange_points" not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
            conn.execute("ALTER TABLE orders ADD COLUMN points_exchange_points INTEGER NOT NULL DEFAULT 0")
            # Historical orders were all exchanged at the original 2-point rate.
            conn.execute("UPDATE orders SET points_exchange_points=COALESCE(points_exchange_count, 0)*2")
        # points_redeemed stores the number of points used.  Keep the actual
        # NT-dollar value in a separate field so the point value can be changed
        # without corrupting historical order totals.
        if "points_redemption_value" not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
            conn.execute("ALTER TABLE orders ADD COLUMN points_redemption_value INTEGER NOT NULL DEFAULT 0")
            conn.execute("UPDATE orders SET points_redemption_value=MAX(COALESCE(points_redeemed, 0)-COALESCE(points_exchange_points, 0), 0)")
        if "points_exchange_value" not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
            conn.execute("ALTER TABLE orders ADD COLUMN points_exchange_value INTEGER NOT NULL DEFAULT 0")
        # subtotal_price preserves the menu total before reward points are
        # redeemed.  total_price is intentionally kept as the amount payable.
        if "subtotal_price" not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
            conn.execute("ALTER TABLE orders ADD COLUMN subtotal_price INTEGER")
        conn.execute("UPDATE orders SET subtotal_price=total_price + COALESCE(points_redeemed, 0) WHERE subtotal_price IS NULL")
        if "payment_status" not in [r["name"] for r in conn.execute("PRAGMA table_info(orders)")]:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT")
        conn.execute("UPDATE orders SET payment_status='待付款' WHERE payment_status IS NULL OR payment_status='' ")
        conn.execute("UPDATE orders SET status='已接單' WHERE status IS NULL OR status NOT IN (?, ?, ?, ?)", ORDER_STATUSES)
        conn.execute("UPDATE orders SET created_at=? WHERE created_at IS NULL", (datetime.now().strftime("%Y/%m/%d"),))
        # 安嘉河食固定為四個分類，讓舊資料庫的分類名稱也一併整理。
        conn.execute("UPDATE menu SET category='河粉／Phở' WHERE shop='pho' AND vi_name LIKE 'Ph%'")
        conn.execute("UPDATE menu SET category='米線／Bún' WHERE shop='pho' AND vi_name LIKE 'Bún%'")
        conn.execute("UPDATE menu SET category='粿條／Hủ Tiếu' WHERE shop='pho' AND vi_name LIKE 'Hủ Tiếu%'")
        conn.execute("UPDATE menu SET category='米苔目／Bánh Canh' WHERE shop='pho' AND vi_name LIKE 'Bánh Canh%'")
        conn.execute("UPDATE menu SET name='順化牛肉米線', vi_name='Bún bò Huế', price=180, category='米線／Bún' WHERE shop='pho' AND vi_name LIKE 'Bún mọc%'")
        # Bún chả 與 Bún thịt nướng 是兩道不同的米線，保留各自中文名稱。
        conn.execute("UPDATE menu SET name='烤肉米線', category='米線／Bún' WHERE shop='pho' AND vi_name LIKE 'Bún chả%'")
        conn.execute("UPDATE menu SET name='涼拌烤肉米線', category='米線／Bún' WHERE shop='pho' AND vi_name LIKE 'Bún thịt nướng%'")
        conn.execute("UPDATE menu SET name='玉米牛奶', vi_name='Sữa bắp (sữa ngô)', category='特色飲品' WHERE shop='drinks' AND vi_name IN ('Chè đậu xanh', 'Sữa bắp')")
        conn.execute("UPDATE menu SET name='涼拌米紙', vi_name='Bánh tráng trộn', category='越南點心' WHERE shop='drinks' AND vi_name='Gỏi cuốn thịt nướng'")
        conn.execute("UPDATE menu SET name='草莓優格', vi_name='Sữa chua dâu', category='越南甜點' WHERE shop='drinks' AND vi_name='Chè chuối'")
        conn.execute("UPDATE menu SET name='越南粉捲', vi_name='Bánh cuốn', category='越南點心' WHERE shop='drinks' AND vi_name='Bánh khọt'")
        menu_items = [
            # 安嘉河食：北部 Phở／Bún，南部 Hủ Tiếu／Bánh Canh，共 20 道
            ("招牌牛肉河粉","Phở bò ",170,"河粉","pho"),("雞肉河粉","Phở gà ",155,"河粉","pho"),("熟牛肉河粉","Phở bò chín",170,"河粉","pho"),("河內牛肉丸河粉","Phở bò viên",175,"河粉","pho"),
            ("烤肉米線","Bún chả ",165,"米線","pho"),("北部炸春捲米線","Bún nem ",155,"米線","pho"),("雞肉米線","Bún gà Hà Nội",160,"米線","pho"),("蟹肉米線","Bún riêu cua Bắc",175,"米線","pho"),("順化牛肉米線","Bún bò Huế",180,"米線","pho"),
            ("西貢豬骨粿條","Hủ Tiếu Nam Vang",175,"粿條","pho"),("乾拌粿條","Hủ Tiếu khô",165,"粿條","pho"),("海鮮粿條","Hủ Tiếu hải sản",190,"粿條","pho"),("西貢牛肉粿條","Hủ Tiếu bò viên",175,"粿條","pho"),("叉燒粿條","Hủ Tiếu xá xíu",180,"粿條","pho"),
            ("豬腳米苔目","Bánh Canh giò heo",185,"米苔目","pho"),("越南蟹肉米苔目","Bánh Canh cua",195,"米苔目","pho"),("魚餅米苔目","Bánh Canh cá lóc",180,"米苔目","pho"),("海鮮米苔目","Bánh Canh hải sản",195,"米苔目","pho"),("雞肉米苔目","Bánh Canh gà",175,"米苔目","pho"),
            # 安嘉越南麵包：北部與南部風味，共 20 道
            ("河內豬肉醬法國麵包","Bánh mì pate Hà Nội",110,"北部風味","banh-mi"),("北部烤雞法國麵包","Bánh mì gà nướng",120,"北部風味","banh-mi"),("河內火腿法國麵包","Bánh mì giăm bông",115,"北部風味","banh-mi"),("北部肉鬆法國麵包","Bánh mì chà bông",110,"北部風味","banh-mi"),("河內豬排法國麵包","Bánh mì thịt heo",125,"北部風味","banh-mi"),("北部牛肉法國麵包","Bánh mì bò",130,"北部風味","banh-mi"),("河內香茅雞法國麵包","Bánh mì gà sả",120,"北部風味","banh-mi"),("北部煎蛋法國麵包","Bánh mì trứng",95,"北部風味","banh-mi"),("河內綜合法國麵包","Bánh mì đặc biệt Hà Nội",145,"北部風味","banh-mi"),("北部素食法國麵包","Bánh mì chay",100,"北部風味","banh-mi"),
            ("西貢烤肉法國麵包","Bánh mì thịt nướng",125,"南部風味","banh-mi"),("南部燒肉法國麵包","Bánh mì xá xíu",130,"南部風味","banh-mi"),("西貢烤牛肉法國麵包","Bánh mì bò nướng",135,"南部風味","banh-mi"),("南部炸雞法國麵包","Bánh mì gà chiên",125,"南部風味","banh-mi"),("西貢鮪魚法國麵包","Bánh mì cá ngừ",115,"南部風味","banh-mi"),("南部沙丁魚法國麵包","Bánh mì cá mòi",110,"南部風味","banh-mi"),("西貢起司法國麵包","Bánh mì phô mai",105,"南部風味","banh-mi"),("南部綜合法國麵包","Bánh mì đặc biệt Sài Gòn",150,"南部風味","banh-mi"),("西貢辣味雞法國麵包","Bánh mì gà cay",125,"南部風味","banh-mi"),("南部素食法國麵包","Bánh mì chay Sài Gòn",105,"南部風味","banh-mi"),
            # 安嘉越南食世界：飲品與點心，共 20 道
            ("越南煉乳冰咖啡","Cà phê sữa đá",75,"越南咖啡","drinks"),("越南黑咖啡","Cà phê đen đá",65,"越南咖啡","drinks"),("椰子咖啡","Cà phê dừa",95,"越南咖啡","drinks"),("蛋咖啡","Cà phê trứng",100,"越南咖啡","drinks"),("鹽咖啡","Cà phê muối",90,"越南咖啡","drinks"),("椰奶可可","Ca cao dừa",85,"特色飲品","drinks"),("斑斕椰奶","Chè lá dứa",80,"特色飲品","drinks"),("越南三色冰","Chè ba màu",85,"特色飲品","drinks"),("綠豆椰奶冰","Chè đậu xanh",80,"特色飲品","drinks"),("羅望子冰茶","Nước me đá",70,"特色飲品","drinks"),
            ("鮮蝦春捲","Gỏi cuốn tôm",95,"越南點心","drinks"),("烤肉春捲","Gỏi cuốn thịt nướng",100,"越南點心","drinks"),("炸春捲","Chả giò",85,"越南點心","drinks"),("越南炸蝦餅","Bánh tôm",110,"越南點心","drinks"),("越南煎餅","Bánh xèo",130,"越南點心","drinks"),("椰絲小煎餅","Bánh khọt",100,"越南點心","drinks"),("越南焦糖布丁","Bánh flan",65,"越南甜點","drinks"),("木薯椰奶甜湯","Chè khoai mì",75,"越南甜點","drinks"),("香蕉椰奶甜湯","Chè chuối",75,"越南甜點","drinks"),("芋頭椰奶甜湯","Chè khoai môn",80,"越南甜點","drinks"),
        ]
        # Only rebuild a truly legacy Pho menu.  The current menu uses the
        # bilingual category name below; checking the removed legacy name here
        # used to delete and recreate the Pho records at every application start,
        # which also lost each dish's image_url association.
        if conn.execute("SELECT 1 FROM menu WHERE shop='pho' AND category='粿條／Hủ Tiếu'").fetchone() is None:
            conn.execute("DELETE FROM menu WHERE shop='pho'")
        drinks_replacements = {
            "Chè đậu xanh": ("玉米牛奶", "Sữa bắp (sữa ngô)", 80, "特色飲品", "drinks"),
            "Gỏi cuốn thịt nướng": ("涼拌米紙", "Bánh tráng trộn", 100, "越南點心", "drinks"),
            "Chè chuối": ("草莓優格", "Sữa chua dâu", 75, "越南甜點", "drinks"),
            "Bánh khọt": ("越南粉捲", "Bánh cuốn", 100, "越南點心", "drinks"),
        }
        menu_items = [drinks_replacements.get(item[1], item) for item in menu_items]
        for item in menu_items:
            is_retired = conn.execute("SELECT 1 FROM retired_menu_items WHERE shop=? AND vi_name=?", (item[4], item[1])).fetchone()
            if not is_retired and conn.execute("SELECT 1 FROM menu WHERE name=? AND shop=?", (item[0], item[4])).fetchone() is None:
                conn.execute("INSERT INTO menu (name,vi_name,price,category,shop) VALUES (?,?,?,?,?)", item)
        conn.execute("UPDATE menu SET name='玉米牛奶', vi_name='Sữa bắp (sữa ngô)', category='特色飲品' WHERE shop='drinks' AND vi_name IN ('Chè đậu xanh', 'Sữa bắp')")
        conn.execute("UPDATE menu SET name='涼拌米紙', vi_name='Bánh tráng trộn', category='越南點心' WHERE shop='drinks' AND vi_name='Gỏi cuốn thịt nướng'")
        conn.execute("UPDATE menu SET name='草莓優格', vi_name='Sữa chua dâu', category='越南甜點' WHERE shop='drinks' AND vi_name='Chè chuối'")
        conn.execute("UPDATE menu SET name='越南粉捲', vi_name='Bánh cuốn', category='越南點心' WHERE shop='drinks' AND vi_name='Bánh khọt'")
        conn.execute("DELETE FROM menu WHERE shop='drinks' AND name='玉米牛奶' AND id NOT IN (SELECT MIN(id) FROM menu WHERE shop='drinks' AND name='玉米牛奶')")
        conn.execute("DELETE FROM menu WHERE shop='drinks' AND name IN ('玉米牛奶', '涼拌米紙', '草莓優格', '越南粉捲') AND id NOT IN (SELECT MIN(id) FROM menu WHERE shop='drinks' GROUP BY name)")
        conn.execute("UPDATE menu SET category='河粉／Phở' WHERE shop='pho' AND vi_name LIKE 'Ph%'")
        conn.execute("UPDATE menu SET category='米線／Bún' WHERE shop='pho' AND vi_name LIKE 'Bún%'")
        conn.execute("UPDATE menu SET category='粿條／Hủ Tiếu' WHERE shop='pho' AND vi_name LIKE 'Hủ Tiếu%'")
        conn.execute("UPDATE menu SET category='米苔目／Bánh Canh' WHERE shop='pho' AND vi_name LIKE 'Bánh Canh%'")

        conn.execute("UPDATE menu SET name='順化牛肉米線', vi_name='Bún bò Huế', price=180, category='米線／Bún' WHERE shop='pho' AND vi_name LIKE 'Bún mọc%'")

        # A previous seed name was renamed after insertion, which could create
        # duplicate Huế beef-noodle records on subsequent starts.  Keep the
        # original record and remove only duplicates that have never appeared
        # in an order, preserving all historical order details.
        conn.execute(
            "DELETE FROM menu WHERE shop='pho' AND name='順化牛肉米線' "
            "AND id NOT IN (SELECT MIN(id) FROM menu WHERE shop='pho' AND name='順化牛肉米線') "
            "AND id NOT IN (SELECT menu_item_id FROM order_items)"
        )

        conn.execute("UPDATE menu SET price=100 WHERE shop='pho'")

        conn.execute("CREATE TABLE IF NOT EXISTS app_settings (setting_key TEXT PRIMARY KEY, setting_value TEXT)")
        conn.execute(
            "INSERT OR IGNORE INTO app_settings (setting_key, setting_value) VALUES ('point_value_ntd', ?)",
            (str(POINT_VALUE_NTD),),
        )
        conn.execute(
            "INSERT OR IGNORE INTO app_settings (setting_key, setting_value) VALUES ('cash_point_value_ntd', ?)",
            (str(CASH_POINT_VALUE_NTD),),
        )
        if not conn.execute("SELECT 1 FROM app_settings WHERE setting_key='banh_mi_menu_15_5'").fetchone():
            conn.execute("DELETE FROM menu WHERE shop='banh-mi'")
            banh_mi_menu = [
                ("招牌越南法國麵包", "Bánh mì đặc biệt", 100, "越南法國麵包", "banh-mi"),
                ("烤豬肉法國麵包", "Bánh mì thịt nướng", 100, "越南法國麵包", "banh-mi"),
                ("烤雞肉法國麵包", "Bánh mì gà nướng", 100, "越南法國麵包", "banh-mi"),
                ("叉燒法國麵包", "Bánh mì xá xíu", 100, "越南法國麵包", "banh-mi"),
                ("牛肉法國麵包", "Bánh mì bò", 110, "越南法國麵包", "banh-mi"),
                ("火腿起司法國麵包", "Bánh mì jambon phô mai", 100, "越南法國麵包", "banh-mi"),
                ("肉鬆法國麵包", "Bánh mì chà bông", 95, "越南法國麵包", "banh-mi"),
                ("煎蛋法國麵包", "Bánh mì trứng", 90, "越南法國麵包", "banh-mi"),
                ("魚餅法國麵包", "Bánh mì chả cá", 100, "越南法國麵包", "banh-mi"),
                ("炸雞法國麵包", "Bánh mì gà chiên", 110, "越南法國麵包", "banh-mi"),
                ("香茅豬肉法國麵包", "Bánh mì thịt heo sả", 105, "越南法國麵包", "banh-mi"),
                ("辣味牛肉法國麵包", "Bánh mì bò cay", 110, "越南法國麵包", "banh-mi"),
                ("素食法國麵包", "Bánh mì chay", 90, "越南法國麵包", "banh-mi"),
                ("豆腐素食法國麵包", "Bánh mì đậu hũ", 95, "越南法國麵包", "banh-mi"),
                ("海鮮法國麵包", "Bánh mì hải sản", 115, "越南法國麵包", "banh-mi"),
                ("越南冰咖啡", "Cà phê sữa đá", 65, "越南飲品", "banh-mi"),
                ("越南黑咖啡", "Cà phê đen đá", 55, "越南飲品", "banh-mi"),
                ("檸檬茶", "Trà chanh", 45, "越南飲品", "banh-mi"),
                ("金桔茶", "Trà tắc", 45, "越南飲品", "banh-mi"),
                ("椰子水", "Nước dừa", 55, "越南飲品", "banh-mi"),
            ]
            conn.executemany("INSERT INTO menu (name,vi_name,price,category,shop) VALUES (?,?,?,?,?)", banh_mi_menu)
            conn.execute("INSERT INTO app_settings (setting_key, setting_value) VALUES ('banh_mi_menu_15_5','done')")
        conn.execute("UPDATE menu SET name=replace(replace(replace(replace(name,'北部',''),'南部',''),'河內',''),'西貢','') WHERE shop='banh-mi'")
        conn.execute("UPDATE menu SET vi_name=replace(replace(vi_name,'Hà Nội',''),'Sài Gòn','') WHERE shop='banh-mi'")
        if not conn.execute("SELECT 1 FROM app_settings WHERE setting_key='banh_mi_cleanup_v2'").fetchone():
            conn.execute("DELETE FROM menu WHERE shop='banh-mi' AND category NOT IN ('越南法國麵包','越南飲品')")
            conn.execute("INSERT INTO app_settings (setting_key, setting_value) VALUES ('banh_mi_cleanup_v2','done')")

        conn.execute("DELETE FROM menu WHERE shop='banh-mi' AND category LIKE '%風味%'")

        conn.execute("DELETE FROM menu WHERE shop='banh-mi' AND id NOT IN (SELECT MIN(id) FROM menu WHERE shop='banh-mi' GROUP BY name)")
        # Do this after legacy menu cleanup/creation, so a new database also
        # receives the labels during its very first initialization.
        for shop_key, dish_name, tag in (
            ("pho", "招牌牛肉河粉", "老闆推薦"),
            ("pho", "順化牛肉米線", "老闆推薦"),
            ("pho", "西貢豬骨粿條", "招牌"),
            ("banh-mi", "招牌越南法國麵包", "老闆推薦"),
            ("banh-mi", "烤豬肉麵包", "招牌"),
            ("banh-mi", "顆粒花生醬麵包", "老闆推薦"),
            ("drinks", "越南煉乳冰咖啡", "招牌"),
            ("drinks", "蛋咖啡", "老闆推薦"),
            ("drinks", "越南煎餅", "老闆推薦"),
        ):
            conn.execute(
                "UPDATE menu SET recommendation_tag=? WHERE shop=? AND name=? AND (recommendation_tag IS NULL OR TRIM(recommendation_tag)='')",
                (tag, shop_key, dish_name),
            )

def is_strong_password(password):
    """Require a basic password policy for newly registered customer accounts."""
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password) is not None
        and re.search(r"[a-z]", password) is not None
        and re.search(r"[^A-Za-z0-9]", password) is not None
    )


@app.route("/account/register", methods=["GET", "POST"])
def register_account():
    """A simple customer account: name, mobile phone and password."""
    error = ""
    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if len(display_name) < 1 or len(phone) < 8:
            error = "請填寫姓名與有效手機號碼。"
        elif password != confirm_password:
            error = "密碼與再次確認密碼不一致。"
        elif not is_strong_password(password):
            error = "密碼至少 8 碼，且須包含英文大寫、小寫與至少 1 個特殊符號。"
        else:
            try:
                with get_db() as conn:
                    cursor = conn.execute(
                        "INSERT INTO customer_accounts (display_name, phone, password_hash, created_at) VALUES (?,?,?,?)",
                        (display_name, phone, generate_password_hash(password), datetime.now().strftime("%Y/%m/%d %H:%M:%S")),
                    )
                session["customer"] = {"id": cursor.lastrowid, "name": display_name, "phone": phone, "points": 0}
                return redirect(url_for("welcome"))
            except sqlite3.IntegrityError:
                error = "此手機號碼已註冊，請直接登入。"
    return render_template("account.html", mode="register", error=error)


@app.route("/account/login", methods=["GET", "POST"])
def login_account():
    error = ""
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        with get_db() as conn:
            account = conn.execute("SELECT * FROM customer_accounts WHERE phone=?", (phone,)).fetchone()
        if account and check_password_hash(account["password_hash"], password):
            session["customer"] = {"id": account["id"], "name": account["display_name"], "phone": account["phone"], "points": int(account["points"] or 0)}
            return redirect(url_for("welcome"))
        error = "手機號碼或密碼不正確。"
    return render_template("account.html", mode="login", error=error)


@app.route("/account/logout", methods=["POST"])
def logout_account():
    session.pop("customer", None)
    return redirect(url_for("welcome"))


@app.route("/")
def welcome():
    customer = session.get("customer")
    if customer:
        with get_db() as conn:
            account = conn.execute("SELECT id,display_name,phone,points,welcome_points_claimed FROM customer_accounts WHERE id=?", (customer["id"],)).fetchone()
        if account:
            customer = {"id": account["id"], "name": account["display_name"], "phone": account["phone"], "points": int(account["points"] or 0), "welcome_points_claimed": bool(account["welcome_points_claimed"])}
            session["customer"] = customer
        else:
            session.pop("customer", None)
            customer = None
    return render_template("welcome.html", shops=SHOPS, customer=customer)


@app.post("/account/claim-welcome-points")
def claim_welcome_points():
    """Give every account, including members registered before this feature, one 10-point gift."""
    customer = session.get("customer")
    if not customer:
        return redirect(url_for("login_account"))
    with get_db() as conn:
        account = conn.execute("SELECT id,display_name,phone,points,welcome_points_claimed FROM customer_accounts WHERE id=?", (customer["id"],)).fetchone()
        if not account:
            session.pop("customer", None)
            return redirect(url_for("welcome"))
        if not account["welcome_points_claimed"]:
            conn.execute("UPDATE customer_accounts SET points=?, welcome_points_claimed=1 WHERE id=?", (int(account["points"] or 0) + 10, account["id"]))
            account = conn.execute("SELECT id,display_name,phone,points,welcome_points_claimed FROM customer_accounts WHERE id=?", (account["id"],)).fetchone()
        session["customer"] = {"id": account["id"], "name": account["display_name"], "phone": account["phone"], "points": int(account["points"] or 0), "welcome_points_claimed": bool(account["welcome_points_claimed"])}
    return redirect(url_for("welcome"))

@app.route("/shop/<shop_key>", methods=["GET", "POST"])
def order(shop_key):
    shop = SHOPS.get(shop_key)
    if not shop: abort(404)
    addons = SHOP_ADDONS[shop_key]
    with get_db() as conn:
        if request.method == "POST":
            customer, pay_method = request.form.get("customer_name", "").strip(), PAYMENT_METHODS[0]
            try: cart = json.loads(request.form.get("cart", "[]"))
            except json.JSONDecodeError: abort(400, "購物車資料格式錯誤。")
            if not customer or pay_method not in PAYMENT_METHODS or not isinstance(cart, list): abort(400, "請填寫取餐姓名、付款方式與餐點。")
            items=[]
            for entry in cart:
                food_id, qty, addon = entry.get("food_id"), entry.get("quantity"), entry.get("addon_name")
                if not isinstance(food_id,int) or not isinstance(qty,int) or not 1<=qty<=10 or addon not in addons: abort(400,"餐點資料無效。")
                food=conn.execute("SELECT * FROM menu WHERE id=? AND shop=?",(food_id,shop_key)).fetchone()
                if not food: abort(404,"找不到選取的餐點。")
                price=food["price"]+addons[addon]; items.append((food["id"],f"{food['name']} ({food['vi_name']})",addon,price,qty,price*qty))
            if not items: abort(400,"請至少加入一項餐點。")
            cursor=conn.execute("INSERT INTO orders (customer_name,item_name,addon_name,quantity,total_price,pay_method,status,created_at,shop_name) VALUES (?,?,?,?,?,?,?,?,?)",(customer,f"共 {len(items)} 項餐點","多項加料",sum(x[4] for x in items),sum(x[5] for x in items),pay_method,"已接單",datetime.now().strftime("%Y/%m/%d"),shop["name"]))
            conn.executemany("INSERT INTO order_items (order_id,menu_item_id,item_name,addon_name,unit_price,quantity,line_total) VALUES (?,?,?,?,?,?,?)",[(cursor.lastrowid,*x) for x in items])
            return redirect(url_for("success",order_id=cursor.lastrowid))
        rows=conn.execute("SELECT * FROM menu WHERE shop=? ORDER BY category,id",(shop_key,)).fetchall()
        menu=[]
        for index, row in enumerate(rows, start=1):
            item=dict(row)
            item["photo_file"]=f"menu-images/{shop_key}/{index:02d}.jpg"
            menu.append(item)
    return render_template("order.html", shop=shop, shop_key=shop_key, menu=menu, addons=addons, payment_methods=PAYMENT_METHODS, descriptions=PHO_DESCRIPTIONS, vi_descriptions=PHO_VI_DESCRIPTIONS)

@app.route("/order")
def old_order(): return redirect(url_for("welcome"))

@app.route("/success/<int:order_id>")
def success(order_id):
    with get_db() as conn:
        order_info=conn.execute("SELECT * FROM orders WHERE id=?",(order_id,)).fetchone(); items=conn.execute("SELECT * FROM order_items WHERE order_id=?",(order_id,)).fetchall()
        if order_info:
            shop_name = order_info["shop_name"] or "舊訂單"
            order_date = (order_info["created_at"] or "")[:10]
            shop_order_number = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE COALESCE(shop_name, '舊訂單')=? AND substr(created_at, 1, 10)=? AND id<=?",
                (shop_name, order_date, order_info["id"]),
            ).fetchone()[0]
    if not order_info: abort(404)
    return render_template("success.html",order=order_info,items=items,shop_order_number=shop_order_number)

@app.route("/admin/order/<int:order_id>/status",methods=["POST"])
def update_order_status(order_id):
    status=request.form.get("status")
    if status not in ORDER_STATUSES: abort(400)
    with get_db() as conn: conn.execute("UPDATE orders SET status=? WHERE id=?",(status,order_id))
    return redirect(url_for("admin_menu"))

@app.route("/admin")
def admin():
    with get_db() as conn:
        orders=conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall(); all_items=conn.execute("SELECT * FROM order_items ORDER BY order_id DESC,id").fetchall()
    groups={}
    for item in all_items: groups.setdefault(item["order_id"],[]).append(item)
    return render_template("admin.html",orders=orders,items_by_order=groups,statuses=ORDER_STATUSES)

PHO_TAKEAWAY_ADDONS = {
    "無加料／Không thêm": 0,
    "檸檬／Chanh": 0,
    "辣椒／Ớt": 0,
    "魚露醬／Nước mắm": 0,
    "加菜／Thêm rau": 15,
    "加主食／Thêm bánh phở hoặc bún": 15,
    "加肉／Thêm thịt": 30,
    "加炸春捲／Thêm nem rán": 30,
    "加蟹肉／Thêm thịt cua": 30,
    "加豬腳／Thêm giò heo": 30,
    "加魚餅／Thêm chả cá": 30,
    "加海鮮／Thêm hải sản": 30,
}
BANH_MI_TAKEAWAY_ADDONS = {
    "無加料／Không thêm": 0, "加肉／Thêm thịt": 30, "加魚肉／Thêm cá": 30,
    "加辣椒／Thêm ớt": 0, "加蛋／Thêm trứng": 10,
    "原狀（有冰）／Nguyên bản (có đá)": 0, "不加冰／Không đá": 0, "加大／Size lớn": 15,
}
BANH_MI_TAKEAWAY_ADDONS["加醃蘿蔔／Thêm đồ chua"] = 10
BANH_MI_TAKEAWAY_ADDONS["加顆粒花生醬／Thêm bơ đậu phộng hạt"] = 15
BANH_MI_TAKEAWAY_ADDONS["加海鮮／Thêm hải sản"] = 30
DRINKS_TAKEAWAY_ADDONS = {
    "無加料／Không thêm": 0,
    "原狀（有冰）／Nguyên bản (có đá)": 0,
    "不加冰／Không đá": 0,
    **SHOP_ADDONS["drinks"],
    "加大／Size lớn": 15,
}

PHO_SPECIAL_ADDONS = {
    "Bún nem Hà Nội": "加炸春捲／Thêm nem rán",
    "Bún riêu cua Bắc": "加蟹肉／Thêm thịt cua",
    "Bánh Canh giò heo": "加豬腳／Thêm giò heo",
    "Bánh Canh cua": "加蟹肉／Thêm thịt cua",
    "Bánh Canh cá lóc": "加魚餅／Thêm chả cá",
    "Bánh Canh hải sản": "加海鮮／Thêm hải sản",
    "Hủ Tiếu hải sản": "加海鮮／Thêm hải sản",
}
BANH_MI_SPECIAL_ADDONS = {
    "Bánh mì chả cá": "加魚肉／Thêm cá", "Bánh mì cá ngừ": "加魚肉／Thêm cá", "Bánh mì cá mòi": "加魚肉／Thêm cá",
}
BANH_MI_SPECIAL_ADDONS["Bánh mì bơ đậu phộng hạt"] = "加顆粒花生醬／Thêm bơ đậu phộng hạt"
BANH_MI_SPECIAL_ADDONS["Bánh mì hải sản"] = "加海鮮／Thêm hải sản"


def frontend_addons_for_item(item):
    """Return the same add-on options currently shown for one customer menu item."""
    raw_config = item.get("addon_config")
    try:
        is_explicitly_empty = NO_ADDONS_MARKER in json.loads(raw_config or "{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        is_explicitly_empty = False
    if is_explicitly_empty:
        return {}
    configured = parse_menu_addons(raw_config)
    if configured:
        return configured

    shop_key = item.get("shop", "")
    vi_name = item.get("vi_name", "")
    category = item.get("category", "")
    name = item.get("name", "")

    if shop_key == "drinks":
        if vi_name.startswith("Cà phê sữa"):
            return {"原狀（有冰）／Nguyên bản (có đá)": 0, "不加冰／Không đá": 0}
        if category in ("越南咖啡", "特色飲品") and name != "越南三色冰":
            options = {"原狀（有冰）／Nguyên bản (có đá)": 0, "不加冰／Không đá": 0}
            if category == "越南咖啡":
                options["加大／Size lớn"] = 15
            return options
        if category in ("越南點心", "越南甜點") or name == "越南三色冰":
            return {}
        return dict(DRINKS_TAKEAWAY_ADDONS)

    if shop_key == "banh-mi":
        if "飲品" in category:
            return {
                "原狀（有冰）／Nguyên bản (có đá)": 0,
                "不加冰／Không đá": 0,
                "加大／Size lớn": 15,
            }
        special = BANH_MI_SPECIAL_ADDONS.get(vi_name)
        if special == "加顆粒花生醬／Thêm bơ đậu phộng hạt":
            return {special: 15}
        options = {key: value for key, value in BANH_MI_TAKEAWAY_ADDONS.items() if "冰" not in key and "加大" not in key}
        if vi_name.startswith(("Bánh mì chay", "Bánh mì đậu hũ", "Bánh mì trứng")):
            options.pop("加肉／Thêm thịt", None)
        if special:
            options.pop("加肉／Thêm thịt", None)
            options[special] = 30
        return options

    options = dict(PHO_TAKEAWAY_ADDONS)
    special = PHO_SPECIAL_ADDONS.get(vi_name)
    if special:
        options.pop("加肉／Thêm thịt", None)
        options[special] = 30
    return options


def addon_options_text(options):
    return "\n".join(f"{name} | {price}" for name, price in options.items()) or "此餐點目前無加料／Món này hiện không có món thêm"

BANH_MI_DESCRIPTIONS = {
    "Bánh mì đặc biệt": "火腿、叉燒、肉鬆、醃蘿蔔、小黃瓜與香菜的豐盛招牌組合。",
    "Bánh mì thịt nướng": "炭烤豬肉帶焦香，搭配酸甜醃菜與新鮮香草。",
    "Bánh mì gà nướng": "香料烤雞肉、爽脆小黃瓜與自製醬料，清爽不膩。",
    "Bánh mì xá xíu": "蜜汁叉燒、醃蘿蔔、香菜與微甜醬汁，鹹甜平衡。",
    "Bánh mì bò": "嫩牛肉片配洋蔥、香菜與越南風味醬汁，肉香十足。",
    "Bánh mì jambon phô mai": "火腿與起司在烘烤麵包中融化，口感濃郁滑順。",
    "Bánh mì chà bông": "細緻肉鬆、奶油與小黃瓜，鹹香柔和、適合早餐。",
    "Bánh mì trứng": "現煎雞蛋、香菜、醃菜與胡椒，簡單卻有飽足感。",
    "Bánh mì chả cá": "越南魚餅煎香後搭配醃菜與辣椒，鮮香有彈性。",
    "Bánh mì gà chiên": "酥脆炸雞、清爽蔬菜與特調醬，外酥內嫩。",
    "Bánh mì thịt heo sả": "香茅豬肉香氣明顯，搭配醃菜與香草十分開胃。",
    "Bánh mì bò cay": "香辣牛肉、辣椒與香菜，適合喜歡重口味的人。",
    "Bánh mì chay": "豆腐、菇類、醃菜與香草製作的清爽素食選擇。",
    "Bánh mì đậu hũ": "煎豆腐吸附醬香，搭配小黃瓜、醃蘿蔔與香菜。",
    "Bánh mì hải sản": "鮮蝦與海鮮餡料配清脆蔬菜，帶有淡淡海味。",
    "Cà phê sữa đá": "濃郁越南滴漏咖啡加入煉乳與冰塊，香甜順口。",
    "Cà phê đen đá": "越南滴漏黑咖啡加冰，苦香濃厚、清爽提神。",
    "Trà chanh": "新鮮檸檬、茶香與冰塊調製，酸甜清新。",
    "Trà tắc": "金桔果香與清茶融合，帶自然酸香與回甘。",
    "Nước dừa": "清甜椰子水冰涼供應，最適合搭配越南麵包。",
}
BANH_MI_VI_DESCRIPTIONS = {name: "Nguyên liệu tươi, rau thơm Việt Nam và bánh mì nướng giòn thơm." for name in BANH_MI_DESCRIPTIONS}
BANH_MI_VI_DESCRIPTIONS.update({
    "Cà phê sữa đá": "Cà phê phin Việt Nam đậm đà, sữa đặc và đá mát lạnh.",
    "Cà phê đen đá": "Cà phê phin đen đậm vị, dùng cùng đá lạnh.",
    "Trà chanh": "Trà thơm pha chanh tươi và đá, chua ngọt thanh mát.",
    "Trà tắc": "Trà tắc thơm dịu, vị chua ngọt tự nhiên.",
    "Nước dừa": "Nước dừa mát lạnh, ngọt thanh tự nhiên.",
})
BANH_MI_INGREDIENTS = {
    "Bánh mì đặc biệt": "火腿、叉燒、肉鬆、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì thịt nướng": "烤豬肉、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì gà nướng": "烤雞肉、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì xá xíu": "叉燒、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì bò": "牛肉、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì jambon phô mai": "火腿、起司、生菜、小黃瓜、醃蘿蔔",
    "Bánh mì chà bông": "肉鬆、生菜、小黃瓜、醃蘿蔔、奶油",
    "Bánh mì trứng": "煎蛋、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì chả cá": "魚餅、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì gà chiên": "炸雞、生菜、小黃瓜、醃蘿蔔、特調醬",
    "Bánh mì thịt heo sả": "香茅豬肉、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì bò cay": "辣味牛肉、生菜、小黃瓜、醃蘿蔔、辣椒",
    "Bánh mì chay": "豆腐、菇類、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì đậu hũ": "煎豆腐、生菜、小黃瓜、醃蘿蔔、香菜",
    "Bánh mì hải sản": "鮮蝦、海鮮餡料、生菜、小黃瓜、醃蘿蔔",
    "Cà phê sữa đá": "越南滴漏咖啡、煉乳、冰塊",
    "Cà phê đen đá": "越南滴漏咖啡、冰塊",
    "Trà chanh": "紅茶、檸檬、糖、冰塊",
    "Trà tắc": "紅茶、金桔、糖、冰塊",
    "Nước dừa": "椰子水、冰塊",
}
BANH_MI_DESCRIPTIONS.update({
    "Bánh mì pate": "豬肝醬、奶油、醃蘿蔔、小黃瓜、香菜與胡椒，麵包烘烤後外酥內軟。",
    "Bánh mì pate Hà Nội": "豬肝醬、奶油、醃蘿蔔、小黃瓜、香菜與胡椒，麵包烘烤後外酥內軟。",
    "Bánh mì jambon": "火腿、奶油、醃蘿蔔、小黃瓜、香菜與越南風味醬料。",
    "Bánh mì chà bông": "肉鬆、奶油、小黃瓜、醃蘿蔔與香菜，鹹香柔和。",
    "Bánh mì thịt heo": "豬肉片、醃蘿蔔、小黃瓜、香菜、辣椒與特製醬料。",
    "Bánh mì bò": "牛肉片、洋蔥、小黃瓜、醃菜、香菜與黑胡椒醬。",
    "Bánh mì gà xé": "手撕雞肉、洋蔥絲、小黃瓜、醃蘿蔔與香菜。",
    "Bánh mì trứng": "現煎雞蛋、奶油、小黃瓜、醃蘿蔔、香菜與胡椒。",
    "Bánh mì đặc biệt Hà Nội": "火腿、叉燒、肉鬆、豬肝醬、醃菜、小黃瓜與香菜。",
    "Bánh mì chay": "豆腐、菇類、醃蘿蔔、小黃瓜、香菜與素食醬料。",
    "Bánh mì thịt nướng": "炭烤豬肉、醃蘿蔔、小黃瓜、香菜、辣椒與甜鹹醬汁。",
    "Bánh mì xá xíu": "蜜汁叉燒、醃菜、小黃瓜、香菜與微甜醬料。",
    "Bánh mì bò nướng": "炭烤牛肉、洋蔥、小黃瓜、醃菜、香菜與黑胡椒。",
    "Bánh mì gà chiên": "酥炸雞肉、生菜、小黃瓜、醃蘿蔔與特調醬。",
    "Bánh mì cá ngừ": "鮪魚、美乃滋、小黃瓜、洋蔥、醃菜與香菜。",
    "Bánh mì cá muối": "鹹魚、奶油、小黃瓜、醃蘿蔔、香菜與辣椒。",
    "Bánh mì phô mai": "起司、奶油、小黃瓜、醃蘿蔔與香菜，烘烤後濃郁牽絲。",
    "Bánh mì đặc biệt Sài Gòn": "火腿、叉燒、肉鬆、豬肝醬、醃菜、小黃瓜與香菜。",
    "Bánh mì gà cay": "香辣雞肉、辣椒、小黃瓜、醃蘿蔔、香菜與辣醬。",
    "Bánh mì chay Sài Gòn": "煎豆腐、菇類、醃菜、小黃瓜、香菜與素食醬料。",
})
BANH_MI_VI_DESCRIPTIONS.update({name: "Bánh mì nướng giòn với nguyên liệu tươi, rau thơm, dưa chua và nước sốt đặc trưng." for name in BANH_MI_DESCRIPTIONS})

BANH_MI_INGREDIENTS["Bánh mì bơ đậu phộng"] = "花生醬、生菜、小黃瓜、醃蘿蔔"
BANH_MI_INGREDIENTS["Bánh mì bơ đậu phộng hạt"] = "顆粒花生醬"
BANH_MI_INGREDIENTS_VI = {
    "Bánh mì đặc biệt": "Giăm bông, xá xíu, chà bông, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì thịt nướng": "Thịt heo nướng, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì gà nướng": "Gà nướng, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì xá xíu": "Xá xíu, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì bò": "Thịt bò, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì jambon phô mai": "Giăm bông, phô mai, rau xà lách, dưa leo, đồ chua.",
    "Bánh mì chà bông": "Chà bông, rau xà lách, dưa leo, đồ chua, bơ.",
    "Bánh mì trứng": "Trứng chiên, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì chả cá": "Chả cá, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì gà chiên": "Gà chiên, rau xà lách, dưa leo, đồ chua, sốt đặc biệt.",
    "Bánh mì thịt heo sả": "Thịt heo sả, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì bò cay": "Thịt bò cay, rau xà lách, dưa leo, đồ chua, ớt.",
    "Bánh mì chay": "Đậu hũ, nấm, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì đậu hũ": "Đậu hũ chiên, rau xà lách, dưa leo, đồ chua, rau mùi.",
    "Bánh mì hải sản": "Tôm, nhân hải sản, rau xà lách, dưa leo, đồ chua.",
    "Cà phê sữa đá": "Cà phê phin, sữa đặc, đá.", "Cà phê đen đá": "Cà phê phin, đá.",
    "Trà chanh": "Trà, chanh, đường, đá.", "Trà tắc": "Trà, tắc, đường, đá.", "Nước dừa": "Nước dừa, đá.",
}

BANH_MI_INGREDIENTS_VI["Bánh mì bơ đậu phộng"] = "Bơ đậu phộng, rau xà lách, dưa leo, đồ chua."
BANH_MI_INGREDIENTS_VI["Bánh mì bơ đậu phộng"] = "Bơ đậu phộng (bơ lạc), rau xà lách, dưa leo, đồ chua."
BANH_MI_INGREDIENTS_VI["Bánh mì bơ đậu phộng hạt"] = "Bơ đậu phộng hạt (bơ lạc hạt)."
BANH_MI_INGREDIENTS_VI["Bánh mì thịt nướng"] = "Thịt heo nướng (thịt lợn nướng), rau xà lách, dưa leo, đồ chua, rau mùi."
BANH_MI_INGREDIENTS_VI["Bánh mì thịt heo sả"] = "Thịt heo sả (thịt lợn sả), rau xà lách, dưa leo, đồ chua, rau mùi."

def enhanced_order(shop_key):
    shop = SHOPS.get(shop_key)
    if not shop:
        abort(404)
    addons = PHO_TAKEAWAY_ADDONS if shop_key == "pho" else BANH_MI_TAKEAWAY_ADDONS if shop_key == "banh-mi" else DRINKS_TAKEAWAY_ADDONS
    with get_db() as conn:
        exchange_point_value = get_point_value(conn)
        cash_point_value = get_cash_point_value(conn)
        customer_data = session.get("customer")
        account = None
        if customer_data:
            account = conn.execute("SELECT id,display_name,phone,points FROM customer_accounts WHERE id=?", (customer_data["id"],)).fetchone()
            if account:
                customer_data = {"id": account["id"], "name": account["display_name"], "phone": account["phone"], "points": int(account["points"] or 0)}
                session["customer"] = customer_data
            else:
                session.pop("customer", None)
                customer_data = None
        if request.method == "POST":
            customer = request.form.get("customer_name", "").strip()
            phone = request.form.get("phone", "").strip()
            if account:
                customer, phone = account["display_name"], account["phone"]
            pay_method = PAYMENT_METHODS[0]
            try:
                cart = json.loads(request.form.get("cart", "[]"))
            except json.JSONDecodeError:
                abort(400, "訂單資料格式錯誤")
            if not customer or not phone or pay_method not in PAYMENT_METHODS or not isinstance(cart, list):
                abort(400, "請完整填寫訂單資料")
            order_time = datetime.now()
            items = []
            exchange_count = 0
            exchange_points = 0
            exchange_value = 0
            original_subtotal = 0
            for entry in cart:
                food_id = entry.get("food_id")
                quantity = entry.get("quantity")
                selected = entry.get("addon_names", [])
                if not isinstance(food_id, int) or not isinstance(quantity, int) or not 1 <= quantity <= 10:
                    abort(400, "餐點資料錯誤")
                note = entry.get("note", "")
                exchange_with_points = entry.get("exchange_with_points", False)
                if not isinstance(note, str) or len(note) > 100:
                    abort(400, "備註資料錯誤")
                if not isinstance(exchange_with_points, bool):
                    abort(400, "點數兌換資料錯誤")
                if exchange_with_points and not account:
                    abort(403, "請先登入會員才能使用點數兌換商品")
                note = note.strip()
                food = conn.execute("SELECT * FROM menu WHERE id=? AND shop=? AND availability_status='供應中'", (food_id, shop_key)).fetchone()
                if not food:
                    abort(404, "找不到餐點")
                item_addons = parse_menu_addons(food["addon_config"]) or frontend_addons_for_item(dict(food))
                hidden_addons = parse_hidden_addons(food["hidden_addons"])
                item_addons = {name: price for name, price in item_addons.items() if name not in hidden_addons}
                # The customer page uses this zero-price sentinel whenever a
                # dish has no chosen add-on (including desserts or a dish
                # whose administrator-defined list has no explicit “none”).
                # It is not a paid add-on, so it must always be accepted.
                item_addons.setdefault("無加料／Không thêm", 0)
                if isinstance(selected, list) and len(selected) > 1:
                    selected = [name for name in selected if name != "無加料／Không thêm"]
                if not selected:
                    selected = ["無加料／Không thêm"]
                if not isinstance(selected, list) or not selected or any(name not in item_addons for name in selected):
                    abort(400, "加料選項錯誤")
                addon_total = sum(item_addons[name] for name in selected)
                item_original_price = promotional_price(food["price"] + addon_total, order_time)
                # A free-item exchange uses points worth NT$5 each.  The point
                # count is always rounded up, e.g. NT$150 requires 30 points.
                exchange_item_value = promotional_price(food["price"], order_time) if exchange_with_points else 0
                unit_price = item_original_price - exchange_item_value
                addon_text = "、".join(selected)
                if exchange_with_points:
                    dish_exchange_points = max(1, (exchange_item_value + exchange_point_value - 1) // exchange_point_value)
                    addon_text += f"；點數兌換餐點／Đổi món bằng điểm（{dish_exchange_points}點／NT${exchange_item_value}）"
                    exchange_count += quantity
                    exchange_points += dish_exchange_points * quantity
                    exchange_value += exchange_item_value * quantity
                if note:
                    addon_text += f"；備註：{note}"
                items.append((food["id"], f"{food['name']} ({food['vi_name']})", addon_text, unit_price, quantity, unit_price * quantity))
                original_subtotal += item_original_price * quantity
            if not items:
                abort(400, "請至少加入一項餐點")
            subtotal = sum(item[5] for item in items)
            try:
                points_redeemed = int(request.form.get("points_to_redeem", "0"))
            except ValueError:
                abort(400, "點數格式錯誤")
            available_points = int(account["points"] or 0) if account else 0
            if exchange_points > available_points:
                abort(400, "可用點數不足，無法兌換商品")
            if points_redeemed < 0 or points_redeemed > available_points:
                abort(400, "使用點數超過目前可用點數")
            # Monetary redemption has a fixed value of NT$5 per point.  Round
            # the required points up so any remaining amount is also covered.
            money_points_needed = (subtotal + cash_point_value - 1) // cash_point_value if subtotal else 0
            points_redeemed = min(points_redeemed, money_points_needed, available_points - exchange_points)
            points_redemption_value = min(subtotal, points_redeemed * cash_point_value)
            total_price = subtotal - points_redemption_value
            points_earned = reward_points_for_amount(total_price) if account else 0
            cursor = conn.execute(
                "INSERT INTO orders (customer_name,phone,item_name,addon_name,quantity,total_price,pay_method,payment_status,status,created_at,shop_name,points_earned,points_redeemed,points_exchange_count,points_exchange_points,points_redemption_value,points_exchange_value,subtotal_price) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (customer, phone, f"共 {len(items)} 項餐點", "多項加料", sum(item[4] for item in items), total_price, pay_method, "待付款", ORDER_STATUSES[0], order_time.strftime("%Y/%m/%d %H:%M:%S"), shop["name"], points_earned, points_redeemed + exchange_points, exchange_count, exchange_points, points_redemption_value, exchange_value, original_subtotal),
            )
            conn.executemany(
                "INSERT INTO order_items (order_id,menu_item_id,item_name,addon_name,unit_price,quantity,line_total) VALUES (?,?,?,?,?,?,?)",
                [(cursor.lastrowid, *item) for item in items],
            )
            if account:
                new_points = available_points - points_redeemed - exchange_points + points_earned
                conn.execute("UPDATE customer_accounts SET points=? WHERE id=?", (new_points, account["id"]))
                session["customer"] = {"id": account["id"], "name": account["display_name"], "phone": account["phone"], "points": new_points}
            return redirect(url_for("success", order_id=cursor.lastrowid))
        # 前端保留顯示暫停供應的菜色，讓顧客能清楚看到供應狀態；
        # 送單時仍會由伺服器拒絕暫停供應的餐點。
        rows = conn.execute("SELECT * FROM menu WHERE shop=? ORDER BY category,id", (shop_key,)).fetchall()
        menu = []
        for row in rows:
            item = dict(row)
            # A menu image must belong to this exact database record.  The old
            # number-based fallback could shift after a dish was added/deleted,
            # which showed the photo of a different dish.
            item["photo_file"] = "images/menu-placeholder.svg"
            item["configured_addons"] = parse_menu_addons(item.get("addon_config"))
            item["hidden_addons"] = parse_hidden_addons(item.get("hidden_addons"))
            menu.append(item)
        menu_version = f"{len(menu)}:{max((item.get('updated_at') or '' for item in menu), default='')}"
    descriptions = {**PHO_DESCRIPTIONS, **BANH_MI_DESCRIPTIONS, **DRINKS_DESCRIPTIONS}
    vi_descriptions = {**PHO_VI_DESCRIPTIONS, **BANH_MI_VI_DESCRIPTIONS, **DRINKS_VI_DESCRIPTIONS}
    special_addons = {**PHO_SPECIAL_ADDONS, **BANH_MI_SPECIAL_ADDONS}
    return render_template("order.html", shop=shop, shop_key=shop_key, menu=menu, menu_version=menu_version, addons=addons, special_addons=special_addons, ingredients=BANH_MI_INGREDIENTS, vi_ingredients=BANH_MI_INGREDIENTS_VI, payment_methods=PAYMENT_METHODS, descriptions=descriptions, vi_descriptions=vi_descriptions, region_vi_labels=REGION_VI_LABELS, recommendation_vi_labels=RECOMMENDATION_VI_LABELS, availability_vi_labels=AVAILABILITY_VI_LABELS, shop_address=SHOP_ADDRESSES[shop_key], promotion_active=promotion_is_active(), promotion_date=PROMOTION_DATE, promotion_rate=90, exchange_point_value=exchange_point_value, cash_point_value=cash_point_value, customer=customer_data, available_points=int(account["points"] or 0) if account else 0)


@app.get("/shop/<shop_key>/menu-version")
def shop_menu_version(shop_key):
    """Small no-cache endpoint for near-real-time customer menu updates."""
    if shop_key not in SHOPS:
        abort(404)
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS menu_count, COALESCE(MAX(updated_at), '') AS latest_update FROM menu WHERE shop=?",
            (shop_key,),
        ).fetchone()
    response = jsonify({"version": f"{row['menu_count']}:{row['latest_update']}"})
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

def redirect_to_menu_position(return_to):
    """Keep the editor on the same shop page and edited menu item."""
    matched = re.fullmatch(r"(pho|banh-mi|drinks)(#(?:shop-(?:pho|banh-mi|drinks)|menu-item-\d+))?", return_to or "")
    if matched:
        return redirect(f"{url_for('admin_menu_shop', shop_key=matched.group(1))}{matched.group(2) or ''}")
    return redirect(url_for("admin_menu"))


def remove_uploaded_menu_image(image_url, menu_id, remove_stale_variants=False):
    """Delete only the private upload belonging to one menu item.

    Built-in menu photos, placeholders and any path outside static/menu-images/uploads
    are intentionally never removed.
    """
    prefix = "/static/menu-images/uploads/"
    if not image_url or not image_url.startswith(prefix):
        return
    filename = image_url.removeprefix(prefix)
    upload_dir = (Path(app.static_folder) / "menu-images" / "uploads").resolve()
    image_path = (upload_dir / filename).resolve()
    try:
        image_path.relative_to(upload_dir)
    except ValueError:
        return
    if image_path.is_file():
        image_path.unlink()
    if remove_stale_variants:
        # A replacement can use a different extension.  When the dish itself
        # is deleted, clear any stale filename generated for this same id.
        for extension in ("jpg", "jpeg", "png", "webp"):
            stale_path = (upload_dir / f"menu_{menu_id}.{extension}").resolve()
            if stale_path.is_file():
                stale_path.unlink()


@app.route("/admin/menu/new/<shop_key>", methods=["POST"])
def create_menu_item(shop_key):
    """Create one editable placeholder dish for the selected shop."""
    if shop_key not in SHOPS:
        abort(404)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO menu (name, vi_name, price, category, shop, description, vi_description, image_url, region, recommendation_tag, exchange_points, availability_status, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("新餐點", "Món mới", 0, MENU_CATEGORY_OPTIONS[shop_key][0][0], shop_key, "", "", "/static/images/menu-placeholder.svg", "全越南常見", "", 2, "供應中", datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")),
        )
    return redirect_to_menu_position(request.form.get("return_to", ""))

@app.route("/admin/menu/<int:menu_id>", methods=["POST"])
def edit_menu_item(menu_id):
    name = request.form.get("name", "").strip()
    vi_name = request.form.get("vi_name", "").strip()
    description = request.form.get("description", "").strip()
    vi_description = request.form.get("vi_description", "").strip()
    category = request.form.get("category", "").strip()
    region = request.form.get("region", "全越南常見").strip()
    recommendation_tag = request.form.get("recommendation_tag", "").strip()
    availability_status = request.form.get("availability_status", "供應中").strip()
    addon_editor_present = request.form.get("addon_editor_present") == "1"
    addon_row_editor_present = request.form.get("addon_row_editor_present") == "1"
    if addon_row_editor_present:
        addon_config = parse_menu_addon_rows(request.form.getlist("addon_name"), request.form.getlist("addon_price"))
        if not addon_config:
            addon_config = {NO_ADDONS_MARKER: 0}
        try:
            addon_visibility = json.loads(request.form.get("addon_visibility_json", "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            abort(400, "加料顯示設定錯誤")
        if not isinstance(addon_visibility, dict):
            abort(400, "加料顯示設定錯誤")
    else:
        addon_config = parse_menu_addon_text(request.form.get("addon_config", "")) if addon_editor_present else None
        addon_visibility = {}
    try:
        price = int(request.form.get("price", ""))
        # Kept for database compatibility; required exchange points now come
        # from the menu price and the fixed NT$5-per-point rule.
        exchange_points = 2
    except ValueError:
        abort(400, "價格格式錯誤")
    if not name or not vi_name or price < 0 or exchange_points < 1 or region not in REGION_OPTIONS or recommendation_tag not in RECOMMENDATION_OPTIONS or availability_status not in AVAILABILITY_OPTIONS:
        abort(400, "請完整填寫菜單資料")
    image_url = None
    image = request.files.get("image")
    if image and image.filename:
        extension = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else ""
        if extension not in {"jpg", "jpeg", "png", "webp"}:
            abort(400, "圖片只接受 JPG、PNG 或 WEBP")
        from pathlib import Path
        upload_dir = Path(app.static_folder) / "menu-images" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"menu_{menu_id}.{extension}"
        image.save(upload_dir / filename)
        image_url = f"/static/menu-images/uploads/{filename}"
    with get_db() as conn:
        item = conn.execute("SELECT * FROM menu WHERE id=?", (menu_id,)).fetchone()
        if not item:
            abort(404)
        allowed_categories = {value for value, _label in MENU_CATEGORY_OPTIONS.get(item["shop"], ())}
        if category not in allowed_categories:
            abort(400, "請選擇正確的餐點分類")
        if addon_config is None:
            addon_config = parse_menu_addons(item["addon_config"])
        option_source = dict(item)
        option_source.update({"name": name, "vi_name": vi_name, "category": category, "addon_config": json.dumps(addon_config, ensure_ascii=False)})
        valid_addons = frontend_addons_for_item(option_source)
        if addon_editor_present:
            hidden_addons = {name for name in valid_addons if addon_visibility.get(name) is False}
        else:
            hidden_addons = parse_hidden_addons(item["hidden_addons"])
        old_image_url = item["image_url"]
        conn.execute(
            "UPDATE menu SET name=?, vi_name=?, price=?, category=?, description=?, vi_description=?, image_url=?, region=?, recommendation_tag=?, exchange_points=?, availability_status=?, addon_config=?, hidden_addons=?, updated_at=? WHERE id=?",
            (name, vi_name, price, category, description, vi_description, image_url or item["image_url"], region, recommendation_tag, exchange_points, availability_status, json.dumps(addon_config, ensure_ascii=False), json.dumps(sorted(hidden_addons), ensure_ascii=False), datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"), menu_id),
        )
        if image_url and image_url != old_image_url:
            shared_image = conn.execute("SELECT 1 FROM menu WHERE id<>? AND image_url=? LIMIT 1", (menu_id, old_image_url)).fetchone()
            if not shared_image:
                remove_uploaded_menu_image(old_image_url, menu_id)
    return redirect_to_menu_position(request.form.get("return_to", ""))

@app.route("/admin/menu/<int:menu_id>/delete", methods=["POST"])
def delete_menu_item(menu_id):
    """Remove a dish from the editable menu while retaining past order details."""
    with get_db() as conn:
        item = conn.execute("SELECT id,shop,vi_name,image_url FROM menu WHERE id=?", (menu_id,)).fetchone()
        if not item:
            abort(404)
        shared_image = conn.execute("SELECT 1 FROM menu WHERE id<>? AND image_url=? LIMIT 1", (menu_id, item["image_url"])).fetchone()
        conn.execute(
            "INSERT OR REPLACE INTO retired_menu_items (shop,vi_name,retired_at) VALUES (?,?,?)",
            (item["shop"], item["vi_name"], datetime.now().strftime("%Y/%m/%d %H:%M:%S")),
        )
        conn.execute("DELETE FROM menu WHERE id=?", (menu_id,))
        if not shared_image:
            remove_uploaded_menu_image(item["image_url"], menu_id, remove_stale_variants=True)
    return redirect_to_menu_position(request.form.get("return_to", ""))

@app.route("/my-orders")
def my_orders():
    phone = request.args.get("phone", "").strip() or session.get("customer", {}).get("phone", "")
    orders = []
    items_by_order = {}
    if phone:
        with get_db() as conn:
            today = datetime.now().strftime("%Y/%m/%d")
            orders = add_shop_order_numbers(conn, conn.execute("SELECT * FROM orders WHERE phone=? AND substr(created_at, 1, 10)=? ORDER BY id DESC", (phone, today)).fetchall())
            for order in orders:
                items_by_order[order["id"]] = conn.execute("SELECT * FROM order_items WHERE order_id=? ORDER BY id", (order["id"],)).fetchall()
    order_groups, order_total_count, order_total_amount = build_customer_order_groups(orders)
    return render_template("my_orders.html", phone=phone, orders=orders, order_groups=order_groups, order_total_count=order_total_count, order_total_amount=order_total_amount, items_by_order=items_by_order, searched=bool(phone), is_history=False)


@app.route("/my-orders/latest")
def my_orders_latest():
    """Return only live status fields for a customer's orders placed today."""
    phone = request.args.get("phone", "").strip() or session.get("customer", {}).get("phone", "")
    if not phone:
        return jsonify({"orders": [], "checked_at": datetime.now().strftime("%H:%M:%S")})
    today = datetime.now().strftime("%Y/%m/%d")
    with get_db() as conn:
        orders = conn.execute(
            "SELECT id, status, payment_status FROM orders WHERE phone=? AND substr(created_at, 1, 10)=?",
            (phone, today),
        ).fetchall()
    return jsonify({
        "orders": [dict(order) for order in orders],
        "checked_at": datetime.now().strftime("%H:%M:%S"),
    })


@app.route("/my-orders/history")
def my_orders_history():
    phone = request.args.get("phone", "").strip() or session.get("customer", {}).get("phone", "")
    selected_date = request.args.get("date", "").strip()
    orders = []
    items_by_order = {}
    if phone:
        with get_db() as conn:
            today = datetime.now().strftime("%Y/%m/%d")
            query = "SELECT * FROM orders WHERE phone=? AND substr(created_at, 1, 10)<>?"
            params = [phone, today]
            if selected_date:
                query += " AND substr(created_at, 1, 10)=?"
                params.append(selected_date.replace("-", "/"))
            orders = add_shop_order_numbers(conn, conn.execute(query + " ORDER BY id DESC", params).fetchall())
            for order in orders:
                items_by_order[order["id"]] = conn.execute("SELECT * FROM order_items WHERE order_id=? ORDER BY id", (order["id"],)).fetchall()
    order_groups, order_total_count, order_total_amount = build_customer_order_groups(orders)
    return render_template("my_orders.html", phone=phone, orders=orders, order_groups=order_groups, order_total_count=order_total_count, order_total_amount=order_total_amount, items_by_order=items_by_order, searched=bool(phone), is_history=True, selected_date=selected_date)


def build_customer_order_groups(orders):
    """Keep a member's takeout orders clearly separated by the three stores."""
    groups = [{"shop_key": key, "shop_name": shop["name"], "orders": [], "count": 0, "amount": 0} for key, shop in SHOPS.items()]
    groups_by_name = {group["shop_name"]: group for group in groups}
    for order in orders:
        group = groups_by_name.get(order["shop_name"])
        if group is None:
            continue
        group["orders"].append(order)
        group["count"] += 1
        group["amount"] += int(order["total_price"] or 0)
    return groups, len(orders), sum(int(order["total_price"] or 0) for order in orders)

def enhanced_admin():
    return render_template("admin_dashboard.html", shops=SHOPS)


@app.route("/admin/manual-order", methods=["GET", "POST"])
def admin_manual_order():
    """Staff ordering screen for walk-in customers without a phone."""
    shop_key = request.values.get("shop_key", "pho")
    if shop_key not in SHOPS:
        abort(404)
    addons = PHO_TAKEAWAY_ADDONS if shop_key == "pho" else BANH_MI_TAKEAWAY_ADDONS if shop_key == "banh-mi" else DRINKS_TAKEAWAY_ADDONS

    with get_db() as conn:
        if request.method == "POST":
            customer = request.form.get("customer_name", "").strip() or "現場顧客"
            member_phone = request.form.get("member_phone", "").strip()
            pay_method = PAYMENT_METHODS[0]
            payment_status = request.form.get("payment_status")
            status = request.form.get("status")
            try:
                cart = json.loads(request.form.get("cart", "[]"))
            except json.JSONDecodeError:
                abort(400, "人工點餐資料格式錯誤")
            if pay_method not in PAYMENT_METHODS or payment_status not in {"待付款", "已付款"} or status not in ORDER_STATUSES or not isinstance(cart, list):
                abort(400, "請完整填寫人工訂單資料")

            member_account = None
            if member_phone:
                member_account = conn.execute(
                    "SELECT id,display_name,phone,points FROM customer_accounts WHERE phone=?", (member_phone,)
                ).fetchone()
                if member_account:
                    customer = member_account["display_name"]

            order_time = datetime.now()
            items = []
            for entry in cart:
                food_id = entry.get("food_id")
                quantity = entry.get("quantity")
                selected = entry.get("addon_names", [])
                note = entry.get("note", "")
                if not isinstance(food_id, int) or not isinstance(quantity, int) or not 1 <= quantity <= 20:
                    abort(400, "餐點或數量錯誤")
                if not isinstance(selected, list) or any(name not in addons for name in selected):
                    abort(400, "加料選項錯誤")
                if not isinstance(note, str) or len(note) > 100:
                    abort(400, "備註資料錯誤")
                food = conn.execute("SELECT * FROM menu WHERE id=? AND shop=? AND availability_status='供應中'", (food_id, shop_key)).fetchone()
                if not food:
                    abort(404, "找不到餐點")
                addon_text = "、".join(selected) if selected else "無加料／Không thêm"
                if note.strip():
                    addon_text += f"；備註：{note.strip()}"
                unit_price = promotional_price(int(food["price"]) + sum(addons[name] for name in selected), order_time)
                items.append((food["id"], f"{food['name']} ({food['vi_name']})", addon_text, unit_price, quantity, unit_price * quantity))
            if not items:
                abort(400, "請至少加入一項餐點")
            total_price = sum(item[5] for item in items)
            points_earned = reward_points_for_amount(total_price) if member_account else 0
            cursor = conn.execute(
                "INSERT INTO orders (customer_name,phone,item_name,addon_name,quantity,total_price,pay_method,payment_status,status,created_at,shop_name,points_earned,points_redeemed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (customer, member_account["phone"] if member_account else member_phone, f"共 {len(items)} 項餐點（人工點餐）", "多項加料", sum(item[4] for item in items), total_price, pay_method, payment_status, status, order_time.strftime("%Y/%m/%d %H:%M:%S"), SHOPS[shop_key]["name"], points_earned, 0),
            )
            conn.executemany(
                "INSERT INTO order_items (order_id,menu_item_id,item_name,addon_name,unit_price,quantity,line_total) VALUES (?,?,?,?,?,?,?)",
                [(cursor.lastrowid, *item) for item in items],
            )
            if member_account:
                conn.execute(
                    "UPDATE customer_accounts SET points=? WHERE id=?",
                    (int(member_account["points"] or 0) + points_earned, member_account["id"]),
                )
            return redirect(url_for("admin_orders"))

        menu = [dict(row) for row in conn.execute("SELECT * FROM menu WHERE shop=? AND availability_status='供應中' ORDER BY category,id", (shop_key,)).fetchall()]
    return render_template(
        "admin_manual_order.html",
        shops=SHOPS,
        shop_key=shop_key,
        menu=menu,
        addons=addons,
        payment_methods=PAYMENT_METHODS,
        statuses=ORDER_STATUSES,
        promotion_active=promotion_is_active(),
    )

@app.route("/admin/menu")
def admin_menu():
    return render_template("admin_menu_home.html", shops=SHOPS)


@app.route("/admin/points-settings", methods=["GET", "POST"])
def admin_points_settings():
    """Configure the point-to-NTD rate used for future redemptions."""
    with get_db() as conn:
        if request.method == "POST":
            try:
                exchange_point_value = int(request.form.get("exchange_point_value", ""))
                cash_point_value = int(request.form.get("cash_point_value", ""))
            except ValueError:
                abort(400, "點數折抵金額必須是整數。")
            if not 1 <= exchange_point_value <= 1000 or not 1 <= cash_point_value <= 1000:
                abort(400, "1 點折抵金額請設定在 NT$1 至 NT$1,000。")
            conn.execute(
                "INSERT INTO app_settings (setting_key, setting_value) VALUES ('point_value_ntd', ?) "
                "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value",
                (str(exchange_point_value),),
            )
            conn.execute(
                "INSERT INTO app_settings (setting_key, setting_value) VALUES ('cash_point_value_ntd', ?) "
                "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value",
                (str(cash_point_value),),
            )
            return redirect(url_for("admin_points_settings", saved="1"))
        exchange_point_value = get_point_value(conn)
        cash_point_value = get_cash_point_value(conn)
    return render_template("admin_points_settings.html", exchange_point_value=exchange_point_value, cash_point_value=cash_point_value, saved=request.args.get("saved") == "1")


@app.route("/admin/menu/<shop_key>")
def admin_menu_shop(shop_key):
    """A separate editable menu page for each of the three stores."""
    if shop_key not in SHOPS:
        abort(404)
    with get_db() as conn:
        point_value = get_point_value(conn)
        # An empty image_url means this record has no verified photo yet.
        # Do not guess using the dish order: that can display another dish's
        # image after menu records are added or removed.
        rows = conn.execute("SELECT * FROM menu WHERE shop=? ORDER BY id", (shop_key,)).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["admin_photo_file"] = "images/menu-placeholder.svg"
            item["addon_config_text"] = menu_addon_text(item.get("addon_config"))
            item["frontend_addons"] = frontend_addons_for_item(item)
            item["frontend_addon_text"] = addon_options_text(item["frontend_addons"])
            item["hidden_addons"] = parse_hidden_addons(item.get("hidden_addons"))
            items.append(item)
    items.sort(key=lambda item: (0 if item["name"] == "新餐點" else 1, item["category"], item["id"]))
    groups = [(shop_key, SHOPS[shop_key]["name"], items)]
    return render_template("admin_menu.html", shops=groups, descriptions=PHO_DESCRIPTIONS, vi_descriptions=PHO_VI_DESCRIPTIONS, region_options=REGION_OPTIONS, recommendation_options=RECOMMENDATION_OPTIONS, availability_options=AVAILABILITY_OPTIONS, category_options=MENU_CATEGORY_OPTIONS, region_vi_labels=REGION_VI_LABELS, recommendation_vi_labels=RECOMMENDATION_VI_LABELS, availability_vi_labels=AVAILABILITY_VI_LABELS, point_value=point_value)


def add_shop_order_numbers(conn, orders):
    """Add a per-shop sequence number that restarts every calendar day."""
    numbered_orders = []
    for order in orders:
        item = dict(order)
        shop_name = item.get("shop_name") or "舊訂單"
        order_date = (item.get("created_at") or "")[:10]
        item["shop_order_number"] = conn.execute(
            "SELECT COUNT(*) FROM orders WHERE COALESCE(shop_name, '舊訂單')=? AND substr(created_at, 1, 10)=? AND id<=?",
            (shop_name, order_date, item["id"]),
        ).fetchone()[0]
        numbered_orders.append(item)
    return numbered_orders


@app.route("/admin/orders")
def admin_orders():
    shop_key = request.args.get("shop", "all").strip()
    if shop_key not in {"all", *SHOPS.keys()}:
        abort(404)
    with get_db() as conn:
        today = datetime.now().strftime("%Y/%m/%d")
        query = "SELECT * FROM orders WHERE substr(created_at, 1, 10)=?"
        params = [today]
        if shop_key != "all":
            query += " AND shop_name=?"
            params.append(SHOPS[shop_key]["name"])
        orders = add_shop_order_numbers(conn, conn.execute(query + " ORDER BY id DESC", params).fetchall())
        items_by_order = {order["id"]: conn.execute("SELECT * FROM order_items WHERE order_id=? ORDER BY id", (order["id"],)).fetchall() for order in orders}
    return render_template(
        "admin_orders.html", orders=orders, items_by_order=items_by_order,
        statuses=ORDER_STATUSES, is_history=False, selected_date="", shop_key=shop_key,
        shops=SHOPS, order_total_count=len(orders),
        order_total_amount=sum(int(order["total_price"] or 0) for order in orders),
    )


@app.route("/admin/orders/latest")
def admin_orders_latest():
    """Small polling endpoint used by the live takeout-order dashboard."""
    shop_key = request.args.get("shop", "all").strip()
    if shop_key not in {"all", *SHOPS.keys()}:
        abort(404)
    today = datetime.now().strftime("%Y/%m/%d")
    query = "SELECT COALESCE(MAX(id), 0) AS latest_id FROM orders WHERE substr(created_at, 1, 10)=?"
    params = [today]
    if shop_key != "all":
        query += " AND shop_name=?"
        params.append(SHOPS[shop_key]["name"])
    with get_db() as conn:
        latest_id = conn.execute(query, params).fetchone()["latest_id"]
    return jsonify({"latest_id": int(latest_id), "checked_at": datetime.now().strftime("%H:%M:%S")})

@app.route("/admin/orders/history")
def admin_orders_history():
    selected_date = request.args.get("date", "").strip()
    shop_key = request.args.get("shop", "all").strip()
    if shop_key not in {"all", *SHOPS.keys()}:
        abort(404)
    with get_db() as conn:
        today = datetime.now().strftime("%Y/%m/%d")
        query = "SELECT * FROM orders WHERE substr(created_at, 1, 10)<>?"
        params = [today]
        if selected_date:
            query += " AND substr(created_at, 1, 10)=?"
            params.append(selected_date.replace("-", "/"))
        if shop_key != "all":
            query += " AND shop_name=?"
            params.append(SHOPS[shop_key]["name"])
        orders = add_shop_order_numbers(conn, conn.execute(query + " ORDER BY id DESC", params).fetchall())
        items_by_order = {order["id"]: conn.execute("SELECT * FROM order_items WHERE order_id=? ORDER BY id", (order["id"],)).fetchall() for order in orders}
    return render_template(
        "admin_orders.html", orders=orders, items_by_order=items_by_order,
        statuses=ORDER_STATUSES, is_history=True, selected_date=selected_date, shop_key=shop_key,
        shops=SHOPS, order_total_count=len(orders),
        order_total_amount=sum(int(order["total_price"] or 0) for order in orders),
    )

@app.route("/admin/daily-sales")
@app.route("/admin/daily-sales/<shop_key>")
def admin_daily_sales(shop_key="all"):
    """Show the quantity and amount sold for every dish on a selected day."""
    if shop_key not in {"all", *SHOPS.keys()}:
        abort(404)
    selected_date = request.args.get("date", "").strip()
    query_date = selected_date.replace("-", "/") if selected_date else datetime.now().strftime("%Y/%m/%d")
    params = [query_date]
    shop_clause = ""
    if shop_key != "all":
        shop_clause = " AND o.shop_name=?"
        params.append(SHOPS[shop_key]["name"])
    with get_db() as conn:
        sales = conn.execute(
            """
            SELECT o.shop_name, oi.item_name,
                   SUM(oi.quantity) AS quantity_sold,
                   SUM(oi.line_total) AS sales_amount
            FROM order_items AS oi
            JOIN orders AS o ON o.id = oi.order_id
            WHERE substr(o.created_at, 1, 10) = ? """ + shop_clause + """
            GROUP BY o.shop_name, oi.item_name
            ORDER BY o.shop_name, quantity_sold DESC, oi.item_name
            """,
            params,
        ).fetchall()
    total_portions = sum(row["quantity_sold"] for row in sales)
    total_amount = sum(row["sales_amount"] for row in sales)
    return render_template(
        "daily_sales.html",
        sales=sales,
        selected_date=query_date.replace("/", "-"),
        total_portions=total_portions,
        total_amount=total_amount,
        is_admin=True,
        shop_key=shop_key,
        shop=SHOPS.get(shop_key),
        shops=SHOPS,
    )


@app.route("/admin/history-report")
@app.route("/admin/history-report/<shop_key>")
def admin_history_report(shop_key="all"):
    """Sales dashboard from the three shops' saved order history."""
    if shop_key not in {"all", *SHOPS.keys()}:
        abort(404)
    start_date = request.args.get("start", "").strip()
    end_date = request.args.get("end", "").strip()
    start_value = start_date.replace("-", "/")
    end_value = end_date.replace("-", "/")
    shop_names = {key: shop["name"] for key, shop in SHOPS.items()}
    params = []
    clauses = ["1=1"]
    if start_value:
        clauses.append("substr(created_at, 1, 10) >= ?")
        params.append(start_value)
    if end_value:
        clauses.append("substr(created_at, 1, 10) <= ?")
        params.append(end_value)
    if shop_key != "all":
        clauses.append("shop_name = ?")
        params.append(SHOPS[shop_key]["name"])
    with get_db() as conn:
        rows = conn.execute(
            "SELECT substr(created_at, 1, 10) AS order_date, shop_name, "
            "SUM(total_price) AS revenue, COUNT(*) AS order_count "
            "FROM orders WHERE " + " AND ".join(clauses) + " "
            "GROUP BY substr(created_at, 1, 10), shop_name ORDER BY order_date, shop_name",
            params,
        ).fetchall()

    daily = {}
    totals = {name: {"revenue": 0, "orders": 0} for name in shop_names.values()}
    for row in rows:
        date = row["order_date"]
        shop_name = row["shop_name"]
        if shop_name not in totals:
            totals[shop_name] = {"revenue": 0, "orders": 0}
        daily.setdefault(date, {name: 0 for name in totals})
        daily[date][shop_name] = int(row["revenue"] or 0)
        totals[shop_name]["revenue"] += int(row["revenue"] or 0)
        totals[shop_name]["orders"] += int(row["order_count"] or 0)

    labels = list(daily)
    series = [
        {"name": name, "values": [daily[date].get(name, 0) for date in labels]}
        for name in shop_names.values()
    ]
    total_revenue = sum(item["revenue"] for item in totals.values())
    total_orders = sum(item["orders"] for item in totals.values())
    return render_template(
        "history_report.html",
        start_date=start_date,
        end_date=end_date,
        labels=labels,
        series=series,
        totals=[{"name": name, **totals[name]} for name in shop_names.values() if shop_key == "all" or name == SHOPS[shop_key]["name"]],
        total_revenue=total_revenue,
        total_orders=total_orders,
        shop_key=shop_key,
        shop=SHOPS.get(shop_key),
        shops=SHOPS,
    )

@app.route("/daily-sales")
def public_daily_sales():
    """Public version of the daily dish sales report."""
    selected_date = request.args.get("date", "").strip()
    query_date = selected_date.replace("-", "/") if selected_date else datetime.now().strftime("%Y/%m/%d")
    with get_db() as conn:
        sales = conn.execute(
            """
            SELECT o.shop_name, oi.item_name,
                   SUM(oi.quantity) AS quantity_sold,
                   SUM(oi.line_total) AS sales_amount
            FROM order_items AS oi
            JOIN orders AS o ON o.id = oi.order_id
            WHERE substr(o.created_at, 1, 10) = ?
            GROUP BY o.shop_name, oi.item_name
            ORDER BY o.shop_name, quantity_sold DESC, oi.item_name
            """,
            (query_date,),
        ).fetchall()
    return render_template(
        "daily_sales.html",
        sales=sales,
        selected_date=query_date.replace("/", "-"),
        total_portions=sum(row["quantity_sold"] for row in sales),
        total_amount=sum(row["sales_amount"] for row in sales),
        is_admin=False,
        shop_key="all",
        shop=None,
        shops=SHOPS,
    )

def enhanced_update_order_status(order_id):
    status = request.form.get("status")
    payment_status = request.form.get("payment_status")
    if status not in ORDER_STATUSES:
        abort(400)
    if payment_status not in {"待付款", "已付款"}:
        abort(400)
    with get_db() as conn:
        conn.execute("UPDATE orders SET status=?, payment_status=? WHERE id=?", (status, payment_status, order_id))
    return redirect(url_for("admin_orders"))

app.view_functions["order"] = enhanced_order
app.view_functions["admin"] = enhanced_admin
app.view_functions["update_order_status"] = enhanced_update_order_status

def update_order_status_v2(order_id):
    status = request.form.get("status")
    payment_status = request.form.get("payment_status")
    if status not in ORDER_STATUSES:
        abort(400)
    if payment_status not in {"待付款", "已付款"}:
        abort(400)
    with get_db() as conn:
        conn.execute("UPDATE orders SET status=?, payment_status=? WHERE id=?", (status, payment_status, order_id))
    return redirect(request.referrer or url_for("admin_orders"))

app.view_functions["update_order_status"] = update_order_status_v2

@app.post("/api/ai-chat")
def ai_chat():
    """Private server-side bridge to OpenAI; the browser never receives the API key."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return jsonify({"error": "尚未設定 ChatGPT API 金鑰", "setup_required": True}), 503

    client_ip = request.headers.get("CF-Connecting-IP", request.remote_addr or "unknown")
    now = time.time()
    recent = [stamp for stamp in AI_RATE_LIMIT.get(client_ip, []) if now - stamp < 60]
    if len(recent) >= 12:
        return jsonify({"error": "請稍候一分鐘後再繼續提問。"}), 429
    recent.append(now)
    AI_RATE_LIMIT[client_ip] = recent

    payload = request.get_json(silent=True) or {}
    question = str(payload.get("message", "")).strip()
    mode = str(payload.get("mode", "chat")).strip()
    if not question or len(question) > 500:
        return jsonify({"error": "請輸入 1 到 500 個字的問題。"}), 400

    translation_instruction = ""
    if mode == "translate":
        direction = str(payload.get("direction", "zh-vi"))
        translation_instruction = (
            "這是翻譯任務。若為中文翻越南文，請先給南越常用翻譯；若北越用詞不同，另列「北越：」。"
            "若為越南文翻繁體中文，請說明詞彙是否偏南越或北越。不要添加不必要的說明。"
        )

    instructions = (
        "你是『安嘉之越南美食品在淡水』的雙語 AI 導覽員與中越翻譯助手。"
        "可回答所有與越南相關且合理的問題，尤其是越南料理、食材、飲料、甜點、小吃、菜名、烹調方式、"
        "香草與調味料、過敏原提醒、點餐與外帶用語、價格詢問、禮貌稱呼、問候與日常會話、"
        "家庭稱謂、節慶、傳統、飲食禮儀、地理、旅遊、歷史與文化差異。"
        "回答美食時可說明常見食材、口味、吃法、適合搭配；涉及本店菜單時，以本店實際菜單為優先。"
        "所有一般回答都必須同時有兩個清楚段落：『繁中：』與『Tiếng Việt:』。"
        "中文翻越南文時，預設使用南越常用說法；若北越用詞明確不同，另列『北越：』。"
        "越南文翻繁體中文時，請保留原本語氣，並在必要時簡短註記其南越或北越用法。"
        "不可把不確定內容說成事實；不確定時要明說，並避免編造菜名、文化來源或歷史。"
        "對醫療、法律、金融與嚴重過敏問題，只提供一般資訊並建議洽詢專業人士。"
        "對完全無關越南的題目，禮貌說明本聊天室主要介紹越南相關內容。"
        + translation_instruction
    )
    request_body = json.dumps({
        "model": "gpt-5.6-luna",
        "instructions": instructions,
        "input": question,
        "store": False,
        "text": {"verbosity": "medium"}
    }).encode("utf-8")
    api_request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=request_body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(api_request, timeout=35) as api_response:
            result = json.loads(api_response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return jsonify({"error": f"ChatGPT 服務暫時無法使用（{error.code}）。"}), 502
    except (urllib.error.URLError, TimeoutError):
        return jsonify({"error": "ChatGPT 連線逾時，請稍後再試。"}), 504

    answer = result.get("output_text", "").strip()
    if not answer:
        for item in result.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    answer += content.get("text", "")
    if not answer:
        return jsonify({"error": "ChatGPT 沒有回傳文字，請再試一次。"}), 502
    return jsonify({"answer": answer})


@app.after_request
def add_taiwan_clock(response):
    if response.content_type.startswith("text/html"):
        page = response.get_data()
        if request.path == "/" and b"my-orders-home" not in page:
            orders_link = '<a class="my-orders-home" href="/my-orders">我的外帶訂單／Đơn mang đi của tôi</a>'.encode("utf-8")
            page = page.replace(b"</main>", orders_link + b"</main>")
        if b"site-footer" not in page:
            footer_text = "安嘉之越南美食品在淡水"
            if not request.path.startswith("/admin"):
                footer_text += '　<a href="/my-orders">我的訂單</a>'
            footer = f'<footer class="site-footer">{footer_text}</footer></body>'.encode("utf-8")
            page = page.replace(b"</body>", footer)
        if b"clock.js" not in page:
            page = page.replace(b"</body>", b'<script src="/static/clock.js"></script></body>')
        response.set_data(page)
    return response

if __name__ == "__main__": init_db(); app.run(debug=False,host="0.0.0.0",port=5000)
