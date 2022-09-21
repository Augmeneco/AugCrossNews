from typing import List

class Attachment:
    url: str

class PhotoAttachment(Attachment):
    caption: str
    
    def __init__(self):
        self.caption = ''

class DocAttachment(Attachment):
    caption: str
    
    def __init__(self):
        self.caption = ''

class VideoAttachment(Attachment):
    caption: str
    thumb_url: str

    def __init__(self):
        self.caption = ''

class Post:
    text: str = ''
    attachments: List[Attachment]
    timestamp: int
    url: str

    def __init__(self):
        self.attachments = list()
        self.text = str()
        self.url = None