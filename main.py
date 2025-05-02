from pathlib import Path
import requests
import json
import time
from tqdm import tqdm

# ユーザー指定
print("URLを入力してください。(ex:https://kemono.su/***/user/***)")
input_url = input()
print("データ収集中...")

service = input_url.split("/")[3]
creator_id = input_url.split("/")[5]

url = f"https://kemono.su/api/v1/{service}/user/{creator_id}/posts-legacy"
res = requests.get(url)
time.sleep(1)
res_json = res.json()
count = res_json["props"]["count"]


# json作成
posts_data = []
for i in range(0, count, 50):
    posts_url = (
        f"https://kemono.su/api/v1/{service}/user/{creator_id}/posts-legacy?o={i}"
    )
    posts_res = requests.get(posts_url)
    time.sleep(1)
    posts_json = posts_res.json()
    results = posts_json["results"]
    result_previews = posts_json["result_previews"]
    for index in range(len(results)):
        post_data = {}
        post_data["id"] = results[index]["id"]
        post_data["title"] = results[index]["title"].strip()
        post_data["files"] = []
        for content in result_previews[index]:
            post_data["files"].append(
                {
                    "name": content["name"],
                    "url": f"{content['server']}/data{content['path']}",
                }
            )
        posts_data.append(post_data)

# ディレクトリ作成
profile_name = res_json["props"]["name"].strip()
profile_service = res_json["props"]["service"]
profile_id = res_json["props"]["id"]
profile_dir = f"download/{profile_name}-{profile_service}-{profile_id}"
Path(f"{profile_dir}").mkdir(exist_ok=True, parents=True)
print(profile_name)

with open(f"{profile_dir}/posts_data.json", "w", encoding="utf-8") as f:
    json.dump(posts_data, f, indent=2, ensure_ascii=False)


# ファイル保存
for post_data in tqdm(posts_data, desc="[total]"):
    dir_id = post_data["id"]
    dir_name = post_data["title"]
    dir_path = f"{profile_dir}/{dir_id} - {dir_name}"
    Path(dir_path).mkdir(exist_ok=True, parents=True)
    time.sleep(3)
    for i, file_data in enumerate(tqdm(post_data["files"], leave=False, desc="[post]")):
        file_name = file_data["name"]
        file_url = file_data["url"]
        file_res = requests.get(file_url)
        file_path = Path(f"{dir_path}/{i}-{file_name}")
        file_path.write_bytes(file_res.content)
        time.sleep(2)
