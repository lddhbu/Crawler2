import os
import optparse
import time

import requests
from BeautifulSoup import BeautifulSoup


class Crawler(object):
    def __init__(self, url, outfile):
        """
        :param url: url to Crawling
        """
        html = requests.get(url).content.decode('utf-8')
        self.soup = BeautifulSoup(html)
        self.outfile = outfile

    def do_request(tag, select, attr, path):
        def decorator(fn):
            def wrapper(self, *args, **kwargs):
                tags = self.soup.findAll(tag, attrs=select)
                for tag_ in tags:
                    url = tag_[attr]
                    name = url.split('/')[-1].split('?')[0]
                    source = requests.get(url).content
                    tag_[attr] = '%s/%s' % (path, name)
                    self.save(path=path, name=name, source=source)
            return wrapper
        return decorator

    @do_request('link', {'type': 'text/css', 'href': True}, 'href', 'css')
    def css_parse(self,):
        pass

    @do_request('img', {'src': True}, 'src', 'images')
    def image_parse(self):
        pass

    @do_request('script', {'src': True}, 'src', 'js')
    def js_parse(self):
        pass

    def html_parse(self):
        self.save(path='', name='index.html', source=str(self.soup))

    def save(self, path, name, source):
        path_ = '%s/%s/%s' % (self.outfile, time.strftime('%Y%m%d%H%M%S'), path)
        if not os.path.exists(path_):
            os.makedirs(path_)
        fp = open('%s/%s' % (path_, name), 'w')
        fp.write(source)
        fp.close()


def option_parser(parser):
    parser.add_option("-d", "--time", dest="time",
        help="Period of time")
    parser.add_option("-u", "--url", dest="url",
        help="Url to crawler")
    parser.add_option("-o", "--outfile", dest="outfile",
        help="Place output in file")


def main():
    parser = optparse.OptionParser()
    option_parser(parser)
    (options, args) = parser.parse_args()
    crawler = Crawler(options.url, options.outfile)
    crawler.css_parse()
    crawler.image_parse()
    crawler.html_parse()


if __name__ == '__main__':
    main()
