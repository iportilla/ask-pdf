# Transform the machine arch into some standard values: "arm", "arm64", or "amd64"
SYSTEM_ARCH := $(shell uname -m | sed -e 's/aarch64.*/arm64/' -e 's/x86_64.*/amd64/' -e 's/armv.*/arm/')

# To build for an arch different from the current system, set this env var to one of the values in the comment above
#export ARCH ?= $(SYSTEM_ARCH)


# Redis VSS Demo
export ARCH ?= amd64
export PORT ?= 80




# These variables can be overridden from the environment
export APP_NAME ?= ask-pdf
export APP_VERSION ?= 1.0.1


DOCKER_NAME ?= $(ARCH)_$(APP_NAME)

#add your id in Docker Hub
export DOCKER_HUB_ID ?= iportilla
export MYDOMAIN ?= github.com/iportilla/ask-pdf


default: all

all: build run

build:
	docker build -t $(DOCKER_HUB_ID)/$(APP_NAME):$(APP_VERSION) -f ./Dockerfile.$(ARCH) .
ifeq (,$(findstring amd64,$(ARCH)))
	rm -f tmp/$(ARCH)/*.rsa.pub
endif


run:
	-docker rm -f $(APP_NAME) 2> /dev/null || :
	docker run -d --name $(APP_NAME) -p $(PORT):8501 --volume `pwd`:/outside $(DOCKER_HUB_ID)/$(APP_NAME):$(APP_VERSION)
	@echo "Open your browser and go to http://localhost:"$(PORT)


check:
	docker logs -f $(APP_NAME)

stop:
	-docker rm -f $(APP_NAME) 2> /dev/null || :

clean:
	-docker rm -f $(APP_NAME) 2> /dev/null || :
	-docker rmi $(DOCKER_HUB_ID)/$(APP_NAME):$(APP_VERSION) 2> /dev/null || :

.PHONY: default all build run check stop clean
