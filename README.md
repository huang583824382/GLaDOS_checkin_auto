# GLaDOS 自动签到，实现无限白嫖

原仓库地址：https://github.com/lukesyy/glados_automation

复制了一个仓库，进行了些修改，防止原仓库被封

环境变量：`GLADOS_COOKIE`（必要）

`GLADOS_COOKIE`多个账号需使用 '&' 隔开，示例：cookie&cookie



# Github Actions

1. 点击右上角 **fork** 按钮
2. 在自己仓库中打开此项目
3. 将 `runGladosAction.yml` 放入 `.github/workflows` 文件夹下
4. 配置环境变量
5. 点亮右上角的星星 **star** 激活 actions
6. 然后点击 Actions 标签查看运行的详细状况

![image](https://user-images.githubusercontent.com/70319988/231369203-c812910a-963d-45b8-98a5-95b2623c25d7.png)
![image](https://user-images.githubusercontent.com/70319988/199923789-639e8295-b03e-4abd-858e-ff427015512a.png)
![image](https://user-images.githubusercontent.com/70319988/199923884-d81dd457-ecc5-4de9-b480-191d25217c47.png)

 # 青龙面板

将 `glados_Qinglong.py` 和 `glados.py` 一起放到青龙里，环境变量同上。

签到成功或识别到当日已签到时正常退出（退出码 0）；任一账号签到失败时返回非零退出码。状态查询、积分查询和自动兑换失败只记录日志，不影响签到退出码。

签到失败后默认等待 60 秒重试一次（共尝试 2 次），两次均失败才返回非零退出码。签到成功或已签到不会重试。可通过 `CHECKIN_MAX_ATTEMPTS` 和 `CHECKIN_RETRY_DELAY_SECONDS` 调整总尝试次数和间隔。
