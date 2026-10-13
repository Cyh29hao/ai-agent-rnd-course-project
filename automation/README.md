# 智能体课程汇报自启动

2026-10-13北京时间21:15触发，等待官方额度确认恢复。参考FIR已通过预检的调度器，使用独立CLI会话并从文件读取最新任务，避免App active-writer冲突。已注册不等于已启动；只有preflight.json passed=true、计划任务LastTaskResult=0才证明真实预检。

25%准备收尾，20%硬停止，每120秒检查额度；不消耗reset credits。Windows任务隐藏运行、单实例、错过补跑、允许电池并尝试唤醒。电脑需开机、用户保持登录、网络可用；不能保证关机时执行。实际状态看status.json与scheduler.jsonl，后台回复不自动写回原App聊天。启动失败写日志和error/blocked状态，不伪称执行。

完成后新版本在大作业_V3_制作中/V4；未完成按后台交接继续。STOP_REQUESTED文件可停止后续执行。旧01:25任务保持禁用。
