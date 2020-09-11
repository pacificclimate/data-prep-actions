# Test an ncWMS instance speed

This script tests speed of response of a running ncWMS instance.
It does so by issuing HTTP requests to the instance at a variable rate.

Presently, the script:

- Issues a single request type, one of:
    - `GetCapabilities`
    - `GetFeatureInfo`
    - `GetMap`
- Issues issues a request for a single dataset.



