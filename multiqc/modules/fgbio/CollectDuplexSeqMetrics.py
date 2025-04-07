#!/usr/bin/env python

""" MultiQC submodule to parse output from fgbio CollectDuplexSeqMetrics """

from multiqc.plots import linegraph


def parse_reports(self):
    family_sizes_data = parse_family_sizes(self)
    duplex_yield_metrics_data = parse_duplex_yield_metrics(self)

    if not family_sizes_data and not duplex_yield_metrics_data:
        return 0

    linegraph_data_simplex = [{}, {}]
    linegraph_data_duplex = [{}, {}]

    for sample, s_data in family_sizes_data.items():
        for fs, fs_data in s_data.items():
            linegraph_data_simplex[0].setdefault(sample, {})[fs] = fs_data["ss_count"]
            linegraph_data_simplex[1].setdefault(sample, {})[fs] = fs_data["ss_fraction"]
            linegraph_data_duplex[0].setdefault(sample, {})[fs] = fs_data["ds_count"]
            linegraph_data_duplex[1].setdefault(sample, {})[fs] = fs_data["ds_fraction"]

    metric_keys = [
        "ds_fraction_duplexes",
        "ds_fraction_duplexes_ideal",
        "ds_duplexes",
        "ds_families",
        "ss_families",
        "cs_families",
        "read_pairs"
    ]
    linegraph_data_yield = [{s: {} for s in duplex_yield_metrics_data} for _ in metric_keys]

    for sample, s_data in duplex_yield_metrics_data.items():
        for fraction, row in s_data.items():
            for i, key in enumerate(metric_keys):
                linegraph_data_yield[i][sample][fraction] = row[key]

    def config_plot(id_, title, xlab, labels):
        return {
            "id": id_,
            "title": title,
            "ylab": "Count",
            "xlab": xlab,
            "xDecimals": not "size" in xlab,
            "tt_label": "<b>{point.x}</b>: {point.y}",
            "data_labels": [{"name": l, "ylab": l} for l in labels],
        }

    pconfig_simplex = config_plot(
        "fgbio_CollectDuplexSeqMetrics_simplex_family_sizes",
        "Fgbio: Frequency of simplex family sizes",
        "Simplex family size",
        ["Count", "Fraction"]
    )

    pconfig_duplex = config_plot(
        "fgbio_CollectDuplexSeqMetrics_duplex_family_sizes",
        "Fgbio: Frequency of duplex family sizes",
        "Duplex family size",
        ["Count", "Fraction"]
    )

    pconfig_yield = {
        "id": "fgbio_CollectDuplexSeqMetrics_duplex_yield_metrics",
        "title": "Fgbio: Duplex yield metrics",
        "xlab": "Downsampling percentage",
        "xDecimals": True,
        "tt_label": "<b>percentage downsampled {point.x}</b>: {point.y}",
        "data_labels": [{"name": key.replace('_', ' ').capitalize(), "ylab": key.replace('_', ' ').capitalize()} for key in metric_keys],
    }

    self.add_section(
        name="Duplex family sizes",
        anchor="fgbio-frequency-duplex-family-sizes",
        description="Plot showing duplex tag family size distribution.",
        plot=linegraph.plot(linegraph_data_duplex, pconfig_duplex),
    )

    self.add_section(
        name="Simplex family sizes",
        anchor="fgbio-frequency-simplex-family-sizes",
        description="Plot showing simplex tag family size distribution.",
        plot=linegraph.plot(linegraph_data_simplex, pconfig_simplex),
    )

    self.add_section(
        name="Duplex yield metrics",
        anchor="fgbio-duplex-yield-metrics",
        description="Duplex yield metrics at different downsampling levels.",
        plot=linegraph.plot(linegraph_data_yield, pconfig_yield),
    )

    return len(family_sizes_data)


def parse_family_sizes(self):
    parsed_data = {}

    type_map = {
        "family_size": int,
        "ss_count": int,
        "ss_fraction": float,
        "ds_count": int,
        "ds_fraction": float,
        "cs_count": int,
        "cs_fraction": float,
        "families": int,
        "fraction": float,
        "tag_family_size": float,
    }

    for f in self.find_log_files("fgbio/collectduplexseqmetrics_family_sizes", filehandles=True):
        s_name = f["s_name"]
        fh = f["f"]
        header = fh.readline().strip().split("\t")
        if not header or "family_size" not in header:
            continue

        s_data = {}
        for line in fh:
            fields = line.strip().split("\t")
            if len(fields) != len(header):
                continue
            row = dict(zip(header, fields))
            for key in row:
                row[key] = type_map.get(key, str)(row[key])
            s_data[row["family_size"]] = row

        if s_data:
            parsed_data[s_name] = s_data

    parsed_data = self.ignore_samples(parsed_data)
    if parsed_data:
        self.write_data_file(parsed_data, "multiqc_fgbio_CollectDuplexSeqMetrics_family_sizes")
    return parsed_data


def parse_duplex_yield_metrics(self):
    parsed_data = {}

    type_map = {
        "fraction": float,
        "read_pairs": int,
        "cs_families": int,
        "ss_families": int,
        "ds_families": int,
        "ds_duplexes": int,
        "ds_fraction_duplexes_ideal": float,
        "ds_fraction_duplexes": float,
    }

    for f in self.find_log_files("fgbio/collectduplexseqmetrics_yield_metrics", filehandles=True):
        s_name = f["s_name"]
        fh = f["f"]
        header = fh.readline().strip().split("\t")
        if not header or "fraction" not in header:
            continue

        s_data = {}
        for line in fh:
            fields = line.strip().split("\t")
            if len(fields) != len(header):
                continue
            row = dict(zip(header, fields))
            for key in row:
                row[key] = type_map.get(key, str)(row[key])
            s_data[row["fraction"]] = row

        if s_data:
            parsed_data[s_name] = s_data

    parsed_data = self.ignore_samples(parsed_data)
    if parsed_data:
        self.write_data_file(parsed_data, "multiqc_fgbio_CollectDuplexSeqMetrics_duplex_yield_metrics")
    return parsed_data
