# Test an ncWMS instance speed

This script tests speed of response of a running ncWMS instance.
It does so by issuing HTTP requests to the instance at a variable rate.

Presently, the script:

- Issues a single request type, one of:
    - `GetCapabilities`
    - `GetFeatureInfo`
    - `GetMap`
- Issues issues a request for a single dataset.


## Database consulting

Want to specify a layer as in P2A or CE.
In order to query the database, we need to specify:
- ensemble
- model
- emission (scenario, experiment)
- run?
- variable
- time
    - timescale (monthly, seasonal, yearly)
    - timestep (specific date)
    
All these are easy to specify except timestep. 
As an alternative to year, month, and day, we can specify
- for all timescales
    - middle year (2025, 2055, 2085) -> month jul
- for seasonal timescale:
    - season (winter, spring, summer, fall) -> months (jan, apr, jul, oct)
- for monthly timescale:
    - month

So a time specifier could look like:
    { 
        timescale: yearly | seasonal | monthly,
        year: 2025 | 2055 | 2085,
        season: fall | winter | spring | summer
        month: jan | feb | ... | dec
    }

Parameters (relevant*) for an ncWMS GetMap request:
- layer*
    - dataset
    - variable
- bbox
- width
- height
- time (=timestep)



