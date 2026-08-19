"""Minimal functional coverage collector for cocotb testbenches."""


class CoverageGroup:
    def __init__(self, name, bins):
        self.name = name
        self.goal = set(bins)
        self.hits = {}

    def sample(self, value):
        if value in self.goal:
            self.hits[value] = self.hits.get(value, 0) + 1

    @property
    def covered(self):
        return len(set(self.hits) & self.goal)

    @property
    def percent(self):
        return 100.0 * self.covered / len(self.goal) if self.goal else 100.0

    def missing(self):
        return sorted(self.goal - set(self.hits), key=str)


class Coverage:
    def __init__(self, log, name="coverage"):
        self.log = log
        self.name = name
        self.groups = {}

    def add_group(self, name, bins):
        self.groups[name] = CoverageGroup(name, bins)
        return self.groups[name]

    def sample(self, group, value):
        self.groups[group].sample(value)

    def report(self):
        self.log.info(f"===== {self.name} =====")
        for g in self.groups.values():
            self.log.info(
                f"  {g.name:<12} {g.covered:>4}/{len(g.goal):<5} {g.percent:6.1f}%"
            )
            missing = g.missing()
            if missing and len(missing) <= 12:
                self.log.info(f"       missing: {missing}")
        return all(g.percent == 100.0 for g in self.groups.values())