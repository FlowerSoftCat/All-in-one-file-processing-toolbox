from pathlib import Path
import re
import shutil
from collections import defaultdict
import sys

def organize_safe(target_path):
    """
    整理核心逻辑，现在接收一个路径参数
    """
    # 转换为 Path 对象
    current_path = Path(target_path)
    
    # 获取脚本自身的名字，防止把自己也整理了
    if getattr(sys, 'frozen', False):
        script_name = Path(sys.executable).name
    else:
        script_name = Path(__file__).name

    print("="*60)
    print(f"📍 目标目录: {current_path}")
    print("="*60)

    # --- 第一阶段：扫描 ---
    print("\n[1/2] 🔍 正在扫描...")
    
    file_groups = defaultdict(list)
    all_files = []
    
    try:
        for f in current_path.iterdir():
            # 只处理文件，且排除脚本自身
            if f.is_file() and f.name != script_name:
                all_files.append(f)
    except Exception as e:
        print(f"❌ 无法读取目录: {e}")
        return

    if not all_files:
        print("⚠️  当前目录下没有找到文件。")
        return

    for file in all_files:
        filename_no_ext = file.stem
        # 匹配后缀如 "_1", "_2" 的正则
        match = re.search(r'_(\d+)$', filename_no_ext)
        
        if match:
            core_name = filename_no_ext[:match.start()]
        else:
            core_name = filename_no_ext
        
        file_groups[core_name].append(file)

    # --- 第二阶段：处理 ---
    print("\n[2/2] 📦 开始整理...")
    
    created_count = 0
    moved_count = 0
    skipped_count = 0
    error_count = 0

    for core_name, files in file_groups.items():
        # 逻辑：数量小于2不处理
        if len(files) < 2:
            skipped_count += len(files)
            continue

        target_folder = current_path / core_name
        
        # 创建文件夹
        if not target_folder.exists():
            try:
                target_folder.mkdir()
                created_count += 1
                print(f"  [新建] {core_name}/")
            except Exception as e:
                print(f"  [错误] 无法创建文件夹 '{core_name}': {e}")
                continue

        # 移动文件
        for file in files:
            target_path = target_folder / file.name
            
            if target_path.exists():
                print(f"  [跳过] {file.name} (目标已存在)")
                continue
            
            try:
                shutil.move(str(file), str(target_path))
                moved_count += 1
                print(f"  [OK] {file.name}")
            except PermissionError:
                print(f"  [拒绝访问] {file.name} (文件被占用或无权限，已跳过)")
                error_count += 1
            except Exception as e:
                print(f"  [失败] {file.name}: {str(e)}")
                error_count += 1

    # --- 总结 ---
    print("\n" + "="*60)
    print("✅ 整理结束。")
    print(f"   新建文件夹: {created_count}")
    print(f"   成功移动:   {moved_count}")
    print(f"   保持不动:   {skipped_count} (单个文件)")
    if error_count > 0:
        print(f"   报错跳过:   {error_count} (请查看上方日志)")
    print("="*60)

def get_default_path():
    """获取默认路径（脚本所在目录）"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent

def main():
    default_path = get_default_path()
    
    while True:
        print("\n" + "="*60)
        print("       文件归类工具 (菜单版)")
        print("="*60)
        print("1. 开始整理")
        print("2. 退出程序")
        
        choice = input("请输入选项 (1/2): ").strip()
        
        if choice == '1':
            print(f"\n请输入要整理的文件夹路径 (直接回车默认为: {default_path})")
            user_input = input("路径: ").strip().replace('"', '')
            
            # 确定最终路径
            if not user_input:
                work_path = default_path
            else:
                work_path = Path(user_input)
            
            # 检查路径合法性
            if work_path.exists() and work_path.is_dir():
                organize_safe(work_path)
            else:
                print(f"\n❌ 错误：路径不存在或不是文件夹: {work_path}")
            
            print("\n按回车键返回主菜单...")
            input() # 暂停，等待用户看完结果
            
        elif choice == '2':
            print("程序已退出。")
            break
        else:
            print("输入无效，请重新输入。")

if __name__ == "__main__":
    main()