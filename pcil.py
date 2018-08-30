from argparse import ArgumentParser
from urllib.request import urlretrieve
import sys
import os

parser = ArgumentParser()
parser.add_argument("-o", "--out", dest="path", default="pcil.h",
                    help="Path to output the header file", metavar="PATH")
parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                    default=False, help="don't print status messages to stdout")
parser.add_argument("-u", "--url", dest="url",
                    help="URL to request the ids database from", metavar="URL")
args = parser.parse_args()

vendors = list()


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

namespace pcil
{
    inline const char* deviceLookup(uint16_t vendorId, uint16_t deviceId)
    {
        uint32_t key = ((vendorId << 16) | (deviceId));
        switch(key)
        {
""")
        with open(os.path.join(os.path.dirname(__file__), "pci.ids"), "r", encoding="utf8") as pcifile:
            for line in pcifile:
                if line.startswith("C "):
                    break
                elif line.startswith("#") or line.isspace():
                    continue
                s = line.split("  ")
                if len(line) - len(line.lstrip('\t')) == 0:
                    vendorId = int(s[0], 16)
                    vendors.append([vendorId, s[1]])
                    continue
                elif len(line) - len(line.lstrip('\t')) == 1:
                    deviceId = int(s[0], 16)
                    key = ((vendorId << 16) | deviceId)
                    headerfile.write("            case {key}: return \"{name}\";\n".format(key=key, name=s[1].strip().replace("\\", "\\\\").replace("\"", "\\\"")))
        headerfile.write("""            default: return "Unrecognized Device";
        }
    }
    
    inline const char* vendorLookup(uint16_t vendorId)
    {
        switch(vendorId)
        {
""")
        for vendor in vendors:
            headerfile.write("            case {key}: return \"{name}\";\n".format(key=vendor[0], name=vendor[1].strip().replace("\\", "\\\\").replace("\"", "\\\"")))
        headerfile.write("""            default: return "Unrecognized Vendor";
        }
    }
}
#endif // PCIL_H
""")
    if not args.quiet:
        print("The header file is located at " + path.replace("\\", "/"))
