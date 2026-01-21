# Configure HDFS (Once when install for the first time)
hdfs namenode -format

# Start
start-dfs.sh

# Create repo
hadoop fs -mkdir -p hdfs://localhost:9000/user/data

# Upload data
hadoop fs -put readme.md hdfs://localhost:9000/user/data


