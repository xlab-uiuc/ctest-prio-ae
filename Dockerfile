FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
	apt-get install -y --no-install-recommends build-essential\
	expect git vim zip unzip wget openjdk-8-jdk wget sudo

RUN sudo apt-get install -y less

RUN apt-get install -y python3 python3-pip
RUN pip3 install gensim==3.8.3
RUN pip3 install matplotlib

RUN sudo apt install -y apt-transport-https software-properties-common
RUN sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN sudo add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/'
RUN sudo apt update
RUN sudo apt install -y r-base
RUN R -e "install.packages('agricolae',dependencies=TRUE, repos='http://cran.rstudio.com/')"