import json
def Settings(CorrectImageName = False):
    with open('settings.json', 'r') as f:
        settings = json.load(f)
        if CorrectImageName:
            imageName = settings["image_name"]
            imageName = imageName[:imageName.index('.')+1]+'png' \
            if imageName[imageName.index('.')+1:] != 'png' \
            else imageName
            settings["image_name"] == imageName
            print(imageName)
        return settings
def WriteSettings(settings):
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    