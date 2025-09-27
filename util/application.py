# Change to anonymize data, for creating screenshots
ANONYMIZED = False


def get_application_name() -> str:
    if ANONYMIZED is True:
        return "Work in Progress"
    else:
        return "Forge of Empires Guild Tools"


application_data = {
    "name": get_application_name(),
    "version": "1.0.0",
    "anonymized": ANONYMIZED
}
