#!/usr/bin/python3

class Log:
	@staticmethod
	def i(msg):
		print(msg)

	@staticmethod
	def e(msg):
		RED = '\033[91m'
		ENDC = '\033[0m'
		print(f"{RED}{msg}{ENDC}")

	@staticmethod
	def w(msg):
		YELLOW = '\033[93m'
		ENDC = '\033[0m'
		print(f"{YELLOW}{msg}{ENDC}")

	@staticmethod
	def accent(msg):
		BLUE = '\033[34m'
		ENDC = '\033[0m'
		print(f"{BLUE}{msg}{ENDC}")
