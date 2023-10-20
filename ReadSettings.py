import json
def Settings(CorrectImageName = False):
    with open('settings.json', 'r') as f:
        settings = json.load(f)
        if CorrectImageName:
            imageName = settings["ImageName"]
            imageName = imageName[:imageName.index('.')+1]+'png' \
            if imageName[imageName.index('.')+1:] != 'png' \
            else imageName
            settings["ImageName"] == imageName
            print(imageName)
        return settings
    