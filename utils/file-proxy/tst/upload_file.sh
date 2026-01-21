#!/bin/bash
#
curl -X POST http://35.187.62.230:5000/upload \
     -H "Authorization: Bearer $SAM_PROXY_TOKEN" \
     -F "file=@/home/dsamarka/work/jan.2026/sensorReadings.parquet"
