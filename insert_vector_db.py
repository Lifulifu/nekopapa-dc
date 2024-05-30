from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai_api import embed
import os


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
    client = QdrantClient(url="http://localhost:6333")
    points = []
    for i, filename in enumerate(os.listdir(path)):
        image_path = os.path.join(path, filename)
        description = remove_filename_extension(filename)
        image_vector = embed(description)
        points.append(
            PointStruct(
                id=i,
                vector=image_vector,
                payload={
                    'filename': image_path,
                    'description': description,
                })
        )
        print(i, description)

    operation_info = client.upsert(
        collection_name="images",
        wait=True,
        points=points,
    )
    print(operation_info)


if __name__ == '__main__':
    delete_collection('images')
    create_collection('images')
    add_images('images')