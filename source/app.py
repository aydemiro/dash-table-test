import base64
import io
import csv
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table

app = Dash(__name__)
server = app.server

app.layout = html.Div(
	[
		html.H2("Interactive CSV / TSV Viewer"),
		dcc.Upload(
			id="upload-data",
			children=html.Div(
				["Drag and drop a CSV/TSV file here or ", html.A("select a file")]
			),
			style={
				"width": "100%",
				"height": "80px",
				"lineHeight": "80px",
				"borderWidth": "1px",
				"borderStyle": "dashed",
				"borderRadius": "5px",
				"textAlign": "center",
			},
			multiple=False,
		),
		html.Div(
			[
				html.Label("Delimiter:"),
				dcc.RadioItems(
					id="delimiter",
					options=[
						{"label": "Auto", "value": "auto"},
						{"label": "Comma (,)", "value": ","},
						{"label": "Tab (\\t)", "value": "\t"},
						{"label": "Semicolon (;)", "value": ";"},
					],
					value="auto",
					inline=True,
				),
			],
			style={"marginTop": "10px"},
		),
		html.Div(id="file-name", style={"marginTop": "10px", "fontStyle": "italic"}),
		html.Div(id="output-table", style={"marginTop": "10px"}),
	],
	style={"maxWidth": "1200px", "margin": "20px auto"},
)


def detect_delimiter(sample: str) -> str:
	"""
	Try to detect delimiter from a sample string using csv.Sniffer.
	Fallback: tab if '\t' in sample else comma.
	"""
	try:
		dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
		return dialect.delimiter
	except Exception:
		return "\t" if "\t" in sample else ","


def parse_contents(contents: str, filename: str, delimiter_choice: str) -> pd.DataFrame:
	content_type, content_string = contents.split(",", 1)
	decoded = base64.b64decode(content_string)
	# Try to interpret as text
	for encoding in ("utf-8", "latin-1", "utf-16"):
		try:
			text = decoded.decode(encoding)
			break
		except Exception:
			text = None
	if text is None:
		# as fallback, try pandas to read from bytes
		buffer = io.BytesIO(decoded)
		try:
			return pd.read_csv(buffer)
		except Exception:
			raise ValueError("Could not decode uploaded file.")
	# Choose delimiter
	if delimiter_choice == "auto":
		sample = text[:4096]
		delim = detect_delimiter(sample)
	else:
		delim = delimiter_choice
	# Use pandas to parse
	try:
		df = pd.read_csv(io.StringIO(text), sep=delim, engine="python")
	except Exception as e:
		raise ValueError(f"Error parsing file with delimiter {repr(delim)}: {e}")
	# Rename dataframe columns to strings to match column ids
	df = df.rename(columns=lambda c: str(c))
	
	return df


@app.callback(
	Output("file-name", "children"),
	Output("output-table", "children"),
	Input("upload-data", "contents"),
	Input("delimiter", "value"),
	State("upload-data", "filename"),
)
def update_output(contents, delimiter_choice, filename):
	if contents is None:
		return "", html.Div("No file uploaded yet.", style={"color": "#666"})
	try:
		df = parse_contents(contents, filename, delimiter_choice)
	except Exception as e:
		return (
			filename or "",
			html.Div(f"Failed to parse file: {e}", style={"color": "red"}),
		)
	# Build DataTable
	columns = [{"name": str(col), "id": str(col)} for col in df.columns]
	data = df.to_dict("records")
	page_size = 20
	virtualize = len(df) > 1000

	table = dash_table.DataTable(
		id="table",
		columns=columns,
		data=data,
		page_size=page_size,
		page_action="native",
		filter_action="native",
		sort_action="native",
		sort_mode="multi",
		column_selectable="single",
		row_selectable="multi",
		selected_rows=[],
		editable=True,
		export_format="csv",
		export_headers="display",
		style_table={"overflowX": "auto"},
		style_cell={
			"minWidth": "100px",
			"maxWidth": "400px",
			"whiteSpace": "normal",
			"textAlign": "left",
		},
		virtualization=virtualize,
	)

	info = html.Div(
		[
			html.Div(f"Loaded: {filename}"),
			html.Div(f"Rows: {len(df)}, Columns: {len(df.columns)}"),
		],
		style={"marginBottom": "8px"},
	)

	return filename or "", html.Div([info, table])


if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True, port=8789)
