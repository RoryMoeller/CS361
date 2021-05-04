# Wikipedia Scraper
## Hyperlinks
|Links|
---|
[Usage](#basic-usage)|
[Common Options](#Common-options)|
[Filters](#current-standard-filters-list)|
[Other usage](#Other-usage)|
---
## Basic Usage

### CL-IO Version
 Supplying I/O from the commandline requires a `-o` and `-i` option. This is templated as:
```
python3 scraper.py -i [link to wikipedia page] -o [output file name]
```
#### An example CL IO script can be found [here](cltest.sh)
---
### HTTP Req IPC Version
Supplying the I/O from a HTTP connection requires a specified port number. This is templated as:
```
python3 scraper.py -s [port number]
```
#### Do NOT supply the script with an exposed port.
#### An example python3 HTTP IO script can be found [here](httpreq.py).
---
## Common options
|Option|Effect|
---|---
`-s` [port] | Should run in HTTP IO mode & use the supplied port number
`-o` [output file] | Should run in CL_IO mode & use the supplied filename as the output destination.
`-i` [input URL] | Required when running in CL_IO mode. Uses the input url as the target
`-d` [delimiter] | Use the supplied delimiter to separate the links.
`-e` [exclusion] | Do not include links in the response if they contain any exclusion. Can have multiple -e options.
`--require` [required substring] | Discard results that do not contain the substring in their attributes. Can have multiple --require options.
`--URL_Format` ["Short"/"Full"] | Default is Full. Shortened URL format will factor out the prepended "http...wikipedia.org"
`--titles` | Appends a tab character and the title of the linked page after each link
`--std_filters` | Adds a set of common non-article pages to the exclusions list

---
## Current standard filters list
* 'wiki/Category:'
* 'wiki/Help:'
* 'wiki/Template'
* 'wiki/Wikipedia:'
---
## Other usage
Additional options are added for extended functionality
|Option|Effect|
---|---
`--other_target` [tag,attribute] | Scrape for the content of "attribute" from "tag"
`--save_image` [subdirectory] | If scraping for image links, save scraped images to "subdirectory"
### Non anchor-href targets
This service can also be used to scrape non-anchor tags and non-href attributes by using `--other_target` and supplying the new target tag and attribute pair to scrape for. Note regarding this use case:
> This can break the output formatting when used with other options. A warning will be issued when this is expected. Specifically, `--title` and `--URL_Format` are likely to be affected.
### Downloading images
This service can also download images to a subdirectory of where the service is run from using the `--save_image` option. These images will not be communicated through either `-s`'s HTTP I/O or `-o`'s output file.

This example uses both non-anchor/href targets & downloading images. 
```
python3 scraper.py -s 15000 --require .png --other_target img,src
```
