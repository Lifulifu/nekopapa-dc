from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai_api import embed
import os
import uuid
from tqdm import tqdm


def remove_filename_extension(filename: str):
    return os.path.splitext(filename)[0]


def create_collection(name: str):
    client = QdrantClient(url="http://localhost:6333")
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=1536, distance=Distance.DOT),
    )


def delete_collection(name: str):
    client = QdrantClient(url="http://localhost:6333")
    client.delete_collection(collection_name=name)


def add_images(path: str):
    with open(os.path.join(path, 'embedded.txt'), 'r') as f:
        embedded_filenames = f.readlines()
    embedded_filenames = set([x.strip() for x in embedded_filenames])

    client = QdrantClient(url="http://localhost:6333")
    points = []
    for filename in tqdm(os.listdir(path)):
        if filename.endswith('.txt'): continue
        if filename in embedded_filenames: continue

        description = remove_filename_extension(filename)
        image_vector = embed(description)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=image_vector,
                payload={
                    'filename': filename,
                    'description': description,
                })
        )
        embedded_filenames.add(filename)

    operation_info = client.upsert(
        collection_name="images",
        wait=True,
        points=points,
    )
    print(operation_info)

    with open(os.path.join(path, 'embedded.txt'), 'w') as f:
        f.write('\n'.join(embedded_filenames))


if __name__ == '__main__':
    # delete_collection('images')
    # create_collection('images')
    add_images('images')