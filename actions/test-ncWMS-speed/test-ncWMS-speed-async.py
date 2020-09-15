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
from argparse import ArgumentParser
import time
import asyncio
import xmltodict
import aiohttp
import yaml
from itertools import product


def time_format(t):
    local_time = time.localtime(t)
    t1 = time.mktime(local_time)
    ms = round((t - t1) * 1000)
    return f"{time.strftime('%H:%M:%S', time.localtime(t))}.{ms}"


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


async def fetch(session, url, params, content_type="text"):
    async with session.get(url, params=params) as response:
        # url = str(response.url)
        # print(f"URL (len {len(url)}) '{url}'")
        if content_type == "text" or response.status != 200:
            return str(response.url), response.status, await response.text()
        else:
            return str(response.url), response.status, await response.read()


async def job_request(
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
        # Note: Must use `layers` param, not `dataset` for dynamic datasets
        "layers": params["dataset"],
    }
    if request_ == "GetCapabilities":
        query_params = base_query_params
    elif request_ == "GetMap":
        query_params = {
            **base_query_params,
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


def iterate(spec):
    """
    Generic iterator

    Forms the cross product of value sets specified in `spec`.
    Yields each elements of the cross product as a dict.
    Value sets are tuples of values, which are flattened for output. This permits
    iteration of selected groupings of values, rather than forcing the cross product
    of values within the group. This is the reason for existence of this generator
    (otherwise itertools.product would be sufficient).

    :param spec: specifier for iteration (see above)
    :return: generator yielding items from cross product

    The specifier, `spec`
    - specifies both names and values of sets whose cross product it forms
    - groups names and values in sets to be iterated as a unit

    As an example, spec takes the form (in YAML notation):

        - names: ['a', 'b']
          values:
            - ["a1", "b1"]
            - ["a2", "b2"]
        - names: "c"
          values:
            - "c1"
            - "c2"

    The values for `a` and `b` are iterated as a unit, which is to say they are treated
    as a single set in the cross product. The values for `c` are also iterated as a
    unit; but since the unit contains only one parameter, this is like an ordinary
    contributor to the cross product. Note in the case of singleton groups, both
    names and values be specified either as lists (each containing a single item) or as
    single items, sans enclosing list, as above.

    The cross product is thus formed as (a, b) x c.

    The results of this cross product are "flattened" so that the yielded value
    has the form (a, b, c) or {"a": a, "b": b, "c": c} according to `output`.

    The output of the spec above would therefore be:

        {'a': 'a1', 'b': 'b1', 'c': 'c1'}
        {'a': 'a1', 'b': 'b1', 'c': 'c2'}
        {'a': 'a2', 'b': 'b2', 'c': 'c1'}
        {'a': 'a2', 'b': 'b2', 'c': 'c2'}
    """
    # print('###', spec)
    def listify(x):
        return x if type(x) == list else [x]

    name_set = [listify(item["names"]) for item in spec]
    value_sets = (map(listify, item["values"]) for item in spec)
    for value_set in product(*value_sets):
        yield {
            name: value
            for names, values in zip(name_set, value_set)
            for name, value in zip(names, values)
        }


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
                            job_request(
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
        print(f"Results")
        print("Job id\tSched time\tDelta\tReq time\tResp time\tLag\tStatus\tMessage")
        errors = 0
        total_lag = 0
        for jobid, params, url, sched_time, req_time, resp_time, status, content \
            in results:
            delta = req_time - sched_time
            resp_lag = resp_time - req_time
            total_lag += resp_lag
            print()
            print(
                f"{jobid}\t{params['title']}"
                f"\n\t{url}"
            )
            print(
                f"\t{time_format(sched_time)}"
                f"\t{round(delta, 3)}"
                f"\t{time_format(req_time)}"
                f"\t{time_format(resp_time)}"
                f"\t{round(resp_lag, 3)}"
                f"\t{status}    "
                f" {'OK' if status == 200 else parse_ncWMS_exception(content)}"
            )
            # print(f"\t{params}")
            if status != 200:
                errors += 1
        print()
        print(f"{errors} errors in {len(results)} requests")
        print(f"Total lag: {total_lag}")


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
