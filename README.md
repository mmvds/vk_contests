#Script makes reposts of VKontakte (social network) contests
How to win in VK contests?
It's easy, you need to make reposts of all competitions :)
Learn More (RU) https://habrahabr.ru/post/331312/

## Installing
```
pip install vk_api
```
unzip to ~/vk folder and add to crontab:
```
05 00 * * *  cat ~/vk/reposted.txt | grep -c "" > ~/vk/todaycount.txt
17 01-20/2 * * * cd ~/vk && /home/bvi/vk/vk_collect.py 2 >> ~/vk_collect.log
15 00 * * * echo "" > ~/vk/vk_collect.log
```

