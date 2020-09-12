"""
Test the speed of response of a running ncWMS instance.
Schedules a set of HTTP requests to be issued at a fixed interval,
records the responses.

`schedule` (and thus `aioschedule`) can't do the job because they can't schedule at
sub-1-second intervals. Stupid. We want to schedule at intervals of 10 ms or less.
Fortunately it is not hard to do simple scheduling with `asyncio.sleep()`.

We also learn that we cannot use synchronous methods inside jobs, otherwise their
sychronousness makes nominally async processes synchronous, or at least that they
wait for the synchronous process to complete before they return. Specifically, can't
use `requests`. Have to use an async http library, like `aiohttp`. Yay.
"""
import time
import asyncio
import xmltodict
import aiohttp


def time_format(t):
    local_time = time.localtime(t)
    t1 = time.mktime(local_time)
    ms = round((t - t1) * 1000)
    return f"{time.strftime('%H:%M:%S', time.localtime(t))}.{ms}"
    # return f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}.{ms}"


def parse_ncWMS_exception(xml):
    """Extract error message returned by ncWMS"""
    try:
        ed = xmltodict.parse(xml)
        if (
            "ServiceExceptionReport" in ed
            and "ServiceException" in ed["ServiceExceptionReport"]
        ):
            return ed["ServiceExceptionReport"]["ServiceException"]
        return None
    except:
        return "((no XML response))"


async def job_print(id, delay, sync=False):
    sched_time = time.time() + delay
    await asyncio.sleep(delay)
    req_time = time.time()
    print(f"Job at {time_format(sched_time)}:\t{time_format(req_time)}")
    if sync:
        time.sleep(0.2)  # Badness: synchronous!
    else:
        await asyncio.sleep(0.2)  # Goodness: asynchronous!
    return id, sched_time, req_time, time.time(), None


async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
        return response.status, await response.text()


async def job_request(id, delay, ncwms, dataset, session=None):
    params = {
        "request": "GetCapabilities",
        "service": "WMS",
        "version": "1.1.1",
        "dataset": dataset,
    }
    sched_time = time.time() + delay
    await asyncio.sleep(delay)
    req_time = time.time()
    status, content = await fetch(session, ncwms, params)
    return id, sched_time, req_time, time.time(), status, content


async def main(
    ncwms = "https://services.pacificclimate.org/pcex/ncwms",
    dataset = "tasmean_aClimMean_anusplin_historical_19610101-19901231",
    offset = 0,
    interval = 0.01,
    count=5
):
    async with aiohttp.ClientSession() as session:
        tasks = (
            asyncio.create_task(
                job_request(
                    id=i,
                    delay=offset + i * interval,
                    ncwms=ncwms,
                    dataset=dataset,
                    session=session,
                )
            )
            for i in range(count)
        )

        start_time = time.time()
        print(f"Main started at {time_format(start_time)}")
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        print(f"Main finished at {time_format(end_time)}.")
        print(f"Elapsed time: {end_time - start_time}")

        print()
        print("Results")
        print("Job id\tSched time\tDelta\tReq time\tResp time\tLag\tStatus\tMessage")
        errors = 0
        total_lag = 0
        for id, sched_time, req_time, resp_time, status, content in results:
            delta = req_time - sched_time
            resp_lag = resp_time - req_time
            total_lag += resp_lag
            print(
                f"{id}"
                f"\t{time_format(sched_time)}"
                f"\t{round(delta, 3)}"
                f"\t{time_format(req_time)}"
                f"\t{time_format(resp_time)}"
                f"\t{round(resp_lag, 3)}"
                f"\t{status}    "
                f" {'OK' if status == 200 else parse_ncWMS_exception(content)}"
            )
            if status != 200:
                errors += 1
        print(f"Total lag: {total_lag}")
        print(f"{errors} errors in {len(results)} requests")


asyncio.run(main())
