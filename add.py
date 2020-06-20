import sys
import datetime
import os
import shutil
from collections import defaultdict
# from parse_solution import parse_solution
from verify import read_solution_and_instance, is_valid, total_distance
from bests import make_full_bks_db, is_better, bks_location


def generate_new_bks(db, paths):
    bks = {}
    report = []

    for f in paths:
        solution, instance = read_solution_and_instance(f)

        ok, errors = is_valid(solution, instance)

        imp = ""
        result = (-1, -1)

        st = "ERR"

        if ok:
            routes = len(solution["routes"])
            distance = total_distance(solution, instance)

            prev_best = db[solution["instance"]][-1]

            st = "OK"
            result = (routes, distance)

            if is_better(prev_best, routes, distance):
                st = "BKS"
                improvement = (float(distance) - float(prev_best["distance"]))
                prec = improvement / float(distance) * 100
                imp = f" ({improvement:.2f}, {prec:.2f}%)"

                inst = solution["instance"]

                if inst not in bks or is_better(bks[inst], routes, distance):
                    bks[inst] = {
                        "instance": inst,
                        "routes": routes,
                        "distance": distance,
                        "benchmark": solution["benchmark"],
                        "file": f,
                    }

        report.append(
            {
                "file": f,
                "benchmark": solution["benchmark"],
                "instance": solution["instance"],
                "status": st,
                "errors": errors,
                "result": result,
                "improvement": imp,
            }
        )

    return bks, report


def make_name(new_best):
    inst = new_best["instance"]
    routes = new_best["routes"]
    distance = round(new_best["distance"], 4)

    new_name = f'{inst}.{routes}_{distance}.txt'

    return new_name


def copy_new_bks(bks):
    today = str(datetime.date.today())

    for b in bks:
        new_best = bks[b]

        new_location = bks_location / new_best["benchmark"] / today

        os.makedirs(
            new_location,
            exist_ok=True
        )

        new_name = make_name(new_best)

        shutil.copyfile(new_best["file"], new_location / new_name)

        # print(
        #     "copying new BKS", new_best["file"],
        #     "to", new_location / new_name)


def group_by_benchmark(report):
    groupped = defaultdict(list)

    for f in report:
        groupped[f["benchmark"]].append(f)

    return groupped


def format_report_item(f):
    routes, dist = f["result"]
    return (
        f'{f["file"]} {f["benchmark"]} {f["instance"]} '
        f'{f["status"]} {routes} {dist:.4f}'
    )


def report_errors(errors):
    if errors:
        print("ERRORS")
        print("======")
        for f in errors:
            print(f["file"], f["errors"])

        print()


def report_in_benchmark_groups(report):
    groupped = group_by_benchmark(report)
    for b in groupped:
        print(b)
        print("-"*len(b))
        for f in groupped[b]:
            print(format_report_item(f))

        print()


def report_if_not_empty(report, name):
    if report:
        print(name)
        print("="*len(name))

        report_in_benchmark_groups(report)


def split_report(report):
    errors = []
    bks = []
    oks = []

    for f in report:
        if f["status"] == "ERR":
            errors.append(f)
        elif f["status"] == "BKS":
            bks.append(f)
        else:
            oks.append(f)

    return errors, bks, oks


def make_nice_report(report):
    errors, bks, oks = split_report(report)

    report_errors(errors)
    report_if_not_empty(bks, "BKS")
    report_if_not_empty(oks, "OK")


if __name__ == "__main__":
    db = make_full_bks_db()

    bks, report = generate_new_bks(db, sys.argv[1:])

    copy_new_bks(bks)
    make_nice_report(report)
