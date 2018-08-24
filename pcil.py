from argparse import ArgumentParser
from urllib.request import urlretrieve
import sys
import os
import re

parser = ArgumentParser()
parser.add_argument("-g", "--gpu", action="store_true", dest="gpuonly",
                    default=False, help="only write gpu info to the header file")
parser.add_argument("-o", "--out", dest="path", default="pcil.h",
                    help="Path to output the header file", metavar="PATH")
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
    path = os.path.join(os.path.dirname(__file__), args.path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if args.url:
        if args.quiet:
            urlretrieve(args.url, 'pci.ids')
        else:
            print("Downloading id database from " + args.url)
            urlretrieve(args.url, 'pci.ids', reporthook)
            print("Download complete")
    with open(path, "w", encoding="utf8") as headerfile:
        headerfile.write("""#ifndef PCIL_H
#define PCIL_H
#include <map>

namespace pcil
{
    static const std::map<short, char*> names = {
""")
        with open(os.path.join(os.path.dirname(__file__), "pci.ids"), "r", encoding="utf8") as pcifile:
            lines = pcifile.readlines()
            last = lines[-1]
            i = 0
            for line in lines:
                if line.startswith("#") or line.isspace():
                    continue
                if line != last:
                    headerfile.write("        {{{id}, \"{name}\"}},\n".format(id=i, name=line.strip().replace("\\", "\\\\").replace("\"", "\\\"")))
                else:
                    headerfile.write("        {{{id}, \"{name}\"}}".format(id=i, name=line.strip().replace("\\", "\\\\").replace("\"", "\\\"")))
                i += 1
        headerfile.write("""
    };
    
    inline const char* lookup(short vendorId, short deviceId)
    {
        return names[vendorId];
    }
}
#endif // PCIL_H
""")
    if not args.quiet:
        print("The header file is located at " + path)
