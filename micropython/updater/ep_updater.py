import uos
import urequests
import ujson
import machine

class updater:
    def __init__(self, github_user="eydam-prototyping", github_repo="tutorials_de",
                 github_path="micropython/updater", ignore_files=[".gitignore"]):
        self.github_user = github_user
        self.github_repo = github_repo
        self.github_path = github_path
        self.ignore_files = ignore_files
        self.github_url = "https://api.github.com/repos/%s/%s/contents/%s" % (github_user, github_repo, github_path)

    def _execute_update(self):
        for file in uos.listdir("next"):
            uos.rename("next/"+file, file)
        uos.rmdir("next")
        machine.reset()

    def _download_file(self, f):
        content = urequests.get(f["download_url"])
        if content.status_code == 200:
            if "next" not in uos.listdir():
                uos.mkdir("next")
            with open("next/" + f["name"], "w") as f:
                f.write(content.content)

    def _download_update(self):
        github_response = urequests.get(self.github_url, headers={"User-Agent": "esp32"})
        github_dir = ujson.loads(github_response.content)

        if "version.json" in uos.listdir():
            with open("version.json", "r") as f:
                version_info = ujson.load(f)
        else:
            version_info = {"files":{}}

        changed = False
        for f in github_dir:
            if f["name"] not in self.ignore_files:
                if f["name"] in version_info["files"]:
                    if f["sha"] != version_info["files"][f["name"]]["sha"]:
                        print("new version of %s found, starting download" % f["name"])
                        self._download_file(f)
                        changed = True
                        version_info["files"][f["name"]]["sha"] = f["sha"]
                else:
                    print("new file found %s, starting download" % f["name"])
                    self._download_file(f)
                    changed = True
                    version_info["files"][f["name"]] = {"sha": f["sha"]}

        if changed:
            with open("version.json", "w") as f:
                ujson.dump(version_info, f) 
                machine.reset()
        else:
            print("Everything up to date")

    def run(self):
        if "next" in uos.listdir():
            self._execute_update()
        else:
            self._download_update()