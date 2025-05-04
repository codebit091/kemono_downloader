from func import access_api, make_file_list, make_dir, save_file


def main():
    # ユーザー指定
    print("URLを入力してください。(ex:https://kemono.su/***/user/***)")
    input_url = input()
    print("データ収集中...")

    artist_data = access_api(input_url)
    artist_dir = make_dir(artist_data)
    posts_count = artist_data["props"]["count"]
    posts_data = make_file_list(input_url, posts_count, artist_dir)

    print(f'Artist : {artist_data["props"]["name"].strip()}')

    save_file(posts_data, artist_dir)


if __name__ == "__main__":
    main()
