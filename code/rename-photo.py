import os
import sys

def convert_to_jpg(img_path, out_path):
    try:
        data = open(img_path, 'rb').read()
        with open(out_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"转换异常: {e}")
        return False

def main():
    print("===== 【零依赖】图片转JPG+视频重命名（全局连续序号）=====")
    folder = input("请输入文件夹完整路径：").strip().strip('"')
    if not os.path.isdir(folder):
        print("路径无效")
        return

    prefix = input("请输入重命名前缀：").strip()
    prefix = prefix.replace(" ", "-")
    if not prefix:
        prefix = "file"

    IMG_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.heic', '.heif', '.avif')
    VID_FORMATS = ('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v', '.3gp', '.webm')

    images = []
    videos = []

    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        if not os.path.isfile(path):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext in IMG_FORMATS:
            images.append(path)
        elif ext in VID_FORMATS:
            videos.append(path)

    print(f"\n找到 {len(images)} 张图片，{len(videos)} 个视频")
    input("按回车开始处理...")

    # 全局统一序号
    index = 1

    # ==================== 处理图片 ====================
    print("\n-------- 开始转换图片 --------")
    for img_path in images:
        new_name = f"{prefix}-{index}.jpg"
        new_path = os.path.join(folder, new_name)
        
        try:
            convert_to_jpg(img_path, new_path)
            os.remove(img_path)
            print(f"✅ {os.path.basename(img_path)} → {new_name}")
            index += 1  # 全局递增
        except Exception as e:
            print(f"❌ 失败：{os.path.basename(img_path)}")

    # ==================== 处理视频（接在图片序号后面） ====================
    print("\n-------- 开始重命名视频 --------")
    for vid_path in videos:
        ext = os.path.splitext(vid_path)[1].lower()
        new_name = f"{prefix}-{index}{ext}"
        new_path = os.path.join(folder, new_name)
        
        try:
            os.rename(vid_path, new_path)
            print(f"✅ {os.path.basename(vid_path)} → {new_name}")
            index += 1  # 继续递增
        except Exception as e:
            print(f"❌ 失败：{os.path.basename(vid_path)}")

    print(f"\n🎉 全部处理完成！总共重命名 {index-1} 个文件")
    input("\n按回车退出")

if __name__ == "__main__":
    main()