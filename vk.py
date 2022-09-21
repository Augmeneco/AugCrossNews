import requests as req
import re
import time

from objects import *
from utils import *

last_id = 0

def vk_api(method, token=CONFIG['vk_token'], **parameters):
    url = 'https://api.vk.com/method/' + method
    parameters['access_token'] = token
    if 'v' not in parameters:
        parameters['v'] = '5.103'

    # if method.split('.')[1][:3] == 'get':
    r = req.post(url, params=parameters)

    result = r.json()

    # print(result)

    if 'error' in result:
        if result['error']['error_code'] == 29:
            time.sleep(60)
        log_print('VK ERROR #{}: "{}"\nPARAMS: {}'.format(result['error']['error_code'],
                                                          result['error']['error_msg'],
                                                          result['error']['request_params']))
        return None

    return result['response']

def get_source_info(response, source_id):
    if source_id < 0:
        source_id *= -1
        for gr in response['groups']:
            if gr['id'] == source_id:
                return gr
    else:
        for pr in response['profiles']:
            if pr['id'] == source_id:
                pr['name'] = pr['first_name']+' '+pr['last_name']
                return pr

def get_news():
    global last_id

    posts = list()

    response = vk_api('newsfeed.get', count=10, filters='post')

    for news in response['items']:
        try:
            if news['type']=='post':
                if news['post_id'] + news['source_id'] != last_id: 
                    if news['source_id'] not in CONFIG['blacklist']:
                        source = get_source_info(response, news['source_id'])
    
                        post = Post()
                        post.timestamp = news['date']
                        post.url = 'https://vk.com/wall%d_%d' % (news['source_id'], news['post_id'])
                        
                        print(news['source_id'])
                        post.text += '<b>%s</b>' % source['name']
    
                        if 'copy_history' in news:
                            news = news['copy_history'][0]
                            source = get_source_info(response, news['owner_id'])
                            post.text += '\n<i>Репост из</i>: <b>%s</b>' % source['name']
                        
                        post_links = str()
                        if 'attachments' in news:
                            for idx in [idx for idx, x in enumerate(news['attachments']) if x['type'] == 'link']:
                                link = news['attachments'].pop(idx)['link']
                                if news['text'].find(link['url']) == -1:
                                    post_links += '<a href="%s">%s</a>\n' % (link['url'], link['title'][:50])
    
                            previews = list()
                            # for idx in [idx for idx, x in enumerate(news['attachments']) if (x['type'] == 'video') and ('platform' in x[x['type']])]:
                            #     attach = news['attachments'].pop(idx)
                            #     #print(attach)
                            #     print(str(attach['video']['owner_id'])+'_'+str(attach['video']['id']))
                            #     #video = vk_api('video.get', videos=str(attach['video']['owner_id'])+'_'+str(attach['video']['id']))
                            #     #print(attach)
                            #     #print(video)
                            #     #video = video['items'][0]
                            #     video = attach['video']
                            #     #print('\n\n')
                            #     #print(video)
                            #     if video['platform'] == 'YouTube':
                            #         #if news['text'].find(video['files']['external'][12:]) == -1:
                            #         post_links += '<i>YouTube</i>: <a href="%s">%s</a>\n' % (video['files']['external'], video['title'])
    
                            #         max = sorted(attach['video']['image'], key=lambda x: x['width']*x['height'])[-1]
                                    
                            #         photo_attach = PhotoAttachment()
                            #         #photo_attach.url = [key for key in video.keys() if 'photo_' in key][-1]
                            #         photo_attach.url = max['url']
                                    
                            #         photo_attach.caption = video['files']['external']
    
                            #         previews.append(photo_attach)
    
                            for attach in news['attachments']:
                                if attach['type'] == 'photo':
                                    #max = attach['photo']['sizes'][-1]
                                    max = sorted(attach['photo']['sizes'], key=lambda x: x['width']*x['height'])[-1]
    
                                    photo_attach = PhotoAttachment()
                                    photo_attach.url = max['url']
                                    photo_attach.caption = attach['photo']['text']
    
                                    post.attachments.append(photo_attach)
    
                                if attach['type'] == 'doc':
                                    doc_attach = DocAttachment()
                                    doc_attach.url = attach['doc']['url']
                                    doc_attach.caption = attach['doc']['title']
    
                                    post.attachments.append(doc_attach)
    
                                # if attach['type'] == 'video':
                                #     video = vk_api('video.get', videos=str(attach['video']['owner_id'])+'_'+str(attach['video']['id']))
                                #     video = video['items'][0]
    
                                #     video_attach = VideoAttachment()
                                #     video_attach.url = list(video['files'].values())[-1]
                                #     #doc_attach.thumb_url = 
                                #     video_attach.caption = '<b>%s</b>\n\n%s' % (video['title'], video['description'])
    
                                #     post.attachments.append(video_attach)
    
                            post.attachments.extend(previews)
    
                        if len(news['text']) > 0:
                            post.text += '\n\n%s' % re.sub(r'\[\s*(\S+)\s*\|(.*?)\]', 
                                                           r'<a href="https://vk.com/\1">\2</a>', news['text'])
                        if len(post_links) > 0:
                            post.text += '\n\n%s' % post_links
    
                        posts.append(post)
                else:
                    break
        except e:
            print(e)
    if len(response['items']) != 0:
        last_id = response['items'][0]['post_id']+response['items'][0]['source_id']

    return posts
