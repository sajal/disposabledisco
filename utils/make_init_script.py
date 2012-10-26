

def make_init_script(config, script):
    APT_PACKAGES = config.get("BASE_PACKAGES", [])
    APT_PACKAGES += config.get("ADDITIONAL_PACKAGES", [])

    script = script.replace("--PACKAGES--", " ".join(APT_PACKAGES))

    PIP_REQUIREMENTS = config.get("PIP_REQUIREMENTS", [])

    pip = ""
    for dep in PIP_REQUIREMENTS:
        pip += "pip install %s\n" %(dep)

    script = script.replace("--PIP--", pip)
    script = script.replace("--PUBKEY--", config.get("MGMT_KEY"))
    return script