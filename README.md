# UE 工程名称修改脚本

# 思路

使用python写一个脚本程序，Unreal Engine 更改工程名称。

要求：
1. 首先，脚本启动后提示用户输入Unreal Engine目录的路径，用户输入后，系统判断该目录是否存在，如果不存在则提示用户检查输入，等待用户重新输入；如果目录存在，则读取该目录下 后缀名为 `.uproject`的文件（比如`DT_Template.uproject`）,该文件其实是 json 文件，读取其中 `EngineAssociation` 字段，标识UE的大版本，显示该版本号：
    ```
    ProjectName : {UE工程名}
    EngineAssociation : {UE版本}
    ```
    其中` {UE工程名}`替换为`.uproject`的文件名不含后缀名，其中 `{UE版本}`替换为 读取到的 `EngineAssociation` 字段的值；
2. 上一步执行完成后，正确拿到UE工程的原名称，全局记录该名称，因为后续修改需要用到。显示一段提示语，提示用户输入需要修改成的新名称，并提示用户输入字母数字和下划线组合的字符串，待用户输入完成回车确认后，检查名称是否满足字母数字和下划线组合的字符串，如果输入包含中文或其他特殊字符，则提示用户重新输入。
3. 上一步，新的工程名称确定好之后，显示一段提示文本，提示用户是否确认修改，并分别显示工程原名称和将要修改的新名称，等待用户确认（Y[es]/N[o]）,如果输入为否定的，则重新返回执行上一步操作。
4. 新名称确认好之后，开始修改操作：
- 4.1 删除工程目录下以下几个文件夹和文件（如果存在）： Binaries、Intermediate、Saved、DerivedDataCache、*.sln， 并显示出 执行日志 删除了哪些文件和文件夹
- 4.2 修改后缀为`.uproject`文件（就是第1步找到的那个`.uproject`文件）的名称，新名称为第3步确认的新名称，只修改文件名不修改后缀名。并显示出 执行日志。
- 4.3 编辑`Config\DefaultGame.ini`文件，`.ini`文件为类似`yaml`的数据格式。找到`[/Script/EngineSettings.GeneralProjectSettings]`分类下面如果有`ProjectName=*`的数据（其中`*`为旧名称），将`=`之后的旧名称修改为新名称，如果未找到则添加。并显示出 执行日志。
- 4.4 如果是C++项目，即在项目根目录下有个`Source`文件夹，Source目录下源文件的文件名称不改，只改`*.Target.cs`和`*Editor.Target.cs`文件为新的项目名称，替换其中`*`部分，后面`.Target.cs`或`Editor.Target.cs`保持不变，只替换其中`*`部分。并显示出 执行日志。
- 4.4.1 修改改名后新的`.Target.cs`和`*Editor.Target.cs`文件内容，该文件为C#文件，修改类名为新的类名，比如：

	`.Target.cs`文件修改：
	``` csharp
	public class DT_TemplateTarget : TargetRules
	{
		public DT_TemplateTarget(TargetInfo Target) : base(Target)
		{
			Type = TargetType.Game;
			DefaultBuildSettings = BuildSettingsVersion.V2;
	
			ExtraModuleNames.AddRange( new string[] { "DT_Template" } );
		}
	}
	```
	修改为：
	``` csharp
	public class NewNameTarget : TargetRules
	{
		public NewNameTarget(TargetInfo Target) : base(Target)
		{
			Type = TargetType.Game;
			DefaultBuildSettings = BuildSettingsVersion.V2;
	
			ExtraModuleNames.AddRange( new string[] { "DT_Template" } );
		}
	}
	```
	
	
	`*Editor.Target.cs`文件修改：
	``` csharp
	public class DT_TemplateEditorTarget : TargetRules
	{
		public DT_TemplateEditorTarget(TargetInfo Target) : base(Target)
		{
			Type = TargetType.Editor;
			DefaultBuildSettings = BuildSettingsVersion.V2;
	
			ExtraModuleNames.AddRange( new string[] { "DT_Template" } );
		}
	}
	```
	修改为：
	``` csharp
	public class NewNameEditorTarget : TargetRules
	{
		public NewNameEditorTarget(TargetInfo Target) : base(Target)
		{
			Type = TargetType.Editor;
			DefaultBuildSettings = BuildSettingsVersion.V2;
	
			ExtraModuleNames.AddRange( new string[] { "DT_Template" } );
		}
	}
	```
	
	
	将旧的代码中`DT_TemplateTarget`替换为`NewNameTarget`,其中`DT_Template`为旧名称，`NewName`为用户输入的新工程名其余不改。需要注意的是`ExtraModuleNames.AddRange`这行代码不做任何修改，保持原样。

5. 提示修改完成，等待用户输入任意键退出程序

# 流程图

``` mermaid
flowchart TD
    A([开始]) --> B[输入项目路径]
    B --> C{路径有效?}
    C -->|否| D[提示重新输入]
    D --> B
    C -->|是| E[解析项目信息]
    E --> F[显示当前名称/版本]
    F --> G[输入新名称]
    G --> H{名称合法?}
    H -->|否| I[提示重新输入]
    I --> G
    H -->|是| J[确认修改]
    J --> K{用户确认?}
    K -->|否| G
    K -->|是| L[清理中间文件]
    L --> M[重命名.uproject]
    M --> N[更新INI配置]
    N --> O{存在Source目录?}
    O -->|是| P[重命名Target文件]
    P --> Q[更新类定义]
    Q --> R[处理普通Target]
    Q --> S[处理EditorTarget]
    O -->|否| T[跳过C++处理]
    R --> U[完成修改]
    S --> U
    T --> U
    U --> V[显示完成]
    V --> W([结束])
```

# 资料

- [Ue修改替换项目名称以及打包的名称 - 哔哩哔哩](https://www.bilibili.com/opus/988472790336143361)
