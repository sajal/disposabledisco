import config

APT_PACKAGES = config.BASE_PACKAGES
APT_PACKAGES += config.ADDITIONAL_PACKAGES

mastetinit = open("master-init.sh", "r").read()
mastetinit = mastetinit.replace("--PACKAGES--", " ".join(APT_PACKAGES))

PIP_REQUIREMENTS = config.PIP_REQUIREMENTS

pip = ""
for dep in PIP_REQUIREMENTS:
	pip += "pip install %s\n" %(dep)

mastetinit = mastetinit.replace("--PIP--", pip)


print mastetinit
