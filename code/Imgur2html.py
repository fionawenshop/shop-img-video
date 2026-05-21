import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 从 embed 代码提取 album_id + 标题
def parse_imgur_embed(code):
    id_match = re.search(r'data-id="([a-zA-Z0-9/]+)"', code)
    title_match = re.search(r'>([^<]+)</a>', code)

    album_id = ""
    if id_match:
        raw = id_match.group(1)
        album_id = raw.split("/")[-1]

    title = title_match.group(1).strip() if title_match else "Product"
    return album_id, title

# 把标题变成 URL 友好格式（空格变横杠，保留正常字符）
def slugify(title):
    title = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
    title = re.sub(r'\s+', '-', title.strip())
    return title.strip('-')

# 获取相册所有内容（图片 + 视频）
def get_album_items(album_id):
    url = f"https://imgur.com/ajaxalbums/getimages/{album_id}/hit.json?all=true"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()

        items = []
        if data.get("success") and isinstance(data.get("data"), dict):
            items = data["data"].get("images", [])
        elif isinstance(data.get("data"), list) and len(data.get("data")) > 0:
            items = data["data"][0].get("images", [])

        result = []
        for item in items:
            hash_str = item.get("hash")
            ext = item.get("ext", "")
            if not hash_str:
                continue

            # 判断是否为视频
            if ext in (".mp4", ".mov", ".avi", ".webm", ".mkv"):
                result.append({
                    "hash": hash_str,
                    "type": "video"
                })
            else:
                result.append({
                    "hash": hash_str,
                    "type": "image"
                })
        return result

    except Exception as e:
        return []

def main():
    print("===== ✅ Imgur 相册 → 自动生成商品格式（图片+视频） =====")
    embed = input("请粘贴整段 Imgur 嵌入代码：\n").strip()

    album_id, title = parse_imgur_embed(embed)
    if not album_id:
        print("❌ 解析失败")
        return

    print(f"\n✅ 商品名称：{title}")
    print(f"✅ 相册ID：{album_id}")
    print("🔍 正在获取所有内容...")

    items = get_album_items(album_id)
    if not items:
        print("❌ 无法获取内容（相册非公开/网络问题）")
        return

    print(f"✅ 成功获取 {len(items)} 个文件\n")

    title_slug = slugify(title)
    output_items = []

    for index, item in enumerate(items, start=1):
        h = item["hash"]
        typename = item["type"]

        if typename == "video":
            filename = f"{title_slug}-{index}.mp4"
            line = f'    {{"id": "{h}", "name": "{filename}", "mimeType": "video/mp4", "isImgur": true}}'
        else:
            filename = f"{title_slug}-{index}.jpg"
            line = f'    {{"id": "{h}", "name": "{filename}", "mimeType": "image/jpeg", "isImgur": true}}'

        output_items.append(line)

    output = f'["{title}", [\n' + ",\n".join(output_items) + "\n]],"
    print("👇 复制到你的 HTML 中：\n")
    print(output)

if __name__ == "__main__":
    main()