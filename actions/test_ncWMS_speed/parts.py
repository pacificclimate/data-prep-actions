import os
import subprocess
import time
import xmltodict
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


def listify(x):
    return x if type(x) == list else [x]


def delistify(x):
    return x if len(x) > 1 else x[0]


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
    # print("### iterate spec", spec)
    name_set = [listify(item["names"]) for item in spec]
    value_sets = (map(listify, item["values"]) for item in spec)
    for value_set in product(*value_sets):
        result = {}
        for names, values in zip(name_set, value_set):
            for name, value in zip(names, values):
                if name in result:
                    result[name].append(value)
                else:
                    result[name] = [value]
        yield { name: delistify(value) for name, value in result.items() }


def extract_capabilities_info(content):
    try:
        d = xmltodict.parse(content)
    except:
        return "Hmmm"
    return {
        "layers": d["WMT_MS_Capabilities"]["Capability"]["Layer"]["Layer"]["Layer"]["Name"]
    }


def format_list(x):
    return '; '.join(listify(x))


def tabulate(row, widths=(8,8,8,8,8,8,8,8,8,8)):
    def format(col, width):
        s = str(col)
        return (s if len(s) <= width else f"..{s[-(width-2):]}").ljust(width)
    return ' | '.join(format(col, width) for col, width in zip(row, widths))


async def fetch(session, url, params, content_type="text"):
    async with session.get(url, params=params) as response:
        # url = str(response.url)
        # print(f"URL (len {len(url)}) '{url}'")
        if content_type == "text" or response.status != 200:
            return str(response.url), response.status, await response.text()
        else:
            return str(response.url), response.status, await response.read()


def print_ncwms_task_results(results):
    columns = (
        ("Job", 3),
        ("Sched time", 12),
        ("Delta", 6),
        ("Req time", 12),
        ("Resp time", 12),
        ("Lag", 6),
        ("Status", 6),
        ("Message", 1000),
    )
    titles, widths = (
        [col[i] for col in columns] for i in range(2)
    )
    underlines = ["-" * width for width in widths]
    print(tabulate(titles, widths=widths))
    print(tabulate(underlines, widths=widths))
    errors = []
    for result in results:
        jobid, params, url, sched_time, req_time, resp_time, status, content = \
            result
        delta = req_time - sched_time
        resp_lag = resp_time - req_time
        print()
        print(
            f"{jobid}\t{'✔' if status == 200 else '❌'} "
            f"{format_list(params['title'])} "
            f"{params['dataset']} "
        )
        # print(f"\t{url}")
        print(tabulate(
            [
                '',
                time_format(sched_time),
                round(delta, 3),
                time_format(req_time),
                time_format(resp_time),
                round(resp_lag, 3),
                status,
                'OK' if status == 200 else parse_ncWMS_exception(content),
            ],
            widths=widths,
        ))

        # Check for file's existence if the request failed
        if status != 200 and params["dataset"].startswith('x/'):
            filepath = params["dataset"][1:]
            exists = os.path.isfile(filepath)
            print(f"\t{'Exists' if exists else 'Absent'}: {filepath}")
            if exists:
                ncdump = subprocess.run([
                    "ncdump", "-v", "time", filepath,
                ], stdout=subprocess.PIPE)
                print(f'{ncdump.stdout.decode("utf-8")}')

        # Print some stuff extracted from the response for GetCapabilities
        if status == 200 and params["request"] == "GetCapabilities":
            print(f"\t{extract_capabilities_info(content)}")

        if status != 200:
            errors.append(result)
    return errors
