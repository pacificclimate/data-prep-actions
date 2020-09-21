"""
Test the speed of response of a running ncWMS instance.
Schedules a set of HTTP requests to be issued at a fixed interval,
records the responses.

`schedule` (and thus `aioschedule`) can't do the job because they can't schedule at
sub-1-second intervals. Stupid. We want to schedule at intervals of 10 ms or less.
Fortunately it is not hard to do simple scheduling with `asyncio.sleep()`.

We also learn that we cannot use synchronous methods inside jobs, otherwise their
sychronousness makes nominally async processes synchronous, or at least they
wait for the synchronous process to complete before they return. Specifically, we
can't use package `requests`. Have to use an async http library, like `aiohttp`.

With the async version working, we observe that ncWMS does not seem to choke on
GetCapabilities requests even when many (20) requests are made at intervals of 5 ms.
First run gives all lags ~ 0.5s. Subsequent runs gives lags ~ 0.1 - 0.2 s.

So now we must add GetMap requests to see if those fail.
"""
import os
from argparse import ArgumentParser
import time
import asyncio
import aiohttp
import yaml
from parts import (
    time_format,
    parse_ncWMS_exception,
    extract_capabilities_info,
    format_list, iterate, tabulate,
    fetch,
    print_ncwms_task_results,
)


async def ncwms_request(
    session,
    id,
    delay,
    params,
):
    request_ = params["request"]
    base_query_params = {
        "request": request_,
        "service": "WMS",
        "version": "1.1.1",
    }
    if request_ == "GetCapabilities":
        query_params = {
            **base_query_params,
            "dataset": params["dataset"],
        }
    elif request_ == "GetMap":
        query_params = {
            **base_query_params,
            # Note: Must use `layers` param, not `dataset` for dynamic datasets
            "layers": f"{params['dataset']}/{params['variable']}",
            "TRANSPARENT": "true",
            "STYLES": "default-scalar/x-Occam",
            "NUMCOLORBANDS": "254",
            "SRS": "EPSG:4326",
            "LOGSCALE": "false",
            "FORMAT": "image/png",
            "BBOX": params["bbox"],
            "WIDTH": params["width"],
            "HEIGHT": params["height"],
            "COLORSCALERANGE": "-5,15",
            "TIME": params["timestamp"],
        }
    else:
        raise ValueError(f"Invalid request type '{request_}'")
    sched_time = time.time() + delay
    await asyncio.sleep(delay)
    req_time = time.time()
    content_type = "text" if request_ == "GetCapabilities" else "binary"
    url, status, content = await fetch(session, params["ncwms"], query_params, content_type)
    return id, params, url, sched_time, req_time, time.time(), status, content


async def main(
    paramsets,
    dry_run=True,
):
    async with aiohttp.ClientSession() as session:
        jobid = 0
        tasks = []
        for paramset in paramsets:
            delay = paramset["delay"]
            interval = paramset["interval"]
            count = paramset["count"]
            if dry_run:
                print(
                    f"Jobs {jobid} to {jobid + count -1}:"
                    f"\n\t{paramset}"
                )
            for i in range(count):
                if not dry_run:
                    tasks.append(
                        asyncio.create_task(
                            ncwms_request(
                                session=session,
                                id=jobid,
                                delay=delay + i * interval,
                                params=paramset,
                            )
                        )
                    )
                jobid += 1

        start_time = time.time()
        print(f"Main started at {time_format(start_time)}")
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        print(f"Main finished at {time_format(end_time)}.")
        print(f"Elapsed time: {end_time - start_time}")

        print()
        print(f"All results")
        errors = print_ncwms_task_results(results)

        print()
        print(f"{len(errors)} errors in {len(results)} requests")

        print()
        print(f"Error results only")
        print_ncwms_task_results(errors)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-n", "--ncwms", help="ncWMS base url of the form https://example.org/dir/ncwms"
    )
    parser.add_argument(
        "-v",
        "--version",
        type=int,
        default=1,
        choices=[1, 2],
        help="ncWMS version format",
    )
    parser.add_argument(
        "-f", "--file",
        help="Specification file for iteration of parameter values. If this option "
             "is specified, all other options except dry_run are ignored."
    )
    parser.add_argument("-D", "--dataset", help="Dataset identifier")
    parser.add_argument(
        "-r",
        "--request",
        help="ncWMS request",
        choices=["GetCapabilities", "GetMap"],
        default="GetCapabilities",
    )
    parser.add_argument(
        "-d", "--delay", help="Delay before start (s)", type=float, default=5.0
    )
    parser.add_argument(
        "-b",
        "--bbox",
        help="Bounding box for GetMap requests",
        default="-125.00000000000001,65,-112.5,77.5",
    )
    parser.add_argument(
        "-w",
        "--width",
        help="Tile width for GetMap requests",
        type=int,
        default=256,
    )
    parser.add_argument(
        "-H",
        "--height",
        help="Tile height for GetMap requests",
        type=int,
        default=256,
    )
    parser.add_argument(
        "-t",
        "--time",
        help="Time arg for GetMap requests",
        default="2085-07-02T00:00:00Z",  # yeah, right
    )
    parser.add_argument(
        "-i", "--interval", help="Time between requests (s)", type=float, default=0.1
    )
    parser.add_argument(
        "-c", "--count", help="Number of requests", type=int, default=10
    )
    parser.add_argument("-y", "--dryrun", dest="dry_run", action="store_true")

    args = parser.parse_args()

    if args.file:
        with open(args.file) as file:
            spec = yaml.safe_load(file)
        paramsets = iterate(spec)
    else:
        paramsets = [
            dict(ncwms=args.ncwms, version=args.version, dataset=args.dataset,
            request=args.request, bbox=args.bbox, width=args.width, height=args.height,
            timestamp=args.time, delay=args.delay, interval=args.interval,
            count=args.count, )
        ]

    asyncio.run(
        main(paramsets, dry_run=args.dry_run)
    )
