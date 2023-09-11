from plemmy import LemmyHttp
from python_dotenv import load_dotenv
from os import getenv
from plemmy.responses import GetFederatedInstancesResponse, GetPostsResponse
from time import sleep


load_dotenv()

lemmy = LemmyHttp(getenv("LEMMY_URL"))
lemmy.login(getenv("LEMMY_USERNAME"), getenv("LEMMY_PASSWORD"))

dryrun = getenv("DRYRUN") == "true"

software = getenv("SOFTWARE_TO_REMOVE", False)
if not software:
    print("No software to remove")
    exit(0)

software = software.split(",")

def main():
    instances = GetFederatedInstancesResponse(lemmy.get_federated_instances())
    found_instances = []
    for instance in instances.federated_instances.allowed:
        if instance.name in software:
            found_instances.append(instance)
        
    for instance in instances.federated_instances.blocked:
        if instance.name in software:
            found_instances.append(instance)

    for instance in instances.federated_instances.linked:
        if instance.software in software:
            found_instances.append(instance.id)
    
    i = 1
    data = GetPostsResponse(lemmy.get_posts(page=i, sort="new"))
    while len(data.posts) > 0 and i < getenv("PAGES", 100):
        data = GetPostsResponse(lemmy.get_posts(page=i, sort="new"))
        for post in data.posts:
            if not post.community.local and post.community.instance_id in found_instances:
                if(dryrun):
                    print(f"Would delete post {post.id} in community {post.community.name}")
                else:
                    print(f"Deleting post {post.id} in community {post.community.name}")
                    lemmy.delete_post(True, post.id)
        i += 1
        sleep(2)
