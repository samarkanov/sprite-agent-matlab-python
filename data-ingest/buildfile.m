function plan = buildfile
import matlab.buildtool.tasks.*
plan = buildplan(localfunctions);
plan.DefaultTasks = "build";
end

function buildTask(~)
% Build the MCP tool
mcpTool = prodserver.mcp.build("getSensorData", ...
    wrapper="None");

% Deploy to the local server
endpoint = prodserver.mcp.deploy(mcpTool, "localhost", 9910);
disp("Endpoint deployed at: " + endpoint);

% Check if the endpoint is available
available = prodserver.mcp.ping(endpoint);

if available
    fprintf('Server is responsive. Proceeding to call function...\n');
else
    error('Build:DeploymentFailed', 'The Production Server endpoint at %s is not responding.', endpoint);
end

% Try to call the function
try
    sensorDataLocation = prodserver.mcp.call(endpoint, "getSensorData");    
catch ME
    % Handle call-specific errors
    error('Build:CallFailed', 'Failed to call "getSensorData": %s', ME.message);
end

fprintf('Sensor data location: %s\n', sensorDataLocation);

end
