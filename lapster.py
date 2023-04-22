import collections
import heapq
import json
import plotly

GLOBAL_SECTORS_TIME = {}
GLOBAL_POINTERS_TIME = {}

GLOBAL_SECTORS_DELTAS = {}
GLOBAL_POINTERS_DELTAS = {}

X_SECTOR = [str(i) for i in range(1, 5)]
X_POINTERS = [str(i) for i in range(1, 13)]


###############################################################################
#                                GET LAP DATA                                 #
###############################################################################

with open("laps.json", "r") as laps_file:
    LAPS_DATA = json.load(laps_file)

for lap_name, lap_frames in LAPS_DATA["laps"].items():
    # TAG: 0/14
    # pointers_time = [(int(lap_frames[str(x+1)]) - int(lap_frames[str(x)])) / 59.94 for x in range(0, 14)]
    pointers_time = [(int(lap_frames[str(x+1)]) - int(lap_frames[str(x)])) / 59.94 for x in range(1, 13)]
    GLOBAL_POINTERS_TIME[lap_name] = pointers_time

    sectors_times = [
        (int(lap_frames["5"]) - int(lap_frames["1"])) / 59.94,
        (int(lap_frames["8"]) - int(lap_frames["5"])) / 59.94,
        (int(lap_frames["11"]) - int(lap_frames["8"])) / 59.94,
        (int(lap_frames["13"]) - int(lap_frames["11"])) / 59.94
    ]
    GLOBAL_SECTORS_TIME[lap_name] = sectors_times

MIN_SECTORS_TIME = [min([sector_time[x] for sector_time in GLOBAL_SECTORS_TIME.values()]) for x in range(0, 4)]
# TAG: 0/14
# MIN_POINTERS_TIME = [min([pointer_time[x] for pointer_time in GLOBAL_POINTERS_TIME.values()]) for x in range(0, 14)]
MIN_POINTERS_TIME = [min([pointer_time[x] for pointer_time in GLOBAL_POINTERS_TIME.values()]) for x in range(0, 12)]

MIN_2_SECTORS_TIME = [heapq.nsmallest(2, [sector_time[x] for sector_time in GLOBAL_SECTORS_TIME.values()]) for x in range(0, 4)]
MAX_2_SECTORS_TIME = [heapq.nlargest(2, [sector_time[x] for sector_time in GLOBAL_SECTORS_TIME.values()]) for x in range(0, 4)]

# TAG: 0/14
# MIN_2_POINTERS_TIME = [heapq.nsmallest(2, [sector_time[x] for sector_time in GLOBAL_POINTERS_TIME.values()]) for x in range(0, 14)]
MIN_2_POINTERS_TIME = [heapq.nsmallest(2, [sector_time[x] for sector_time in GLOBAL_POINTERS_TIME.values()]) for x in range(0, 12)]
# TAG: 0/14
# MAX_2_POINTERS_TIME = [heapq.nlargest(2, [sector_time[x] for sector_time in GLOBAL_POINTERS_TIME.values()]) for x in range(0, 14)]
MAX_2_POINTERS_TIME = [heapq.nlargest(2, [sector_time[x] for sector_time in GLOBAL_POINTERS_TIME.values()]) for x in range(0, 12)]


for lap_name, sector_time in GLOBAL_SECTORS_TIME.items():
    GLOBAL_SECTORS_DELTAS[lap_name] = [sector_time[x] - MIN_SECTORS_TIME[x] for x in range(0, 4)]

for lap_name, pointer_time in GLOBAL_POINTERS_TIME.items():
    GLOBAL_POINTERS_DELTAS[lap_name] = [pointer_time[x] - MIN_POINTERS_TIME[x] for x in range(0, 12)]

GLOBAL_SECTORS_DELTAS = collections.OrderedDict(sorted(GLOBAL_SECTORS_DELTAS.items()))
GLOBAL_POINTERS_DELTAS = collections.OrderedDict(sorted(GLOBAL_POINTERS_DELTAS.items()))

###############################################################################
#                                CREATE GRAPH                                 #
###############################################################################

GRAPH_SECTORS = plotly.graph_objects.Figure()
GRAPH_POINTERS = plotly.graph_objects.Figure()

counter = 0
for lap_name, sector_deltas in GLOBAL_SECTORS_DELTAS.items():
    if counter > 5:
        GRAPH_SECTORS.add_trace(plotly.graph_objects.Scatter(x=X_SECTOR, y=sector_deltas, name="-".join(lap_name.split("-")[:-1]), line={"width":2}, visible="legendonly"))
    else:
        GRAPH_SECTORS.add_trace(plotly.graph_objects.Scatter(x=X_SECTOR, y=sector_deltas, name="-".join(lap_name.split("-")[:-1]), line={"width":2}))
    counter += 1
GRAPH_SECTORS.update_layout(paper_bgcolor="#2C3034", template="plotly_dark")
# plotly.offline.plot(GRAPH_SECTORS, filename="./sectors.html", auto_open=False)
GRAPH_SECTORS_DIV = plotly.io.to_html(GRAPH_SECTORS, include_plotlyjs=False, default_width='90%', default_height='100%', div_id="graph_sectors")

counter = 0
for lap_name, pointers_deltas in GLOBAL_POINTERS_DELTAS.items():
    if counter > 5:
        GRAPH_POINTERS.add_trace(plotly.graph_objects.Scatter(x=X_POINTERS, y=pointers_deltas, name="-".join(lap_name.split("-")[:-1]), line={"width":2}, visible="legendonly"))
    else:
        GRAPH_POINTERS.add_trace(plotly.graph_objects.Scatter(x=X_POINTERS, y=pointers_deltas, name="-".join(lap_name.split("-")[:-1]), line={"width":2}))
    counter +=1
GRAPH_POINTERS.update_layout(paper_bgcolor="#2C3034", template="plotly_dark")
# plotly.offline.plot(GRAPH_POINTERS, filename="./pointers.html", auto_open=False)
GRAPH_POINTERS_DIV = plotly.io.to_html(GRAPH_POINTERS, include_plotlyjs=False, default_width='90%', default_height='100%', div_id="graph_pointers")

###############################################################################
#                              CREATE TABLE HTML                              #
###############################################################################

def split_dict(dict_data, dict_size):
    keys = list(dict_data.keys())
    for i in range(0, len(keys), dict_size):
        yield {k: dict_data[k] for k in keys[i: i + dict_size]}

def create_table_html(table_name, sector_time_data, sector_delta_data, x_graph_len, min_sectors_time, max_sector_time):
    table_html = ""
    table_template = """
    <table class="{} table table-dark table-striped table-sm table-hover rounded rounded-3 overflow-hidden table-fixed">
        <thead>
            <tr>
                <th scope="col">#</th>
                {}
            </tr>
        </thead>
        <tbody>
            {}
        </tbody>
    <table>
    """
    for sector_data in split_dict(collections.OrderedDict(sorted(sector_time_data.items())), 10):
        lap_header_html = ""
        for lap_counter, lap_name in enumerate(sector_data.keys()):
            if lap_counter > len(plotly.colors.qualitative.Plotly):
                color = plotly.colors.qualitative.Plotly[lap_counter % len(plotly.colors.qualitative.Plotly)]
            else:
                color = plotly.colors.qualitative.Plotly[lap_counter]
            kart_number = lap_name.split("-")[-1]
            lap_name = "-".join(lap_name.split("-")[:-1])
            lap_header_html += "<th title=\"{}\" id=\"{}\" scope=\"col\" style=\"color:{}\"><span onclick=\"show_video(event)\">🎞️</span><span onclick=\"show_line(event)\">{}</span></th>\n".format(kart_number, lap_name, color, lap_name)
        for i in range(lap_counter, 9):
            lap_header_html += "<th scope=\"col\">-</th>\n"

        all_sector_times = {}
        # # TAG: 0/14
        # for i in range(0, x_graph_len + 2):
        for i in range(0, x_graph_len):
            all_sector_times[i] = []

        for sector_times in sector_data.values():
            for sector_index, sector_time in enumerate(sector_times):
                all_sector_times[sector_index].append(sector_time)

        for sector_index, sector_times in all_sector_times.items():
            if len(sector_times) < 10:
                for i in range(len(sector_times), 10):
                    all_sector_times[sector_index].append("-")

        lap_time_html = ""
        sector_counter = 1
        for sector_times in all_sector_times.values():
            sector_rows_html = "<tr>\n"
            # TAG: 0/14
            # sector_rows_html += "<th scope=\"row\">{}</th>\n".format(sector_counter - 1)
            sector_rows_html += "<th scope=\"row\">{}</th>\n".format(sector_counter)
            lap_counter = 0
            for sector_time in sector_times:
                if sector_time == "-":
                    sector_rows_html += "<td>{}</td>\n".format(sector_time)
                else:
                    if sector_time in min_sectors_time[sector_counter - 1]:
                        sector_rows_html += "<td class=\"top_sector\">{:.4f} (+{:.2f})</td>\n".format(sector_time, sector_delta_data[list(sector_data)[lap_counter]][sector_counter - 1])
                    elif sector_time in max_sector_time[sector_counter - 1]:
                        sector_rows_html += "<td class=\"bottom_sector\">{:.4f} (+{:.2f})</td>\n".format(sector_time, sector_delta_data[list(sector_data)[lap_counter]][sector_counter - 1])
                    else:
                        sector_rows_html += "<td>{:.4f} (+{:.2f})</td>\n".format(sector_time, sector_delta_data[list(sector_data)[lap_counter]][sector_counter - 1])
                    lap_counter += 1
            sector_rows_html += "</tr>\n"

            sector_counter += 1
            lap_time_html += sector_rows_html

        table_html += table_template.format(table_name, lap_header_html, lap_time_html)

    return table_html


sectors_table_html = create_table_html("sectors_table", GLOBAL_SECTORS_TIME, GLOBAL_SECTORS_DELTAS, len(X_SECTOR), MIN_2_SECTORS_TIME, MAX_2_SECTORS_TIME)
pointers_table_html = create_table_html("pointers_table", GLOBAL_POINTERS_TIME, GLOBAL_POINTERS_DELTAS, len(X_POINTERS), MIN_2_POINTERS_TIME, MAX_2_POINTERS_TIME)


with open("template_index.html", "r") as template_file:
    TEMPLATE_HTML = template_file.read()

with open("index.html", "w") as template_file:
    template_file.write(TEMPLATE_HTML\
        .replace("%%SECTORS-TABLE%%", sectors_table_html)\
        .replace("%%POINTERS-TABLE%%", pointers_table_html)\
        .replace("%%SECTORS-GRAPH%%", GRAPH_SECTORS_DIV.replace("height:100%; width:90%;", "height:100%; width:90%; margin:auto"))\
        .replace("%%POINTERS-GRAPH%%", GRAPH_POINTERS_DIV.replace("height:100%; width:90%;", "height:100%; width:90%; margin:auto"))

    )
