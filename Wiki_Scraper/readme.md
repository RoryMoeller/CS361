# Wikipedia Scraper
## Hyperlinks
|Links|
---|
[Usage](#basic-usage)|
[Options](#all-options)|
[Filters](#current-standard-filters-list)|
---
## Basic Usage

### CL-IO Version
 Supplying I/O from the commandline requires a `-o` and `-i` option. This is templated as:
```
python3 scraper.py -i [link to wikipedia page] -o [output file name]
```
#### An example CL IO script can be found [here](cltest.sh)
### Socket IPC Version
Supplying the I/O from a socket connection requires a specified port number. This is templated as:
```
python3 scraper.py -s [port number]
```
#### An example python3 socket IO script can be found [here](sockettest.py)
---
## All options
|Option|Effect|
---|---
`-s` [port] | Should run in socket mode & use the supplied port number
`-o` [output file] | Should run in CL_IO mode & use the supplied filename as the output destination.
`-i` [input URL] | Required when running in CL_IO mode. Uses the input url as the target
`-d` [delimiter] | Use the supplied delimiter to seperate the links.
`-e` [exclusion] | Do not include links in the response if they contain any exclusion. Can have multiple -e options.
`--URL_Format` ["Short"/"Full"] | Default is Full. Shortened URL format will factor out the prepended "http...wikipedia.org"
`--titles` | Appends a tab character and the title of the linked page after each link
`--std_filters` | Adds a set of common non-article pages to the exclusions list

---
## Current standard filters list
* 'wiki/Category:'
* 'wiki/Help:'
* 'wiki/Template'
* 'wiki/Wikipedia:'