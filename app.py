from flask import Flask, render_template, request
from zipfile import ZipFile
from bs4 import BeautifulSoup
import tempfile, os

app = Flask(__name__, template_folder="templates", static_folder="static")

def extract_usernames(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        t, h = a.text.strip(), a["href"]
        if "/_u/" in h:
            out.append(h.split("/_u/")[-1].strip("/"))
        elif "instagram.com/" in h:
            out.append(h.split("instagram.com/")[-1].strip("/"))
        elif t:
            out.append(t)
    return list(dict.fromkeys(out))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("zipfile")
        if not file:
            return render_template("index.html", error="ZIP dosyası yüklenmedi.")
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "data.zip")
        file.save(path)
        with ZipFile(path, "r") as z:
            z.extractall(tmp)
        followers_html = following_html = None
        for root, _, files in os.walk(tmp):
            for f in files:
                if "followers_1.html" in f:
                    followers_html = os.path.join(root, f)
                elif "following.html" in f:
                    following_html = os.path.join(root, f)
        if not followers_html or not following_html:
            return render_template("index.html", error="ZIP içinde gerekli dosyalar bulunamadı.")
        followers = extract_usernames(followers_html)
        following = extract_usernames(following_html)
        not_following_back = [u for u in following if u not in followers]
        return render_template("index.html", result=not_following_back)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

