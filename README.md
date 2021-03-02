# Video Downloader
A repository to learn how to write a telegram bot in Python.  
If you want to use this bot, clone this repository to your VPS or NAS and run your own instance, because this bot save files to my personal server.  
To deploy, make a copy of `settings-template.py` and call it `settings.py`. Put this file in the root directory of this project. This file will contains the settings required for the bot to run. Do this or **the bot won't run**.  

_Current State:_
* Deployed on Hub. Reply the client with the same text message sent from the client;
* Download videos from 
<a href="https://www.youtube.com/" target="_blank"> Youtube </a>
and 
<a href="https://www.bilibili.com/" target="_blank"> Bilibili </a>
* If you send a LaTex expression to the bot, it will reply with the rendered image of the expression.
* Process monitor for commands executed with `track [command]` .
  
_Next Step:_ 
* process monitor/notification with pipeline, so that a notification can be sent when a process is added.

# Credits:
<a href="https://github.com/ujay-zheng/biget" target="_blank"> ujay-zheng/biget </a>
