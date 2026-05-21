import re

# ================ 运行后直接粘贴你的内容，不用改代码 ================
print("请粘贴你的 imgbb 链接代码，完成后按回车两次：\n")

# 自动获取多行输入
lines = []
while True:
    line = input()
    if line == "":
        break
    lines.append(line)
input_str = "\n".join(lines)

# 提取图片链接
img_urls = re.findall(r'src="(https://[^"]+)"', input_str)

# 自动提取产品名（去掉末尾数字）
alt_match = re.search(r'alt="([^"]+?)\s*\d*"', input_str)
product_name = alt_match.group(1).strip() if alt_match else "Product"

# 输出你要的格式
print("\n" + "="*50)
print(f'["{product_name}", [')
for url in img_urls:
    print(f'    {{"id": "", "name": "{url}", "mimeType": "image/jpeg", "isImgur": false}},')
print(']],')