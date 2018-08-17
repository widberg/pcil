from argparse import ArgumentParser
from urllib.request import urlretrieve
import sys

parser = ArgumentParser()
parser.add_argument("-g", "--gpuonly", action="store_true", dest="gpuonly",
                    default=False, help="only write gpu info to the header file")
parser.add_argument("-p", "--path", dest="path", default="pcil.h",
                    help="PATH to output the header file", metavar="PATH")
parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                    default=False, help="don't print status messages to stdout")
parser.add_argument("-u", "--url", dest="url",
                    help="URL to request the ids database from", metavar="URL")
args = parser.parse_args()


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else:  # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))


if __name__ == '__main__':
    if args.download:
        if args.quiet:
            urlretrieve(args.download, 'pci.ids')
        else:
            print("Downloading id database from " + args.download)
            urlretrieve(args.download, 'pci.ids', reporthook)
            print("Download complete")
