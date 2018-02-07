#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import vk_api
import json
import random
import time
import re
import sys
from subprocess import PIPE, Popen

def main():
    login, password = '<email>', '<password>'
    vk_session = vk_api.VkApi(login, password)
    ftc = open('todaycount.txt')
    for ltc in ftc:
      todaycount=int(ltc)
    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    tools = vk_api.VkTools(vk_session)

    def cmdline(command):
      process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
      )
      return process.communicate()[0]

    def isFake(owner_id):#True если фэйк (id>=0 или members_count<60)
      if (owner_id<0):
        with vk_api.VkRequestsPool(vk_session) as pool:
          requests=pool.method('groups.getById', {
           'group_id':-owner_id,
            'fields':['members_count']
            })
        if (int(requests.result[0]['members_count'])>60):
          return False
        else:
          print 'Fake: id'+ str(owner_id)+' count:'+ str(int(requests.result[0]['members_count']))
      return True

    def isStop(description):#True если описание содержит стоп слова
      fstop = open('stopwords.txt')
      for stopword in fstop:
        if description.decode('utf-8').lower().find(stopword.decode('utf-8').lower().strip())>-1:
          print description+'\n'+stopword+'\n'
          return True
      return False

    def makeRepostSteampunk():#Репостим стимпанк группу в конце дня, чтобы быть похожими на человека
     print 'Парсим группу: 39009769'
     with vk_api.VkRequestsPool(vk_session) as pool:
        requests=pool.method('wall.get', {
           'owner_id': '-39009769',
           'count':'300'
            })
     for k in requests.result['items']:
          try:
            if k['copy_history'][0]['owner_id']:
              owner_id=int(k['copy_history'][0]['owner_id'])
              post_id=int(k['copy_history'][0]['id'])
          except:
            owner_id=int(k['owner_id'])
            post_id=int(k['id'])
          if not isReposted(owner_id, post_id):
            if int(re.search(r'\d{1,10}',cmdline("cat reposted.txt | grep -c ''")).group(0))-todaycount<149:
              repname='wall'+str(owner_id)+'_'+str(post_id)
              with vk_api.VkRequestsPool(vk_session) as pool:
                requests=pool.method('wall.repost', {
                'object':repname
                })
              print 'owner_id '+str(owner_id)+' post_id '+str(post_id)
              frep = open('reposted.txt','a+')
              frep.write(str(owner_id)+','+str(post_id)+'\n')
              frep.close()
              break
    
    def makeRepost(owner_id, post_id):
     if int(re.search(r'\d{1,10}',cmdline("cat reposted.txt | grep -c ''")).group(0))-todaycount<144:
      repname='wall'+str(owner_id)+'_'+str(post_id)
      with vk_api.VkRequestsPool(vk_session) as pool:
          requests=pool.method('wall.repost', {
           'object':repname
            })
      print 'owner_id '+str(owner_id)+' post_id '+str(post_id)
      frep = open('reposted.txt','a+')
      frep.write(str(owner_id)+','+str(post_id)+'\n')
      frep.close()
      time.sleep(120.0+random.random()*180.0)
     else:
      print 'На сегодня хватит'
      while int(re.search(r'\d{1,10}',cmdline("cat reposted.txt | grep -c ''")).group(0))-todaycount<149:
        time.sleep(120.0+random.random()*200.0)
        makeRepostSteampunk()
      sys.exit(0)
      
    def isMember(owner_id):
      fjoin = open('joined.txt')
      for group in fjoin:
        if (group.strip()==str(owner_id)):
          return True
      return False

    def joinGroup(owner_id):
      with vk_api.VkRequestsPool(vk_session) as pool:
       if int(owner_id)<0:
        requests=pool.method('groups.join', {
           'group_id':-int(owner_id)
            })
      fjoin = open('joined.txt','a+')
      fjoin.write(str(owner_id)+'\n')
      fjoin.close()

    def isReposted(owner_id, post_id):
      frep = open('reposted.txt')
      for repost in frep:
        if (repost.strip()==str(owner_id)+','+str(post_id)):
          print 'Уже репостили '+str(owner_id)+','+str(post_id)
          return True
      return False

    def checkResults(requests):
     for i in requests.result['items']:
      description=unicode(json.dumps(i['text']),'raw-unicode-escape').encode('utf-8')
      if not isStop(description):
        if not isReposted(int(i['owner_id']),int(i['id'])):
          if not isFake(int(i['owner_id'])):
            print 'Репостим:\n'+description
            makeRepost(i['owner_id'],i['id'])
            for j in re.findall(r'wall-\d{1,10}_\d{1,10}', description):
              j_owner_id=re.search(r'-\d{1,10}',j).group(0)
              j_id=re.search(r'\d{1,10}$',j).group(0)
              if not isReposted(int(j_owner_id),int(j_id)):
                print 'Репостим детей:\n'
                makeRepost(int(j_owner_id),int(j_id))
              if not isMember(int(j_owner_id)):
                joinGroup(int(j_owner_id))
            if not isMember(int(i['owner_id'])):
              joinGroup(int(i['owner_id']))
            for j in re.findall(r'club\d{1,10}', description):
              j_owner_id=-int(re.search(r'\d{1,10}',j).group(0))
              if not isMember(int(j_owner_id)):
                joinGroup(int(j_owner_id))

    def readWall(group_id):
      print 'Парсим группу: ' + str(group_id)
      with vk_api.VkRequestsPool(vk_session) as pool:
        requests=pool.method('wall.get', {
           'owner_id': group_id,
           'count':'9'
            })
      for k in requests.result['items']:
          try:
            if k['copy_history'][0]['owner_id']:
              description=unicode(json.dumps(k['copy_history'][0]['text']),'raw-unicode-escape').encode('utf-8')
              owner_id=k['copy_history'][0]['owner_id']
              post_id=k['copy_history'][0]['id']
          except:
            description=unicode(json.dumps(k['text']),'raw-unicode-escape').encode('utf-8')
            owner_id=k['owner_id']
            post_id=k['id']
          if (description.lower().find('лайк')>-1) or (description.lower().find('Лайк')>-1) or (description.lower().find('Репост')>-1) or (description.lower().find('РЕПОСТ')>-1) or (description.lower().find('друзьям')>-1) or (description.lower().find('репост')>-1) or (description.lower().find('поделит')>-1):
              print description+'\n'
              if not isStop(description):
                if not isReposted(int(owner_id),int(post_id)):
                    print 'Репостим:\n'+description
                    makeRepost(owner_id,post_id)
                    for j in re.findall(r'wall-\d{1,10}_\d{1,10}', description):
                      j_owner_id=re.search(r'-\d{1,10}',j).group(0)
                      j_id=re.search(r'\d{1,10}$',j).group(0)
                      if not isReposted(int(j_owner_id),int(j_id)):
                        print 'Репостим детей:\n'
                        makeRepost(int(j_owner_id),int(j_id))
                      if not isMember(int(j_owner_id)):
                        joinGroup(int(j_owner_id))
                    if not isMember(int(owner_id)):
                      joinGroup(int(owner_id))
                    for j in re.findall(r'club\d{1,10}', description):
                      j_owner_id=-int(re.search(r'\d{1,10}',j).group(0))
                      if not isMember(int(j_owner_id)):
                        joinGroup(int(j_owner_id))
          else:
              print description
              print "Нет слова Репостим"

    with vk_api.VkRequestsPool(vk_session) as pool:
      requests=pool.method('newsfeed.search', {
           'q':u'Конкурс репост подарки Нижний Новгород',
            'count':'150'
            })

    with vk_api.VkRequestsPool(vk_session) as pool:
      requests2=pool.method('newsfeed.search', {
           'q':u'Конкурс репост подарки Россия',
            'count':'150'
            })
    #Репостим золотые группы
    fgc = open('goldclub.txt')
    for club in fgc:
      time.sleep(1.2)
      try:
        readWall(int(club))
      except:
        print 'Не парсится группа '+str(club)

    checkResults(requests)
    checkResults(requests2)
    #checkResults(requests3)

    if (int(re.search(r'\d{1,10}',cmdline("date | cut -f 1 -d :  | awk '$1=$1' | cut -f 4 -d ' '")).group(0))>15): 
      print 'На сегодня хватит'
      while ((int(re.search(r'\d{1,10}',cmdline("cat reposted.txt | grep -c ''")).group(0))-todaycount<149) and (int(re.search(r'\d{1,10}',cmdline("date | cut -f 1 -d :  | awk '$1=$1' | cut -f 4 -d ' '")).group(0))<21)):
        time.sleep(120.0+random.random()*200.0)
        makeRepostSteampunk()
      sys.exit(0)

if __name__ == '__main__':
    main()

