run_api_uvicorn:
	@echo Docs link here: http://localhost:$(MY_PORT)/docs
	uvicorn api.fast:app --port $(MY_PORT) --reload

docker_build_local_image:
	docker build -t energy:$(DOCKER_LOCAL_TAG) .

#laptop_port : container_port
run_api_docker:
	@echo running from local docker image
	@echo "open http://localhost:$(MY_PORT)/ in browser to see"
	docker run -it --env-file .env -p $(MY_PORT):$(PORT) energy:$(DOCKER_LOCAL_TAG)

#inspect running image
docker_local_shell:
	docker run -it --env-file .env -p $(MY_PORT):$(PORT) energy:$(DOCKER_LOCAL_TAG) sh

#**FOR USE WITHIN CONTAINER!**
run_cmd:
	uvicorn api.fast:app --host 0.0.0.0 --port $(PORT)

#	0 - create repo
deploy_create_repo:
	gcloud artifacts repositories create $(DOCKER_REPO_NAME) --repository-format=docker --location=$(GCP_REGION) --description="$(DOCKER_REPO_DESCRIPTION)" --project=$(GCP_PROJECT_ID)

# 1 - build image for that repo
deploy_build_image:
	docker build -t $(IMAGE_URI) .

# 2 - test it first
deploy_test_image:
	@echo "http://localhost:$(MY_PORT)/docs try the endpoints to test"
	docker run -it --env-file .env -p $(MY_PORT):$(PORT) $(IMAGE_URI)

# 3 - push that image onto the repo (image name contains repo)
deploy_push_image:
	docker push $(IMAGE_URI)

# 4 - make google serve it
deploy_run_image:
	gcloud run deploy --image $(IMAGE_URI) --region $(GCP_REGION)

#see running services
# https://console.cloud.google.com/run?project=energeo-428208
#see stored images
# https://console.cloud.google.com/artifacts/browse/energeo-428208?project=energeo-428208

#how to delete service
# https://cloud.google.com/run/docs/managing/services#delete
#how to delete image
# https://cloud.google.com/artifact-registry/docs/docker/manage-images#deleting_images

setup_project:
	pyenv virtualenv enerGeo_env
	pyenv local enerGeo_env
	pip install --upgrade pip
	pip install -r requirements.txt

refresh_requirements:
	pip freeze | xargs pip uninstall -y
	pip install -r requirements.txt
	pip install --upgrade pip

git_commands:
# delete local branches that are tracking remote ones
	git fetch origin --prune
#delete remote branch
	git push -d origin <branch-name>


#docker image management commands

stop_running_containers:
	docker ps -a -q | xargs -r docker stop | xargs -r docker rm

docker_dangling_show:
	docker images -f 'dangling=true'

docker_dangling_delete:
	docker images -f 'dangling=true' -q | xargs -r docker rmi
