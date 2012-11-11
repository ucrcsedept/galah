import imp

# Default configuration values for Galah.
defaults = {
    "global/SUBMISSION_DIRECTORY": "/var/local/galah/web/submissions/",
    "global/MONGODB": "galah",
	"web/DEBUG": True,
    "web/SECRET_KEY": "Very Secure Key",
    "web/HOST_URL": "http://localhost:5000"
}

def load_config(file, domain):
	loaded = imp.load_source("user_config_file", file)

	local_config = {}

	# Note we make a **shallow** copy of the defaults here
	user_config = dict(defaults)
	user_config.update(loaded.config)

	# The prefix values we will look for when scanning the configuration file.
	prefix = "%s/" % domain
	global_prefix = "global/"

	# Grab all the configuration values for the given domain, and any global
	# configuration values.
	for k, v in user_config.items():
		if k.startswith(prefix) and k != len(prefix):
			local_config[k[len(prefix):]] = v
		elif k.startswith(global_prefix) and k != len(global_prefix):
			local_config[k[len(global_prefix):]] = v

	return local_config