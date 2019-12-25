#! /usr/bin/env python3

from time import time, sleep
import Get_Servers as gs
import threading


class Timer:
	def __init__(self):
		self.start = time()

	def reset(self):
		self.start = time()

	def time_passed(self):
		return time() - self.start

p = False

def __update():
	global p
	if not p:
		p = True
		print('update_thread started')
		gs.update_servers()
		gs.create_ovpn_files(10)
		print('thread finished')
		p = False


def updater_thread():
	global p
	if not p:
		thr = threading.Thread(target= __update)
		thr.start()

class vpn_hosts_manager:	
	def __init__(self):
		print('started server')
		updater_thread()
		self.timer = Timer()
		
	def hosts_updater(self):
		while True:		
			if self.timer.time_passed() / 3600 >= 1:
				self.timer.reset()
				updater_thread()
			sleep(0.1)
		
h_mgr = vpn_hosts_manager()
h_mgr.hosts_updater()