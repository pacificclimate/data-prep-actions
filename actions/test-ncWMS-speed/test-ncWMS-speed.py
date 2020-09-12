"""
Test the speed of response of a running ncWMS instance.
Schedules a set of HTTP requests to be issued at a fixed interval,
records the responses.
"""
from argparse import ArgumentParser
import requests
import sched
import time
import xmltodict


def time_format(t):
    local_time = time.localtime(t)
    t1 = time.mktime(local_time)
    ms = round((t - t1) * 1000)
    return f"{time.strftime('%H:%M:%S', time.localtime(t))}.{ms}"
    # return f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}.{ms}"


responses = []


def action_print(sched_time, sleep):
    """A scheduled action for demonstration/testing."""
    req_time = time.time()
    print(f"Action at {time_format(sched_time)}:\t{time_format(time.time())}")
    time.sleep(sleep)
    responses.append((sched_time, req_time, time.time(), None))


def action_request(sched_time, ncwms, dataset):
    """A scheduled action that issues http requests and accumulates their responses."""
    params = {
        "request": "GetCapabilities",
        "service": "WMS",
        "version": "1.1.1",
        "dataset": dataset,
    }
    req_time = time.time()
    response = requests.get(ncwms, params=params)
    responses.append((sched_time, req_time, time.time(), response))


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


def main(
    version=None,
    ncwms=None,
    dataset=None,
    delay=5.0,
    interval=0.1,
    count=10,
    dry_run=False,
):
    s = sched.scheduler(time.time, time.sleep)
    now = time.time()
    start_time = now + delay
    times = [start_time + i * interval for i in range(count)]
    print(f"It is now {time_format(now)}. Scheduling requests for")
    for t in times:
        print(f"\t{time_format(t)}")

    # Schedule requests
    for t in times:
        if dry_run:
            s.enterabs(t, 0, action_print, argument=(t, 1.0))
        else:
            s.enterabs(t, 0, action_request, argument=(t, ncwms, dataset))
    s.run()

    # Print results
    print("Responses")
    print("sched-time\tdelta\treq-time\treq-int\tres-time\tlag\tstatus\tmessage")
    errors = 0
    for i, (sched_time, req_time, resp_time, response) in enumerate(responses):
        delta = round(req_time - sched_time, 2)
        req_interval = " -- " if i == 0 else round(req_time - responses[i-1][1], 3)
        resp_lag = round(resp_time - req_time, 2)
        status_code = response and response.status_code
        content = response and response.content
        print(
            f"{time_format(sched_time)}"
            f"\t{delta}"
            f"\t{time_format(req_time)}"
            f"\t{req_interval}"
            f"\t{time_format(resp_time)}"
            f"\t{resp_lag}"
            f"\t{status_code}    "
            f" {'OK' if status_code == 200 else parse_ncWMS_exception(content)}"
        )
        if status_code != 200:
            errors += 1
    print(f"Done: {errors} errors in {len(responses)} requests")


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
    parser.add_argument("-D", "--dataset", help="Dataset identifier")
    parser.add_argument(
        "-d", "--delay", help="Delay before start (s)", type=float, default=5.0
    )
    parser.add_argument(
        "-i", "--interval", help="Time between requests (s)", type=float, default=0.1
    )
    parser.add_argument(
        "-c", "--count", help="Number of requests (s)", type=int, default=10
    )
    parser.add_argument("-y", "--dryrun", dest="dry_run", action="store_true")

    args = parser.parse_args()

    main(
        ncwms=args.ncwms,
        version=args.version,
        dataset=args.dataset,
        delay=args.delay,
        interval=args.interval,
        count=args.count,
        dry_run=args.dry_run
    )
