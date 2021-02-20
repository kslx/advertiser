from multiprocessing.pool import Pool
from threading import Thread
from urllib.parse import urlparse
from advertiserExtractor.db.mysql import Mysql
from advertiserExtractor.download.spider import Spider
from advertiserExtractor.extractor.extractor import Extractor
from advertiserExtractor.extractor.parser import Parser
import queue
import multiprocessing as mp
from advertiserExtractor.log.log import logger
import multiprocessing

m = Mysql()
s = Spider()
ids = [30000]


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

def run(q):
    data = q.get()
    run_task(data)


def run_task(data):
    advertiserid = data[0]
    target_url = data[1]
    advertiser = data[2]
    logger.info({'id': advertiserid})
    if target_url:
        html = s.fetch(target_url)
        item = handle(target_url, html)
        m.process(item)
        identifier = item['identifier']
        if identifier:
            id = m.get_id(identifier)
            if id:
                m.insert({'advertiserid': advertiserid, 'detailid': id, 'advertiser': advertiser})

def process_crawler(q):
    num_cpus = multiprocessing.cpu_count()
    print("Starting {} process".format(num_cpus))
    process = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=run,args=(q,))
        p.daemon = True
        p.start()
        process.append(p)
    for p in process:
        p.join()


if __name__ == '__main__':
    q = queue.Queue()
    id = ids.pop(0)
    datas = m.get_urls(id)
    id = datas[999][0]
    for data in datas:
        q.put(data)
    ids.append(id)
    print('size: %s'%(q.qsize()))
    process_crawler(q)



