# Use a base image that includes Nvidia CUDA, Python, and Java
FROM nvidia/cuda:12.3.1-runtime-ubuntu20.04

# Install Java and Python
RUN apt update 
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa 
RUN apt update 
RUN apt-get install -y openjdk-17-jdk
RUN apt-get install -y python3.11 python3-pip

# Create working directory
WORKDIR /app

# Copy your initial application files into the container
COPY . /app

# Create support data directory
RUN mkdir -p /support_data

# Default environment variables
ENV NEO4J_HOST 192.168.2.43
ENV NEO4J_AUTH_USERNAME neo4j
ENV NEO4J_AUTH_PASSWORD lkg_khcn
ENV NEO4J_PORT 7769

ENV NLP_API_ENDPOINT http://192.168.2.34:6666
ENV PATH_SPECIAL_VERBS /support_data/danhsachdongtudacbiet.xlsx

# Install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Expose the default network ports
EXPOSE 8007

# Specify the command to run your application when the container starts
CMD ["python3", "main_api.py"]
