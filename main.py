import random
import json
import string
from tqdm import tqdm
import requests

def generate_random_movie_data():
    movie_id = random.randint(1, 1000000000)
    title = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(5, 20)))
    overview = ''.join(random.choice(string.ascii_letters + string.whitespace) for _ in range(random.randint(50, 300)))
    genres = random.sample(["Drama", "Crime", "Comedy", "Action", "Adventure", "Sci-Fi"], random.randint(1, 3))
    release_date = random.randint(315532800, 1672531199)  # From 1980-01-01 to 2022-12-31

    return {
        "id": movie_id,
        "title": title,
        "overview": overview,
        "genres": genres,
        "release_date": release_date
    }

target_size_mb = 100
bytes_per_record = len(json.dumps(generate_random_movie_data()))
target_size_bytes = target_size_mb * (1024 ** 2)  # 1 MB = 1024^2 bytes
num_records = target_size_bytes // bytes_per_record
bearer_master_key = "testEnv"

total_expected_time = num_records  # Assuming 1 record per second

for i in range(900):
    output_filename = f"output_{i + 1}.json"

    with open(output_filename, 'w') as f:
        f.write('[\n')
        for idx in tqdm(range(num_records)):
            movie_data = generate_random_movie_data()
            json.dump(movie_data, f)
            if idx != num_records - 1:
                f.write(',\n')
            else:
                f.write('\n')
        f.write(']')

    # Make the POST request
    url = 'http://localhost:7700/indexes/populate-test/documents?primaryKey=id'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + bearer_master_key
    }
    datas = open(output_filename, 'rb').read()
    response = requests.post(url, headers=headers, data=datas)

    if response.status_code == 202:
        print(f"File {i + 1} uploaded successfully.")
    else:
        print(f"Error uploading file {i + 1}. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
