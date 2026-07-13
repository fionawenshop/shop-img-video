import os
from io import BytesIO
from PIL import Image

def batch_convert_replace_original(folder_dir, limit_mb=1):
    max_byte = limit_mb * 1024 * 1024
    # 支持的图片后缀
    support_ext = (".png", ".webp", ".bmp", ".tiff", ".jpeg", ".heic", ".jpg")

    if not os.path.isdir(folder_dir):
        print(f"\n错误：文件夹不存在，请检查路径：{folder_dir}")
        return

    total = 0
    success = 0
    fail = 0

    for file_name in os.listdir(folder_dir):
        file_full_path = os.path.join(folder_dir, file_name)
        # 跳过子文件夹
        if os.path.isdir(file_full_path):
            continue

        file_stem, ext = os.path.splitext(file_name)
        ext_lower = ext.lower()
        if ext_lower not in support_ext:
            continue

        total += 1
        out_file_name = f"{file_stem}.jpg"
        out_full_path = os.path.join(folder_dir, out_file_name)

        # 跳过自身，防止重复处理
        if file_full_path == out_full_path:
            try:
                # 原图是jpg，直接压缩
                img = Image.open(file_full_path).convert("RGB")
                quality = 95
                step = 5
                while True:
                    buf = BytesIO()
                    img.save(buf, format="JPEG", quality=quality, optimize=True)
                    size = buf.tell()
                    if size <= max_byte or quality <= 10:
                        break
                    quality -= step
                img.save(out_full_path, format="JPEG", quality=quality, optimize=True)
                kb = round(size / 1024, 2)
                print(f"压缩 | {file_name} | 画质:{quality} | {kb}KB")
                success += 1
                continue
            except Exception as e:
                print(f"失败 | {file_name} 错误：{str(e)}")
                fail += 1
                continue

        try:
            # 打开图片转RGB
            img = Image.open(file_full_path).convert("RGB")
            quality = 95
            step = 5

            # 循环降低画质至1MB以内
            while True:
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=quality, optimize=True)
                size = buf.tell()
                if size <= max_byte or quality <= 10:
                    break
                quality -= step

            # 保存新jpg
            img.save(out_full_path, format="JPEG", quality=quality, optimize=True)
            # 删除原始文件，实现替换
            os.remove(file_full_path)
            kb = round(size / 1024, 2)
            print(f"替换 | {file_name} → {out_file_name} | 画质:{quality} | {kb}KB")
            success += 1
        except Exception as e:
            print(f"失败 | {file_name} 错误：{str(e)}")
            fail += 1

    print(f"\n===== 处理完成 =====")
    print(f"总计图片：{total} 张")
    print(f"处理成功：{success} 张")
    print(f"处理失败：{fail} 张")


if __name__ == "__main__":
    print("===== 图片批量转JPG并压缩至1M内（直接替换原文件） =====")
    print("警告：转换后会删除原始图片文件！请提前备份重要图片！\n")
    folder_path = input("请输入图片文件夹完整路径：").strip()
    batch_convert_replace_original(folder_path, limit_mb=1)
    input("\n按回车键退出程序...")