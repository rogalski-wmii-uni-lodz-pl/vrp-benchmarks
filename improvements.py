import csv
import datetime
from collections import defaultdict
import pathlib
import bests


def change(to_type, what, a, b):
    return to_type(a[what]) - to_type(b[what])


def to_date(what: str):
    return datetime.datetime.strptime(what, "%Y-%m-%d")


def diff(to_type, what, a, b):
    imp = change(to_type, what, a, b)

    pr = round(imp / to_type(b[what]) * 100, 4)
    return imp, pr


current_full_path = pathlib.Path(__file__).resolve()
pure_path = pathlib.PurePosixPath(current_full_path).parent


def relative_url_hack(url):
    return url.relative_to(pure_path)


def to_improvmenet(prev, sol):
    what = "distance"
    t = float

    if int(prev["routes"]) > int(sol["routes"]):
        what = "routes"
        t = int

    ch, pr = diff(t, what, sol, prev)

    if what == "distance":
        ch = round(ch, 4)

    prev_best = t(prev[what])
    sol_best = t(sol[what])

    after = change(to_date, "when", sol, prev)

    relative_url_hack(sol["url"])

    improvement = {
        "when": sol["when"],
        "who": sol["who"],
        "improved": what,
        "instance": sol["instance"],
        "change": ch,
        "%": pr,
        "new_bks": sol_best,
        "prev_bks": prev_best,
        "beaten": prev["who"],
        "prev_when": prev["when"],
        "after_days": after.days,
        "prev_url": relative_url_hack(prev["url"]),
        "new_url": relative_url_hack(sol["url"]),
    }
    return improvement


def instance_order(inst):
    if '_' in inst:
        t, clients, n = inst.split('_')
        order = (int(clients), t, int(n))

    else:
        t = inst.lstrip('lrc')
        n = inst[:-len(t)]
        order = (t, int(n))

    return order


def generate_improvements():
    db = bests.make_full_bks_db()

    improvements = []

    for inst in db:
        for prev, sol in zip(db[inst], db[inst][1:]):
            imp = to_improvmenet(prev, sol)
            improvements.append(imp)

    improvements.sort(key=lambda x: instance_order(x["instance"]))
    return improvements


def improvements_csv(fd, improvements):
    fields = [
        "when",
        "instance",
        "improved",
        "change",
        "%",
        "new_bks",
        "prev_bks",
        "who",
        "beaten",
        "prev_when",
        "after_days",
    ]

    out = csv.DictWriter(fd, fieldnames=fields, extrasaction='ignore')
    out.writeheader()

    out.writerows(sorted(
        improvements,
        reverse=True,
        key=lambda x: x["when"]))


def format_improvements_for_date_md(fd, imps):
    for benchmark in ["GH", "LL"]:
        if imps[benchmark]:
            bench = "Gehring-Homberger"
            if benchmark == "LL":
                bench = "Li&Lim"

            total = sum(
                len(imps[benchmark][who])
                for who in imps[benchmark])

            fd.write(f"### {bench} ({total} new)\n")

            for who in sorted(imps[benchmark]):
                fd.write(f"#### {who} ({len(imps[benchmark][who])} new):\n")

                for imp in imps[benchmark][who]:
                    text = (
                        f'1. `{imp["instance"]}` '
                        f'from [{imp["prev_bks"]}]({imp["prev_url"]}) '
                        f'to [{imp["new_bks"]}]({imp["new_url"]}) '
                        f'after {imp["after_days"]} days, '
                        f'beating {imp["beaten"]} '
                        f'by {imp["change"]} (by {imp["%"]}%).\n'
                    )
                    fd.write(text)


def improvements_md(fd, improvements):
    d = None

    imps = {
        "GH": defaultdict(list),
        "LL": defaultdict(list),
        "total": 0
    }

    for imp in sorted(improvements, reverse=True, key=lambda x: x["when"]):
        if d and d != imp["when"]:
            fd.write(f'## {d} ({imps["total"]} new)\n')
            format_improvements_for_date_md(fd, imps)

            imps["GH"].clear()
            imps["LL"].clear()
            imps["total"] = 0

        d = imp["when"]

        bench = "GH"
        if imp["instance"][0] == 'l':
            bench = "LL"

        imps[bench][imp["who"]].append(imp)
        imps["total"] += 1

        # text = (
        #     f'1. {imp["who"]} improved the {imp["improved"]}\'s '
        #     f'on {bench} {imp["instance"]} '
        #     f'from {imp["prev_bks"]} to {imp["new_bks"]} '
        #     f'after {imp["after_days"]} days, '
        #     f'improving a solution found previously by {imp["beaten"]} '
        #     f'by {imp["change"]} (by {imp["%"]}%).\n'
        # )

        # fd.write(text)


def gen():
    with open("improvements.csv", 'w') as fd:
        improvements_csv(fd, generate_improvements())

    with open("improvements.md", 'w') as fd:
        improvements_md(fd, generate_improvements())


if __name__ == "__main__":
    gen()
