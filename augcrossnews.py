import requests as req
import json
import time
from objects import *
from utils import *

import vk

def make_object(obj, url=None):
    obj['chat_id'] = CONFIG['target_channel']
    obj['parse_mode'] = 'HTML'
    obj['disable_web_page_preview'] = True
    if url != None:
        obj['reply_markup'] = json.dumps({
            'inline_keyboard':[[{
                'text': 'Открыть пост', 
                'url': url
            }]]
        })
    return obj

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def main():
    while True:
        try:
            log_print('Получаю новости...')
            posts = list()
            posts += vk.get_news()
    
            if len(posts) > 0:
                log_print('Новости получены. Начинаю постинг...')
                for post in posts:
                    # Only text
                    if len(post.attachments) == 0:
                        for is_last_element, chunk in signal_last(chunks(post.text, 4096)):
                            body = {
                                'text': chunk
                            }
                            tg_api('sendMessage', make_object(body, post.url) if is_last_element else make_object(body))
    
                    # Text length less 1024 and one attachment
                    elif (len(post.text) <= 1024) and (len(post.attachments) == 1):
                        if isinstance(post.attachments[0], PhotoAttachment):
                            body = {
                                'photo': post.attachments[0].url,
                                'caption': post.text
                            }
                            tg_api('sendPhoto', make_object(body, post.url))
    
                        if isinstance(post.attachments[0], VideoAttachment):
                            body = {
                                'video': post.attachments[0].url,
                                'supports_streaming': True,
                                'caption': post.text
                            }
                            tg_api('sendVideo', make_object(body, post.url))
    
                        if isinstance(post.attachments[0], DocAttachment):
                            body = {
                                'document': post.attachments[0].url,
                                'caption': post.text
                            }
                            tg_api('sendDocument', make_object(body, post.url))
    
                    # Text length more then 1024 or attachments more then one
                    elif (len(post.text) > 1024) or (len(post.attachments) > 1):
                        for group in chunks(post.attachments, 10):
                            attachments = list()
                            for attach in group:
                                if isinstance(attach, PhotoAttachment):
                                    InputMediaPhoto = {
                                        'type': 'photo',
                                        'media': attach.url,
                                        'caption': attach.caption,
                                        'parse_mode': 'HTML'
                                    }
                                    attachments.append(InputMediaPhoto)
    
                                if isinstance(attach, VideoAttachment):
                                    InputMediaPhoto = {
                                        'type': 'video',
                                        'media': attach.url,
                                        'caption': attach.caption,
                                        'supports_streaming': True,
                                        'parse_mode': 'HTML'
                                    }
                                    attachments.append(InputMediaPhoto)
    
                                if isinstance(attach, DocAttachment):
                                    body = {
                                        'document': attach.url,
                                        'caption': attach.caption
                                    }
                                    tg_api('sendDocument', make_object(body))
    
                            body = {
                                'media': json.dumps(attachments)
                            }
                            tg_api('sendMediaGroup', make_object(body, post.url))
                        
                        for is_last_element, chunk in signal_last(chunks(post.text, 4096)):
                            body = {
                                'text': chunk
                            }
                            tg_api('sendMessage', make_object(body, post.url) if is_last_element else make_object(body))
                    
                    time.sleep(1)
                
                log_print('Постинг закончен.')
            else:
                log_print('Новых постов нет.')
        except e:
            print(e)
        time.sleep(CONFIG['cooldown'])


if __name__ == "__main__":
    main()
