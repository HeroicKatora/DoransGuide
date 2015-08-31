import urllib3 as HTTP
import json
from itertools import product
from contextlib import ExitStack
import os
import certifi

regions = ['na']
items_path = "items/{region}/{version}/{lang}.json"
champ_path = "champions/{region}/{version}/{lang}.json"

def del_safe(item, *args):
	for arg in args:
		try:
			del item[arg]
		except KeyError:
			pass

if __name__ == "__main__":
	api_key = input("Api key: ")
	pool = HTTP.PoolManager(10, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
	def request_raw(path, **args):
		parameters = dict(args, api_key = api_key)
		fullpath = '{path}?{para}'.format(path = path, para = '&'.join('{a}={b}'.format(a = x, b = parameters[x]) for x in parameters))
		print(fullpath)
		res = pool.request('GET', fullpath)
		if res.status != 200:
			print(res.status)
			return request_raw(path, **args)
		return res
	
	def request(path, **args):
		with request_raw(path, **args) as r:
			data = r.data.decode()
		return json.loads(data)

	for region in regions:
		versions = request('https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/versions'.format(region = region))
		languages = request('https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/languages'.format(region = region))
		for (version,) in product(versions):
			lang = 'en_US'
			ifile_p = items_path.format(region = region, version = version, lang = lang)
			cfile_p = champ_path.format(region = region, version = version, lang = lang)
			os.makedirs(os.path.dirname(ifile_p), exist_ok=True)
			os.makedirs(os.path.dirname(cfile_p), exist_ok=True)
			if not os.path.exists(ifile_p):
				with ExitStack() as stack:
					file_h = stack.enter_context(open(ifile_p, 'w'))
					req = request('https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/item'.format(region = region),
						locale = lang, version = version, itemListData="all")
					del_safe(req, 'basic', 'groups', 'tree', 'type')
					for itemId in req['data']:
						item = req['data'][itemId]
						del_safe(item, 'colloq', 'consumeOnFull', 'consumed', 'depth', 'effect', 'from', 'gold', 'group')
						del_safe(item, 'inStore', 'into', 'sanitizedDescription', 'specialRecipe', 'stacks', 'stats')
					json.dump(req, file_h)

			if not os.path.exists(cfile_p):
				with ExitStack() as stack:
					file_h = stack.enter_context(open(cfile_p, 'w'))
					req = request('https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/champion'.format(region = region),
						locale = lang, version = version, champData="all", dataById=True)
					del_safe(req, 'format', 'type', 'keys')
					for champId in req['data']:
						champ = req['data'][champId]
						del_safe(champ, 'allytips', 'blurb', 'enemytips', 'partype', 'passive')
						del_safe(champ, 'recommended', 'skins', 'spells', 'stats')
					json.dump(req, file_h)
