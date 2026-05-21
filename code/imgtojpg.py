import os
from PIL import Image
import pillow_heif

# 注册heic/heif格式支持
pillow_heif.register_heif_opener()

def convert_cover_original(folder_path, max_size_mb=10):
    supported_formats = (
        '.png', '.jpg', '.jpeg', '.bmp', '.gif',
        '.tiff', '.webp', '.heic', '.heif'
    )
    max_size_bytes = max_size_mb * 1024 * 1024
    init_quality = 95

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isdir(file_path):
            continue

        suffix = os.path.splitext(filename)[1].lower()
        if suffix not in supported_formats:
            continue

        print(f"\n正在处理：{filename}")
        try:
            with Image.open(file_path) as img:
                # 透明通道转白底
                if img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")

                # 统一后缀为 .jpg，文件名不变
                name_only = os.path.splitext(filename)[0]
                new_path = os.path.join(folder_path, name_only + ".jpg")

                current_quality = init_quality
                # 循环压缩到10M以内
                while current_quality >= 10:
                    img.save(new_path, "JPEG", quality=current_quality, optimize=True)
                    if os.path.getsize(new_path) <= max_size_bytes:
                        break
                    current_quality -= 8

                # 如果原文件不是jpg，删除旧图实现覆盖替换
                if suffix != ".jpg":
                    os.remove(file_path)

                print(f"✅ 已覆盖替换：{name_only}.jpg")

        except Exception as e:
            print(f"❌ 处理失败 {filename}：{str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    folder = input("请输入图片文件夹完整路径：").strip()
    print("=" * 50)

    if not os.path.isdir(folder):
        print("❌ 路径不存在，请检查！")
    else:
        convert_cover_original(folder, max_size_mb=10)
        print("\n🎉 全部处理完成！")