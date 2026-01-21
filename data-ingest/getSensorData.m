function endpoint = getSensorData()
%GETSENSORDATA Generates synthetic vibration data and exports it to HDFS.
%
%   ENDPOINT = GETSENSORDATA() creates a 1-second synthetic vibration signal
%   modeling industrial machinery, stores it as a Parquet file locally, 
%   and transfers it to a Hadoop Distributed File System (HDFS) instance.
%
%   OUTPUT:
%       endpoint - A string containing the full HDFS URI of the saved file.
%
%   PROCESS:
%       1. Simulates a signal with 50Hz (rotational) and 120Hz (fault) components.
%       2. Adds Gaussian white noise to simulate real-world sensor interference.
%       3. Formats data into a MATLAB table and exports to Apache Parquet format.
%       4. Executes a system-level 'hadoop fs -put' command to migrate the file.
%
%   REQUIREMENTS:
%       - Hadoop environment must be configured (core-site.xml).
%       - HDFS NameNode must be reachable at localhost:9000.
%       - 'hadoop' command-line utilities must be in the system PATH.
%
%   See also PARQUETWRITE, SYSTEM, ARRAY2TABLE.

    % --- Output Argument Validation ---
    arguments(Output)
        endpoint string  % Final HDFS path of the generated dataset
    end

    % Configure Hadoop
    if isdeployed
        setenv("HADOOP_HOME", "/home/dsamarka/prog/hadoop-3.4.2");
    end

    % --- Configuration & Path Setup ---
    % outFile: Temporary local storage before HDFS ingestion
    % hdfsPath: The target directory within the HDFS hierarchy
    outFile = "sensorReadings.parquet";
    hdfsPath = "hdfs://localhost:9000/user/data/";
    outPath = strcat(hdfsPath, outFile);

    % --- Signal Acquisition Simulation ---
    fs = 2000;                      % Sampling frequency in Hz
    t = linspace(0, 1, fs);         % Time vector for a 1-second duration
    
    % Construct synthetic vibration signature:
    % Component 1: 50Hz fundamental frequency
    % Component 2: 120Hz higher-frequency fault harmonic
    % Component 3: Random noise scaled by 0.5
    sig = sin(2*pi*50*t) + 0.8*sin(2*pi*120*t) + 0.5*randn(size(t));

    % --- Data Persistence ---
    % Convert signal vector to a table for Parquet compatibility
    % Variable name 'vibration' is used for schema consistency in HDFS
    T = array2table(sig', 'VariableNames', {'vibration'});
    
    % Write the file to the local working directory
    parquetwrite(outPath, T);

    fprintf('Successfully uploaded to HDFS: %s\n', outPath);
    
    % Return the full URI for downstream MCP resources or data processing
    % Programmatically replace protocol and port
    endpoint = strrep(outPath, "hdfs://", "webhdfs://"); % Downstream MCP tool works with webhdfs and not hdfs
    endpoint = strrep(endpoint, ":9000", ":9870"); % When moving from hdfs to webhdfs, the port must be changed
end
