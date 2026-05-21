# ========== 运行后直接输入内容，不用改任何代码 ==========
products = []

print("====== 批量生成 Shoplazza 产品图片 JS 代码 ======")
print("输入规则：")
print("1. 先输入【产品名称】")
print("2. 再输入【图片链接】，一行一个")
print("3. 输完链接后，直接【回车空一行】结束当前产品")
print("4. 所有产品输完后，再次【回车空一行】生成代码\n")

while True:
    # 输入产品名称
    name = input("请输入产品名称：").strip()
    if not name:
        break

    # 输入图片链接
    print("\n请输入图片链接（一行一个，空行结束）：")
    urls = []
    while True:
        url = input().strip()
        if not url:
            break
        urls.append(url)

    products.append([name, urls])
    print(f"\n✅ 产品「{name}」已录入，共 {len(urls)} 张图\n")

# 生成 JS 代码
print("\n" + "="*60)
print("【👇 直接复制以下代码到 Shoplazza 👇】\n")

print("const allProducts = [")

for prod_name, img_urls in products:
    print(f'["{prod_name}", [')
    for url in img_urls:
        print(f'    {{"id": "", "name": "{url}", "mimeType": "image/jpeg", "isImgur": false}},')
    print(']],')

print("]")

print("\n" + "="*60)
print("✅ 生成完成！复制即可使用")