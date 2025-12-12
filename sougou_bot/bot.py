# bot.py
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, BotCommand
from scraper import search_telegram
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

# 从 .env 文件读取 TOKEN，确保敏感信息不会暴露在代码中
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# @dp.message() 是装饰器（decorator）
# dp 是 Dispatcher 对象，用于管理机器人的消息路由
# .message() 表示注册一个消息处理器
# 括号内不写条件，表示处理所有接收到的消息
# 被装饰的函数会在收到任何消息时自动调用

# 重要：命令处理器必须在通用处理器之前！

@dp.message(F.command("help"))
async def help_handler(msg: Message):
    """处理 /help 命令"""
    help_text = """
🔍 **Telegram 频道搜索机器人** 使用说明

**基础用法：**
直接输入你要搜索的关键词，机器人会从以下来源搜索相关 Telegram 频道和群组：

📌 **支持的搜索内容：**
• 频道名称或描述（如"美剧"、"编程"等）
• 群组主题（如"投资"、"游戏"等）
• 相关关键词搜索

**命令列表：**
• /start - 显示欢迎信息
• /help - 显示此帮助信息
• /search - 开始搜索

**搜索结果说明：**
每个搜索结果包含：
✓ 频道/群组名称
✓ 直接链接（点击可加入）
✓ 来自多个搜索引擎的综合结果

**使用示例：**
```
用户：python
机器人：返回所有与Python相关的Telegram频道和群组
```

**提示：**
💡 搜索结果会自动去重，避免重复显示
💡 最多显示前20个最相关的结果
💡 如果找不到结果，请尝试其他关键词

❓ 有问题？可以直接输入你想要搜索的内容！
"""
    await msg.reply(help_text, parse_mode="Markdown")


@dp.message(F.command("start"))
async def start_handler(msg: Message):
    """处理 /start 命令"""
    start_text = """
👋 欢迎使用 **Telegram 频道搜索机器人**！

这是一个强大的频道和群组搜索工具。

**快速开始：**
1️⃣ 直接输入你想搜索的关键词
2️⃣ 等待机器人搜索并返回结果
3️⃣ 点击结果中的链接加入频道或群组

**例子：**
输入 `编程` 即可搜索所有编程相关的Telegram频道！

📖 输入 /help 查看详细说明
"""
    await msg.reply(start_text, parse_mode="Markdown")


@dp.message(F.command("search"))
async def search_command_handler(msg: Message):
    """处理 /search 命令"""
    search_text = """
🔍 **开始搜索**

请输入你要搜索的关键词，例如：
• python
• 编程
• 美剧
• 投资
• 游戏

直接输入关键词即可！
"""
    await msg.reply(search_text, parse_mode="Markdown")


@dp.message()
async def search_handler(msg: Message):
    """处理所有文本消息，直接搜索（但排除命令）"""
    query = msg.text.strip()
    
    # 如果是命令（以 / 开头），忽略
    if query.startswith('/'):
        return
    
    if not query:
        return

    await msg.reply(f"🔍 正在搜索：{query}\n请稍候…")

    try:
        # 在线程池运行 search_telegram，避免阻塞
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, search_telegram, query)
    except Exception as e:
        print(f"搜索错误: {e}")
        await msg.reply(f"❌ 搜索失败\n\n错误信息：\n{str(e)}")
        return

    if not results:
        await msg.reply("⚠️ 没有找到相关频道或群。\n\n💡 提示：尝试使用不同的关键词或更简短的搜索词")
        return

    text = f"🔍 **搜索结果：{query}** (共 {len(results)} 个)\n\n"
    for i, item in enumerate(results, 1):
        text += f"{i}. [{item['title']}]({item['link']})\n"
    
    # 添加页脚
    text += "\n---\n💬 继续输入其他关键词继续搜索"

    await msg.reply(text, parse_mode="Markdown", disable_web_page_preview=True)



async def main():
    print("🤖 机器人启动...")
    
    # 设置菜单命令
    commands = [
        BotCommand(command="start", description="👋 欢迎和快速开始"),
        BotCommand(command="help", description="📖 查看使用说明"),
        BotCommand(command="search", description="🔍 搜索Telegram频道"),
    ]
    await bot.set_my_commands(commands)
    print("✅ 菜单已设置")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    # __name__ 是 Python 内置变量
    # 当脚本直接运行时，__name__ 的值为 "__main__"
    # 当脚本被导入时，__name__ 的值为模块名
    # 这样可以区分脚本是直接运行还是被其他文件导入
    asyncio.run(main())
