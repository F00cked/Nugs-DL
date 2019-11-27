# Nugs-DL
Tool written in Python to download streamable tracks from nugs.net. 

![](https://orion.feralhosting.com/sorrow/ngs.png)

# Setup
## Mandatory ##
The following field values need to be inputted into the config file:
- email
- password - in plain text
- quality - quality track to fetch from API. 1: AAC 150, 2: FLAC, 3: ALAC, 4: 24-bit MQA / best.

Nugs-DL may also be used via CLI.    

```
usage: Nugs-DL.py [-h] -u URL [-q {1,2,3,4}]

Sorrow446.

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL or text file filename.
  -q {1,2,3,4}, --quality {1,2,3,4}
                        1: AAC 150, 2: FLAC, 3: ALAC, 4: MQA.
  ```

**You can't download ANY tracks with a free account.**

# Update Log #
### 5th July 19 - Release 1 ###
### 27th Nov 19 - Release 2 ###
Complete rewrite
- Hi-res MQA support
- CLI support
- Download from text file support

If you need to get in touch: Sorrow#5631, [Reddit](https://www.reddit.com/user/Sorrow446)

# Disclaimer
I will not be responsible for how you use Nugs-DL.    
Nugs brand and name is the registered trademark of its respective owner.    
Nugs-DL has no partnership, sponsorship or endorsement with Nugs.    
