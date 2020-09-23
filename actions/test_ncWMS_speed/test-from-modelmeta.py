from argparse import ArgumentParser
import datetime
import time
from sqlalchemy import create_engine, and_, or_, extract
from sqlalchemy.orm import sessionmaker
from modelmeta import (
    ClimatologicalTime,
    DataFile,
    DataFileVariableGridded,
    Ensemble,
    EnsembleDataFileVariables,
    Emission,
    Model,
    Run,
    Time,
    TimeSet,
    VariableAlias,
)
import yaml
import asyncio
import aiohttp
from declarative_iteration import iterate
from parts import (
    fetch,
    tabulate,
    time_format,
    print_ncwms_task_results,
    dict_subset,
)


def format(value):
    if type(value) == datetime.datetime:
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    return value


def to_dict(obj, names):
    return {
        name: format(getattr(obj, name)) for name in names
    }


def season_month_num(value):
    if type(value) == str:
        try:
            return {
                "winter": 1,
                "spring": 4,
                "summer": 7,
                "fall": 10,
            }[value]
        except KeyError:
            raise ValueError(f"Invalid season name '{value}'")
    return value


def month_num(value):
    if type(value) == str:
        try:
            return (
                "jan feb mar apr may jun jul aug sep oct nov dec"
                .split().index(value) + 1
            )
        except ValueError:
            raise ValueError(f"Invalid month name '{value}'")
    return value


def get_db_session(dsn):
    engine = create_engine(dsn)
    Session = sessionmaker(bind=engine)
    return Session()


def get_layer_query(
    session,
    ensemble_name=None,
    models=None,
    emissions=None,
    variable_name=None,
    timescale=None,
    year=None,
    season=None,
    month=None,
):
    q = (
        session.query(
            DataFile.unique_id.label("unique_id"),
            DataFile.filename.label("filepath"),
            Model.short_name.label("model_id"),
            Emission.short_name.label("emission"),
            Run.name.label("run"),
            DataFileVariableGridded.netcdf_variable_name.label("variable"),
            TimeSet.time_resolution.label("timescale"),
            TimeSet.multi_year_mean.label("multi_year_mean"),
            TimeSet.start_date.label("start_date"),
            TimeSet.end_date.label("end_date"),
            Time.timestep.label("timestep"),
        )
            .join(Run, Run.id == DataFile.run_id)
            .join(Model)
            .join(Emission)
            .join(
            DataFileVariableGridded,
            DataFileVariableGridded.data_file_id == DataFile.id
        )
            .join(EnsembleDataFileVariables)
            .join(Ensemble)
            .join(
            VariableAlias,
            VariableAlias.id == DataFileVariableGridded.variable_alias_id
        )
            .join(TimeSet, TimeSet.id == DataFile.time_set_id)
            .join(Time, Time.time_set_id == TimeSet.id)
            # .join(ClimatologicalTime, ClimatologicalTime.time_set_id == TimeSet.id)
            .filter(Ensemble.name == ensemble_name)
            .filter(Emission.short_name.in_(emissions))
            .order_by(DataFile.unique_id, TimeSet.time_resolution, Time.timestep)
    )

    if models is not None:
        q = q.filter(Model.short_name.in_(models))
    if variable_name is not None:
        q = q.filter(DataFileVariableGridded.netcdf_variable_name == variable_name)
    if timescale is not None:
        q = q.filter(TimeSet.time_resolution == timescale)
        if timescale == "yearly":
            q = q.filter(extract('year', Time.timestep) == year)
        elif timescale == "seasonal":
            q = q.filter(
                and_(
                    extract('year', Time.timestep) == year,
                    extract('month', Time.timestep) == season_month_num(season),
                )
            )
        elif timescale == "monthly":
            q = q.filter(
                and_(
                    extract('year', Time.timestep) == year,
                    extract('month', Time.timestep) == month_num(month),
                )
            )
        else:
            raise ValueError(f"Invalid timescale '{timescale}'")

    return q


db_query_columns = (
    ("unique_id",  "unique_id", 80),
    ("filepath",  "filepath", 200),
    ("model_id",  "model_id", 10),
    ("emission",  "emission", 18),
    # ("run",  "run", 8),
    ("variable",  "variable", 10),
    ("timescale",  "timescale", 10),
    ("multi_year_mean",  "MYM", 5),
    # ("start_date",  "start_date", 20),
    # ("end_date",  "end_date", 20),
    ("timestep",  "timestep", 20),
)
dbq_attrs, dbq_titles, dbq_widths = (
    [col[i] for col in db_query_columns] for i in range(3)
)
dbq_underlines = ["-" * width for width in dbq_widths]


async def ncwms_request(
    session=None,
    id=0,
    **kwargs,
):
    # To enable passing additional parameters not directly relevant to the ncwms
    # request proper, we use a generic kwargs argument for most of them, and extract the
    # relevant ones by keyword. The entire parameter set is returned by the task so that
    # anything relevant can be retrieved from its results later.

    start_delay = kwargs["start_delay"]
    ncwms = kwargs["ncwms"]
    request = kwargs["request"]
    dataset = kwargs["dataset"]
    variable_name = kwargs["variable_name"]
    timestep = kwargs["timestep"]
    bbox = kwargs["bbox"]
    width = kwargs["width"]
    height = kwargs["height"]

    base_query_params = {
        "request": request,
        "service": "WMS",
        "version": "1.1.1",
    }
    if request == "GetCapabilities":
        query_params = {
            **base_query_params,
            "dataset": dataset,
        }
    elif request == "GetMap":
        query_params = {
            **base_query_params,
            # Note: Must use `layers` param, not `dataset` for dynamic datasets
            "layers": f"{dataset}/{variable_name}",
            "TRANSPARENT": "true",
            "STYLES": "default-scalar/x-Occam",
            "NUMCOLORBANDS": "254",
            "SRS": "EPSG:4326",
            "LOGSCALE": "false",
            "FORMAT": "image/png",
            "BBOX": bbox,
            "WIDTH": width,
            "HEIGHT": height,
            "COLORSCALERANGE": "-5,15",
            "TIME": timestep,
        }
    else:
        raise ValueError(f"Invalid request type '{request}'")

    sched_time = time.time() + start_delay
    await asyncio.sleep(start_delay)
    req_time = time.time()
    content_type = "text" if request == "GetCapabilities" else "binary"
    url, status, content = await fetch(session, ncwms, query_params, content_type)
    return id, kwargs, url, sched_time, req_time, time.time(), status, content


async def main(
    mmdb=None,
    param_sets=None,
    dry_run=False,
):

    print("Parameter sets")
    for i, param_set in enumerate(param_sets):
        print(f'Parameter set {i}', param_set)

    db_session = get_db_session(mmdb)
    # print(tabulate(titles, widths=widths))

    tasks = []
    job_id = 0

    async with aiohttp.ClientSession() as aiohttp_session:
        for i, param_set in enumerate(param_sets):
            print()
            layer_params = dict_subset(param_set, (
                "ensemble_name",
                "models",
                "emissions",
                "variable_name",
                "year",
                "timescale",
                "season",
                "month",
            ))
            # print("Layer params", lp)
            q = get_layer_query(db_session, **layer_params)

            print(f"Parameter set {i}: {q.count()} layers selected", )
            query_results = q.all()
            print(tabulate(dbq_titles, widths=dbq_widths))
            print(tabulate(dbq_underlines, widths=dbq_widths))

            for query_result in query_results:
                row = [format(getattr(query_result, name)) for name in dbq_attrs]
                print(tabulate(row, widths=dbq_widths))

                dataset = (
                    query_result.unique_id if param_set["dataset_type"] == "static"
                    else f"x{query_result.filepath}"
                )
                for j in range(param_set["count"]):
                    tasks.append(
                        ncwms_request(
                            session=aiohttp_session,
                            id=job_id,
                            query_result=query_result,
                            start_delay=param_set["delay"] + j * param_set["interval"],
                            dataset=dataset,
                            timestep=format(query_result.timestep),
                            **param_set,
                        )
                    )
                    job_id += 1

        print(f"{len(tasks)} tasks to start")
        if dry_run:
            return

        start_time = time.time()
        print(f"Tasks started at {time_format(start_time)}")
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        print(f"Tasks finished at {time_format(end_time)}.")
        print(f"Elapsed time: {end_time - start_time}")

        print()
        print(f"All results")
        errors = print_ncwms_task_results(results)

        print()
        print(f"{len(errors)} errors in {len(results)} requests")

        print()
        print(f"Error results only")
        print_ncwms_task_results(errors, details=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-m",
        "--mmdb",
        help="modelmeta database connection string of the form "
             "postgresql://user:password@host:port/database"
    )
    parser.add_argument(
        "-f", "--file",
        help="Specification file for iteration of parameter values."
    )
    parser.add_argument("-y", "--dryrun", dest="dry_run", action="store_true")
    args = parser.parse_args()

    with open(args.file) as file:
        spec = yaml.safe_load(file)
    param_sets = iterate(spec)

    asyncio.run(
        main(mmdb=args.mmdb, param_sets=param_sets)
    )



