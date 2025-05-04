from pathlib import Path
import requests
import json
import time
from tqdm import tqdm


# API接続
def access_api(input_url: str, index: int = 0) -> dict:
    service = input_url.split("/")[3]
    creator_id = input_url.split("/")[5]
    api_url = (
        f"https://kemono.su/api/v1/{service}/user/{creator_id}/posts-legacy?o={index}"
    )
    try:
        res = requests.get(api_url)
        res.raise_for_status()
        time.sleep(1)
        res_json = res.json()
    except requests.exceptions.RequestException as e:
        print("API通信エラー：", e)
    return res_json


# ディレクトリ作成
def make_dir(artist_data: dict) -> str:
    artist_name = artist_data["props"]["name"].strip()
    artist_service = artist_data["props"]["service"]
    artist_id = artist_data["props"]["id"]
    artist_dir = f"download/{artist_name}-{artist_service}-{artist_id}"
    Path(f"{artist_dir}").mkdir(exist_ok=True, parents=True)
    return artist_dir


# ファイルリスト作成
def make_file_list(input_url: str, posts_count: int, artist_dir: str) -> list[dict]:
    posts_data = []
    for i in range(0, posts_count, 50):
        posts_json = access_api(input_url, i)

        results = posts_json["results"]
        result_previews = posts_json["result_previews"]
        result_attachments = posts_json["result_attachments"]

        for index in range(len(results)):
            post_data = {
                "id": results[index]["id"],
                "title": results[index]["title"].strip(),
                "published": results[index]["published"],
                "files": [],
            }

            for content in result_previews[index]:
                post_data["files"].append(
                    {
                        "name": content["name"],
                        "url": f"{content['server']}/data{content['path']}",
                    }
                )
            for content in result_attachments[index]:
                post_data["files"].append(
                    {
                        "name": content["name"],
                        "url": f"{content['server']}/data{content['path']}",
                    }
                )

            posts_data.append(post_data)

    with open(f"{artist_dir}/posts_data.json", "w", encoding="utf-8") as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)

    return posts_data


# ファイル保存
def save_file(posts_data: list[dict], artist_dir: str) -> None:
    for post_data in tqdm(posts_data, desc="[total]"):
        dir_id = post_data["id"]
        dir_name = post_data["title"]
        dir_path = Path(f"{artist_dir}/{dir_id} - {dir_name}")
        if not (dir_path.exists()):
            Path(dir_path).mkdir(exist_ok=True, parents=True)
            time.sleep(3)
        for i, file_data in enumerate(
            tqdm(post_data["files"], leave=False, desc="[post]")
        ):
            file_name = file_data["name"]
            file_url = file_data["url"]
            file_path = Path(f"{dir_path}/{i}-{file_name}")
            if not (file_path.exists()):
                try:
                    with requests.get(file_url, stream=True) as r:
                        r.raise_for_status()
                        with open(file_path, "wb") as f:
                            for chunk in tqdm(
                                r.iter_content(chunk_size=1024 * 1024),
                                leave=False,
                                desc="[file]",
                            ):
                                f.write(chunk)
                    time.sleep(2)
                except requests.exceptions.RequestException as e:
                    print("ファイルアクセスエラー：", e)
