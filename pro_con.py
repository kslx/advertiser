from multiprocessing import Process,Queue
import time,random,os
from urllib.parse import urlparse
from advertiserExtractor.db.mysql import Mysql
from advertiserExtractor.download.spider import Spider
from advertiserExtractor.extractor.parser import Parser

m=Mysql()
s = Spider()
ids = [144018319]
def handle(url, html):
    parser = urlparse(url)
    hostname = parser.hostname
    extractor = Parser.create(url, html)
    item = extractor.parse(hostname, html)
    return item

def run(data):
    run_task(data)

def run_task(data):
    advertiserid = data[0]
    target_url = data[1]
    advertiser = data[2]
    # logger.info({'id': advertiserid})
    if target_url:
        html = s.fetch(target_url)
        item = handle(target_url, html)
        m.process(item)
        identifier = item['identifier']
        if identifier:
            id = m.get_id(identifier)
            if id:
                m.insert({'advertiserid': advertiserid, 'detailid': id, 'advertiser': advertiser})

def consumer(q):
    while True:
        data=q.get()
        run(data)

def producer(q):
    while True:
        if q.qsize()<100:
            id = ids.pop(0)
            datas = m.get_urls(id)
            id = datas[999][0]
            for data in datas:
                q.put(data)
            ids.append(id)

if __name__ == '__main__':
    q=Queue()
    p1=Process(target=producer,args=(q,))
    c1=Process(target=consumer,args=(q,))
    c2=Process(target=consumer,args=(q,))
    c3=Process(target=consumer,args=(q,))
    c4=Process(target=consumer,args=(q,))
    c1.daemon=True
    c2.daemon=True
    c3.daemon=True
    c4.daemon=True
    p_l=[p1,c1,c2,c3,c4]
    for p in p_l:
        p.start()
    p1.join()

