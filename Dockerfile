FROM google/cloud-sdk:latest
RUN apt-get install -y rsync git
ADD . /schemaorg
#RUN mkdir -p /schemaorg
WORKDIR /schemaorg
RUN git submodule update --init --recursive
EXPOSE 8080
CMD ./runpythonapp.sh

