build_docker_image_local :
	docker build -t energy:$(DOCKER_TAG) .

build_docker_image_live :
	docker build -t $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(VERSION) .

run_api_local_test :
	uvicorn api.fast:app --host 0.0.0.0 --port $(MY_PORT) --reload

docker_run_interactive :
	docker run -it --env-file .env energy:$(DOCKER_TAG) sh

#laptop_port : container_port
run_api_from_container :
	docker run -it --env-file .env -p $(MY_PORT):$(PORT) energy:$(DOCKER_TAG)

stop_running_containers:
	docker ps -a -q | xargs -r docker stop | xargs -r docker rm

#**FOR USE WITHIN CONTAINER!**
run_cmd :
	uvicorn api.fast:app --host 0.0.0.0 --port $(PORT)

all :
	docker build -t energy:$(DOCKER_TAG) .
	echo "open http://127.0.0.1:$(MY_PORT)/test in browser to see"
	docker run --env-file .env -p $(MY_PORT):$(PORT) energy:$(DOCKER_TAG)
# $(BROWSER) http://127.0.0.1:8020/test

#	create repo
deploy_create_repo :
	gcloud artifacts repositories create $(DOCKER_REPO_NAME) --repository-format=docker --location=$(GCP_REGION) --description=$(DOCKER_REPO_DESCRIPTION) --project=$(GCP_PROJECT_ID)
# gcloud artifacts repositories create $DOCKER_REPO_NAME --repository-format=docker --location=$GCP_REGION --description="$DOCKER_REPO_DESCRIPTION" --project=$GCP_PROJECT_ID

# build image for that repo
deploy_build_image :
	docker build -t $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(VERSION) .
# docker build -t $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$DOCKER_REPO_NAME/$DOCKER_IMAGE_NAME:$VERSION .

# test it first
deploy_test_image :
	@echo "http://127.0.0.1:$(MY_PORT)/test to test"
	docker run -it --env-file .env -p $(MY_PORT):$(PORT) $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(VERSION)
# docker run --env-file .env -p $MY_PORT:$PORT $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$DOCKER_REPO_NAME/$DOCKER_IMAGE_NAME:$VERSION

# push that image onto the repo
deploy_push_image :
	docker push $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(VERSION)
# docker push $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$DOCKER_REPO_NAME/$DOCKER_IMAGE_NAME:$VERSION

# make google serve it
deploy_run_image :
	gcloud run deploy --image $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(VERSION) --region $(GCP_REGION)
# gcloud run deploy --image $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$DOCKER_REPO_NAME/$DOCKER_IMAGE_NAME:$VERSION --region $GCP_REGION

#see running services
# https://console.cloud.google.com/run?project=energeo-428208
#see stored images
# https://console.cloud.google.com/artifacts/browse/energeo-428208?project=energeo-428208

#how to delete service
# https://cloud.google.com/run/docs/managing/services#delete
#how to delete image
# https://cloud.google.com/artifact-registry/docs/docker/manage-images#deleting_images
