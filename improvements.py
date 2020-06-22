import csv
import datetime
import bests


def change(to_type, what, a, b):
    return to_type(a[what]) - to_type(b[what])


def to_date(what: str):
    return datetime.datetime.strptime(what, "%Y-%m-%d")


def diff(to_type, what, a, b):
    imp = change(to_type, what, a, b)

    pr = round(imp / to_type(b[what]) * 100, 4)
    return imp, pr


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
    }
    return improvement


def instance_order(inst):
    if '_' in inst:
        t, clients, n = inst.split('_')
        order = (t, int(clients), int(n))

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

    out = csv.DictWriter(fd, fieldnames=fields)
    out.writeheader()

    out.writerows(sorted(
        improvements,
        reverse=True,
        key=lambda x: x["when"]))


def gen():
    with open("improvements.csv", 'w') as fd:
        improvements_csv(fd, generate_improvements())


if __name__ == "__main__":
    gen()
