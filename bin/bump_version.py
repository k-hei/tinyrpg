from enum import Enum
import sys


class Increment(Enum):
	MAJOR = 'major'
	MINOR = 'minor'
	PATCH = 'patch'
	ITERATION = 'iteration'


def parse_version(version):
	return map(int, version[1:].split('.'))

def stringify_version(major, minor, patch, iteration):
	return f'v{major}.{minor}.{patch}.{str(iteration).zfill(3)}'

def bump_version(version, increment=Increment.MINOR):
	major, minor, patch, iteration = parse_version(version)

	if increment == Increment.MAJOR:
		major += 1
		minor = 0
		patch = 0

	elif increment == Increment.MINOR:
		minor += 1
		patch = 0

	elif increment == Increment.PATCH:
		patch += 1

	iteration += 1

	return stringify_version(major, minor, patch, iteration)


def main(increment):
	try:
		with open('VERSION', mode='r', encoding='utf-8') as version_file:
			version = version_file.read()
	except FileNotFoundError:
		print('VERSION file not found')
		return

	version_new = bump_version(version, increment)
	print(version_new)

	with open('VERSION', mode='w', encoding='utf-8') as version_file:
		version_file.write(version_new)


if __name__ == '__main__':
	increment = (Increment(sys.argv[1])
		if len(sys.argv) >= 2
		else Increment.MINOR)

	main(increment)
