import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ====================== 已修复全部配置 ======================
SHOPLAZZA_TOKEN = "HBiAoOWvmXIurDQNxyxvzIilP8u9bCw_UQhwSAarxDQ"
MERCHANT_ID = "5767395360"
GOOGLE_JSON_KEY = "merchant-center-sync-493511-133582a88354.json"
CURRENCY = "USD"

# ✅ 已改成你的正确主域名！
SHOP_URL = "https://fionawen.com"
# ============================================================

# 拉取商品（cursor 分页，不会死循环）
def fetch_all_products():
    all_products = []
    cursor = ""
    while True:
        url = f"{SHOP_URL}/openapi/2022-01/products?limit=250"
        if cursor:
            url += f"&cursor={cursor}"

        headers = {"Access-Token": SHOPLAZZA_TOKEN}
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            data = resp.json()
        except:
            break

        products = data.get("products", [])
        if not products:
            break

        all_products.extend(products)
        cursor = data.get("cursor")
        print(f"拉取 {len(products)} 件，总计：{len(all_products)}")

    return all_products

# 转换 Google 标准格式（全字段齐全）
def convert_to_google(product):
    items = []
    for v in product["variants"]:
        sku = v.get("sku", f"FW_{v['id']}")
        if sku.startswith("-"):
            sku = f"FW_{v['id']}"

        item = {
            "offerId": sku,
            "title": product["title"],
            "description": product.get("description", "Dress").replace("<p>","").replace("</p>","").replace("<br>"," "),
            # ✅ 这里现在是正确域名：https://fionawen.com
            "link": f"{SHOP_URL}/products/{product['handle']}?variant={v['id']}",
            "imageLink": "https:" + product["image"]["src"],
            "price": {
                "value": float(v["price"]),
                "currency": CURRENCY
            },
            "availability": "in stock",
            "condition": "new",
            "brand": "FionaWen",
            "channel": "online",
            "contentLanguage": "en",
            "targetCountry": "US"
        }
        items.append(item)
    return items

# 上传商品
def upload_to_google(items):
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_JSON_KEY,
        scopes=["https://www.googleapis.com/auth/content"]
    )
    service = build("content", "v2.1", credentials=credentials)

    for item in items:
        try:
            service.products().insert(
                merchantId=MERCHANT_ID,
                body=item
            ).execute()
            print(f"✅ 上传成功：{item['offerId']}")
        except Exception as e:
            print(f"❌ 失败：{item['offerId']}")
            print(f"错误：{str(e)[:300]}")

# 执行
if __name__ == "__main__":
    products = fetch_all_products()
    google_items = []
    for p in products:
        google_items.extend(convert_to_google(p))
    print(f"总变体：{len(google_items)}")
    upload_to_google(google_items)