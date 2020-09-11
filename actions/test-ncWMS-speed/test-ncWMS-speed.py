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
    return f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}.{ms}"


def action_print(t):
    """A scheduled action for demonstration/testing."""
    print(f"Action at {time_format(t)}:\t{time.time()}")


responses = []


def action_request(t, ncwms, dataset):
    """A scheduled action that issues http requests and accumulates their responses."""
    params = {
        "request": "GetCapabilities",
        "service": "WMS",
        "version": "1.1.1",
        "dataset": dataset,
    }
    response = requests.get(ncwms, params=params)
    responses.append((t, response))


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
            s.enterabs(t, 0, action_print, argument=(t,))
        else:
            s.enterabs(t, 0, action_request, argument=(t, ncwms, dataset))
    s.run()

    # Print results
    print("Responses")
    errors = 0
    for t, response in responses:
        status_code = response.status_code
        content = response.content
        print(
            f"\t{time_format(t)}\t  {status_code}"
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
    parser.add_argument("-y", "--dry-run", dest="dry_run", action="store_true")

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
