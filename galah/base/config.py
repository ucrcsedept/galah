import imp

def load_config(file, domain):
	loaded = imp.load_source("user_config_file", file)

	local_config = {}

	prefix = "%s/" % domain
	global_prefix = "global/"

	# Grab all the configuration values for the given domain, and any global
	# configuration values.
	for k, v in loaded.config.items():
		if k.startswith(prefix) and k != len(prefix):
			local_config[k[len(prefix):]] = v
		elif k.startswith(global_prefix) and k != len(global_prefix):
			local_config[k[len(global_prefix):]] = v

	return local_config