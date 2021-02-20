from urllib.parse import urlparse
from advertiserExtractor.db.mysql import Mysql
from advertiserExtractor.download.spider import Spider
from advertiserExtractor.extractor.extractor import Extractor
from advertiserExtractor.extractor.parser import Parser
import queue

from advertiserExtractor.log.log import logger

m = Mysql()
q = queue.Queue()
s=Spider()
ids=[30000]
def handle(url, html):
    parser = urlparse(url)
    hostname = parser.hostname
    extractor = Parser.create(url, html)
    item = extractor.parse(hostname, html)
    return item

def start():
   id = ids.pop(0)
   datas = m.get_urls(id)
   id = datas[999][0]
   for data in datas:
        q.put(data)
   ids.append(id)

def run():
     while True:
        if q.qsize()<100:
                start()
        else:
            data = q.get()
            run_task(data)

def log(id):
    logger.info({'id':id})

def run_task(data):
    advertiserid = data[0]
    target_url = data[1]
    advertiser = data[2]
    logger.info({'id':advertiserid})
    if target_url:
        html = s.fetch(target_url)
        item = handle(target_url, html)
        m.process(item)
        identifier = item['identifier']
        if identifier:
            id = m.get_id(identifier)
            if id:
                m.insert({'advertiserid': advertiserid, 'detailid': id, 'advertiser': advertiser})

# if __name__=='__main__':
#      run()
def ckeck_queue():
    if q.qsize()<100:
        start()


def checkDataThread(client):
    detect = DetectData(client)
    thr = Thread(target=detect.check, args=())
    thr.start()



if __name__ == '__main__':
    start_page = 1
    end_page = 3000

    # 多进程抓取
    pages = [i for i in range(start_page, end_page)]
    p = mp.Pool()
    p.map_async(func, pages)
    p.close()
    p.join()

