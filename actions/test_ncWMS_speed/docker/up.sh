#!/bin/bash
docker run -it -v $(pwd):/app/actions/test_ncWMS_speed --name test-ncwms-speed pcic/test-ncwms-speed:test-ncWMS-speed
