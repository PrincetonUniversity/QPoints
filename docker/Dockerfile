#FROM arm64v8/ubuntu:latest
FROM ubuntu:latest

# Update package lists
RUN apt-get update

# Install gdb-multiarch
RUN apt-get install -y gdb-multiarch
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y qemu
RUN apt-get install -y qemu-system
RUN pip3 install jinja2 
RUN apt-get install -y vim

# Set the entrypoint to start a shell
WORKDIR /qpoints
ENTRYPOINT ["/bin/bash"]
