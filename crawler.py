import os
import optparse
import time
from threading import Timer

import requests
import chardet
from BeautifulSoup import BeautifulSoup


class Crawler(object):
    def __init__(self, url, outfile):
        """
        :param url: url to Crawling
        :param outfile: Place output
        """
        self.url = url
        self.outfile = outfile

    def refresh(self):
        """
        refresh html and soup
        :return:
        """
        response = requests.get(self.url)
        self.encoding = chardet.detect(response.content).get('encoding')
        html = response.content.decode(self.encoding, 'ignore')
        self.soup = BeautifulSoup(html)
        self.directory = '%s/%s' % (self.outfile, time.strftime('%Y%m%d%H%M%S'))

    def do_request(tag):
        """
         Request source and change url to local.
        :param tag: tag to change, like 'img'.
        :return:
        """
        def decorator(fn):
            def wrapper(self, select, attr, path, *args, **kwargs):
                """
                :param select: attribute filter to tag, like {'src': True}.
                :param attr: attribute to change, this should be a URL.
                :param path: relative path to save source.
                :return:
                """
                tags = self.soup.findAll(tag, attrs=select)
                for tag_ in tags:
                    url = tag_[attr]
                    name = url.split('/')[-1].split('?')[0]
                    if not url.startswith('http'):  # some incomplete URL
                        url = 'http://%s' % url.split('//', 1)[-1]
                    source = requests.get(url).content
                    tag_[attr] = '%s/%s' % (path, name)
                    self.save(path=path, name=name, source=source)
            return wrapper
        return decorator

    @do_request('link')
    def css_parse(self):
        pass

    @do_request('img')
    def image_parse(self):
        pass

    @do_request('script')
    def js_parse(self):
        pass

    @do_request('iframe')
    def iframe_parse(self):
        pass

    def html_parse(self):
        self.save(path='', name='index.html', source=str(self.soup))

    def save(self, path, name, source):
        path_ = '%s/%s' % (self.directory, path)
        if not os.path.exists(path_):
            os.makedirs(path_)
        fp = open('%s/%s' % (path_, name), 'w')
        fp.write(source)
        fp.close()


def option_parser(parser):
    parser.add_option("-d", "--interval", dest="interval",
                      help="Interval of crawling the web")
    parser.add_option("-u", "--url", dest="url",
                      help="Url to crawler")
    parser.add_option("-o", "--outfile", dest="outfile",
                      help="Place output in file")


def timer(crawler, interval):
    """
    Repeat
    :param crawler:
    :param interval:
    :return:
    """
    t = Timer(int(interval), timer, (crawler, interval))
    t.start()
    crawler.refresh()
    crawler.css_parse({'type': 'text/css', 'href': True}, 'href', 'css')
    crawler.js_parse({'src': True}, 'src', 'js')
    crawler.image_parse({'src': True}, 'src', 'images')
    crawler.image_parse({'_src': True}, '_src', 'images')
    crawler.iframe_parse({'src': True}, 'src', 'iframe')
    crawler.html_parse()


def main():
    parser = optparse.OptionParser()
    option_parser(parser)
    (options, args) = parser.parse_args()
    crawler = Crawler(options.url, options.outfile)
    timer(crawler, options.interval)


if __name__ == '__main__':
    main()
