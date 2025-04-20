import os
import re
import json
import shutil
import glob

# ---------------------------
# 工具函数
# ---------------------------
def get_valid_directory():
    """获取有效的项目目录路径"""
    while True:
        path = input("请输入Unreal Engine项目目录路径：").strip()
        if os.path.isdir(path):
            return os.path.normpath(path)
        print("错误：目录不存在，请检查路径后重新输入。")

def validate_new_name(name):
    """验证新名称是否符合规范"""
    return re.match(r'^\w+$', name) is not None

def get_confirmation(prompt):
    """获取用户确认(Y/N)"""
    while True:
        choice = input(prompt).lower()
        if choice in ('y', 'yes'):
            return True
        elif choice in ('n', 'no'):
            return False
        print("请输入 Y/N 或 yes/no")

# ---------------------------
# 核心逻辑
# ---------------------------
class UEProjectRenamer:
    def __init__(self):
        self.project_dir = None
        self.old_name = None
        self.new_name = None
        self.uproject_path = None
        self.is_cpp_project = False

    def run(self):
        try:
            self.setup_project_info()
            self.get_new_name()
            self.confirm_operation()
            self.perform_rename()
            print("\n操作成功完成！")
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
        finally:
            input("\n按任意键退出...")

    def setup_project_info(self):
        """步骤1：获取项目基本信息"""
        self.project_dir = get_valid_directory()
        
        # 查找uproject文件
        uproject_files = glob.glob(os.path.join(self.project_dir, "*.uproject"))
        if not uproject_files:
            raise Exception("未找到.uproject文件")
        if len(uproject_files) > 1:
            raise Exception("发现多个.uproject文件")
        
        self.uproject_path = uproject_files[0]
        self.old_name = os.path.splitext(os.path.basename(self.uproject_path))[0]
        
        # 解析引擎版本
        with open(self.uproject_path, "r", encoding="utf-8") as f:
            content = "".join([line.split("//")[0].strip() for line in f])
            data = json.loads(content)
        
        engine_version = data.get("EngineAssociation", "未知版本")
        print(f"\n当前项目信息：")
        print(f"ProjectName       : {self.old_name}")
        print(f"EngineAssociation : {engine_version}\n")

    def get_new_name(self):
        """步骤2：获取并验证新名称"""
        while True:
            self.new_name = input("请输入新的项目名称（仅允许字母/数字/下划线）：").strip()
            if validate_new_name(self.new_name):
                if self.new_name == self.old_name:
                    print("新名称不能与旧名称相同！")
                    continue
                return
            print("名称包含非法字符，请重新输入！")

    def confirm_operation(self):
        """步骤3：确认操作"""
        print(f"\n即将执行重命名操作：")
        print(f"原项目名称: {self.old_name}")
        print(f"新项目名称: {self.new_name}")
        print(f"\n* 请确保UE编辑器和Visual Studio已关闭，否则可能会导致文件锁定。\n")
        if not get_confirmation("是否确认继续？(Y/N): "):
            self.get_new_name()
            self.confirm_operation()

    def perform_rename(self):
        """步骤4：执行所有重命名操作"""
        self.clean_intermediate_files()
        self.rename_uproject_file()
        self.update_ini_settings()
        self.check_cpp_project()
        if self.is_cpp_project:
            self.rename_target_files()
            self.update_target_classes()

    def clean_intermediate_files(self):
        """4.1 清理中间文件"""
        targets = [
            ("Binaries", "目录"),
            ("Intermediate", "目录"), 
            ("DerivedDataCache", "目录"),
            ("Saved", "目录"),
            ("*.sln", "文件")
        ]
        
        print("\n正在清理中间文件...")
        for pattern, type_name in targets:
            paths = glob.glob(os.path.join(self.project_dir, pattern))
            for path in paths:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        print(f"已删除目录: {os.path.basename(path)}")
                    else:
                        os.remove(path)
                        print(f"已删除文件: {os.path.basename(path)}")
                except Exception as e:
                    print(f"删除失败 {type_name}: {path} - {str(e)}")

    def rename_uproject_file(self):
        """4.2 重命名uproject文件"""
        new_path = os.path.join(self.project_dir, f"{self.new_name}.uproject")
        os.rename(self.uproject_path, new_path)
        print(f"\n已重命名项目文件: {self.new_name}.uproject")

    def update_ini_settings(self):
        """4.3 更新INI文件配置"""
        ini_path = os.path.join(self.project_dir, "Config", "DefaultGame.ini")
        if not os.path.exists(ini_path):
            return

        print("\n更新INI配置...")
        section = "[/Script/EngineSettings.GeneralProjectSettings]"
        new_line = f"ProjectName={self.new_name}"
        updated = False

        with open(ini_path, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            f.seek(0)
            in_section = False
            
            for line in lines:
                if line.strip() == section:
                    in_section = True
                elif in_section and line.startswith("ProjectName="):
                    line = new_line + "\n"
                    updated = True
                elif in_section and line.startswith("["):
                    in_section = False
                
                f.write(line)
            
            if not updated:
                f.write("\n" + section + "\n" + new_line + "\n")

        print(f"已更新 {os.path.basename(ini_path)}")

    def check_cpp_project(self):
        """检查是否为C++项目"""
        source_dir = os.path.join(self.project_dir, "Source")
        self.is_cpp_project = os.path.exists(source_dir)

    def rename_target_files(self):
        """4.4 重命名Target文件"""
        patterns = [
            f"{self.old_name}.Target.cs",
            f"{self.old_name}Editor.Target.cs"
        ]
        
        print("\n重命名Target文件：")
        for pattern in patterns:
            old_path = os.path.join(self.project_dir, "Source", pattern)
            if os.path.exists(old_path):
                new_name = pattern.replace(self.old_name, self.new_name)
                new_path = os.path.join(self.project_dir, "Source", new_name)
                os.rename(old_path, new_path)
                print(f"重命名: {pattern} -> {new_name}")

    def update_target_classes(self):
        """4.4.1 精确修改所有Target类名"""
        files = [
            f"{self.new_name}.Target.cs",
            f"{self.new_name}Editor.Target.cs"
        ]
        
        print("\n更新C#类定义：")
        for filename in files:
            filepath = os.path.join(self.project_dir, "Source", filename)
            if not os.path.exists(filepath):
                continue

            with open(filepath, "r+", encoding="utf-8") as f:
                content = f.read()
                
                # 匹配两种类名模式：XXXTarget 和 XXXEditorTarget
                patterns = [
                    (rf'class\s+{re.escape(self.old_name)}(Target\b)', f'class {self.new_name}\\1'),
                    (rf'public\s+{re.escape(self.old_name)}(Target\()', f'public {self.new_name}\\1'),
                    (rf'class\s+{re.escape(self.old_name)}(EditorTarget\b)', f'class {self.new_name}\\1'),
                    (rf'public\s+{re.escape(self.old_name)}(EditorTarget\()', f'public {self.new_name}\\1')
                ]

                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)
                
                f.seek(0)
                f.write(content)
                f.truncate()
            
            print(f"已更新 {filename} 类定义")

if __name__ == "__main__":
    UEProjectRenamer().run()