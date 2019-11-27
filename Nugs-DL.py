import os
import re
import sys
import json
import time
import platform
import argparse
import traceback

import nugspy
import requests
from tqdm import tqdm
from mutagen import File
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

client = nugspy.Client()

def print_title():
	print("""
 _____                 ____  __    
|   | |_ _ ___ ___ ___|    \|  |   
| | | | | | . |_ -|___|  |  |  |__ 
|_|___|___|_  |___|   |____/|_____|
          |___|                    
   """)
   
def get_os():
	if platform.system() == 'Windows':
		return True
	else:
		return False 
   
def os_cmds(arg):
	if get_os():
		if arg == "c":
			os.system('cls')
		elif arg == "t":
			os.system('title Nugs-DL R2 (by Sorrow446)')
	else:
		if arg == "c":
			os.system('clear')
		elif arg == 't':
			sys.stdout.write('\x1b]2;Nugs-DL R2 (by Sorrow446)\x07')

def parse_args(qual):
	parser = argparse.ArgumentParser(
		description='Sorrow446.')
	parser.add_argument(
		'-u', '--url',
		help="URL or text file filename.",
		required=True)
	parser.add_argument(
		'-q', '--quality',
		choices=[1, 2, 3, 4],
		type=int,
		help="1: AAC 150, 2: FLAC, 3: ALAC, 4: MQA.",
		default=qual)
	args = parser.parse_args()
	return args.url.strip(), args.quality

def parse_cfg():
	with open('config.json') as f:
		cfg = json.load(f)
	return cfg.values()

def dir_setup(dir):
	if not os.path.isdir(dir):
		os.makedirs(dir)

def check_url(in_url):
	mat = re.match(r'http[s]?://play\.nugs\.net/#/catalog/recording/([0-9]+/?$)', in_url)
	if mat:
		return True, mat.group(1)
	else:
		return False, None

def sanitize(f):
	if get_os():
		return re.sub(r'[\\/:*?"><|]', '-', f)
	else:
		return re.sub('/', '-', f)	
		
def mqa_check(meta):
	for product in meta['products']:
		if product['formatStr'] == "MQA":
			return True
	return False

def exist_check(f, delete):
	if os.path.isfile(f):
		if delete:
			os.remove(f)
		return True
	return False	

def download(url, title, cur, tot, qual, pre):
	if not qual:
		spec = "AAC 150"
	elif qual == 1:
		spec = "16-bit / 44.1kHz FLAC"
	elif qual == 2:
		spec = "16-bit / 44.1kHz ALAC"
	elif qual == 4:
		spec = "24-bit MQA"
	print("Downloading track {} of {}: {} - {}".format(cur, tot, title, spec))
	r = requests.get(url, stream=True, headers={
		'Range':'bytes=0-',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; '
			'rv:67.0) Gecko/20100101 Firefox/67.0',
		'Referer': 'https://play.nugs.net/'
		}
	)
	r.raise_for_status()
	size = int(r.headers.get('content-length', 0))
	with open(pre, 'wb') as f:
		with tqdm(total=size, unit='B',
			unit_scale=True, unit_divisor=1024,
			initial=0, miniters=1) as bar:		
				for chunk in r.iter_content(32*1024):
					if chunk:
						f.write(chunk)
						bar.update(len(chunk))

def write_tags(f, title, cur, tot, ext):
	if ext == ".flac":
		audio = FLAC(f)
		audio['album'] = title
		audio['tracktotal'] = str(tot)
	else:
		audio = MP4(f)
		audio["\xa9alb"] = title
		audio["trkn"] = [(cur, tot)]
	audio.save()
	
def main(qual, album_id):
	dir_setup("Nugs-DL downloads")
	meta = client.get_album_meta(album_id)
	if qual != 4:
		qual -= 1
	if qual == 0:
		qual = None	
	if qual in [1, 3]:
		ext = ".flac"
	else:
		ext = ".m4a"
	album_artist = meta['artistName']
	try:
		album_title = meta['venue'].rstrip() + " (" + meta['performanceDate'] + ")"
	except AttributeError:
		album_title = meta['containerInfo']
	folder = album_artist + " - " + album_title
	folder_s = os.path.join("Nugs-DL downloads", sanitize(folder))
	dir_setup(folder_s)
	cur = 0
	tot = len(meta['tracks'])
	print(folder)
	for track in meta['tracks']:
		cur += 1
		title = track['songTitle']
		url = client.get_track_url(track['trackID'], qual)
		if not url:
			print("The API didn't return a track URL. Skipped.")
			continue		
		elif qual == 3 and not "mqa24/" in url:
			qual = 1
		post = os.path.join(folder_s, sanitize(str(cur) + ". " + title + ext))	
		if exist_check(post, False):
			print("Track already exists locally. Skipped")
			return
		pre = os.path.join(folder_s, str(cur) + ".nugs-dl_download")
		exist_check(pre, True)
		download(url, title, cur, tot, qual, pre)
		write_tags(pre, album_title, cur, tot, ext)
		try:
			os.rename(pre, post)
		except OSError:
			print("Failed to rename track.")
	
if __name__ == '__main__':
	try:
		os_cmds('t')
		print_title()
		cli = False
		email, pwd, qual = parse_cfg()
		client.auth(email, pwd)
		label = client.get_sub_info()
		print("Signed in successfully - " + label + " account.")
		while True:
			try:
				if sys.argv[1]:
					cli = True
					in_url, qual = parse_args(qual)
					if in_url.endswith('.txt'):
						if not exist_check(in_url, False):
							print("")
							print("The specified text file doesn't exist.")
							sys.exit(1)
						cur = 0	
						with open(in_url) as f:
							tot = len([line for line in f])
							f.seek(0)
							for in_url in f:
								cur += 1
								print("")
								print("Album {} of {}:".format(cur, tot))
								valid_url, album_id = check_url(in_url)	
								if not valid_url:
									print("Invalid URL. Skipped")
									continue
								main(qual, album_id)
							sys.exit()
			except IndexError:
				print("")
				in_url = input("Input URL: ").strip()
				print("")
			if not in_url:
				os_cmds('c')				
				print_title()
				continue
			valid_url, album_id = check_url(in_url)
			if not valid_url:
				if cli:
					print("")
				print("Invalid URL.")
				if cli:
					sys.exit(1)
				time.sleep(1)
				os_cmds('c')
				print_title()
				continue				
			main(qual, album_id)
			if cli:
				sys.exit()
			time.sleep(1)
			os_cmds('c')
			print_title()
		
	except (KeyboardInterrupt, SystemExit):
		sys.exit()
	except:
		traceback.print_exc()
		input('\nAn exception has occurred. Press enter to exit.')
		sys.exit()
