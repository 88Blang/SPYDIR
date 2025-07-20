from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle, Paragraph, ListFlowable, ListItem
from reportlab.lib import colors
import pandas as pd
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


default_hex = "#7798AB"
c1 = colors.HexColor(default_hex)


header_style = {
    "BACKGROUND": colors.aqua,  # c1,
    "TEXTCOLOR": colors.whitesmoke,
    "FONTNAME": "Helvetica-Bold",
    "FONTSIZE": 20,
    "PADDING": 10,
    "BOTTOMPADDING": 4,
    "ALIGN": "LEFT",
    "VALIGN": "MIDDLE",
}

index_style = {
    "BACKGROUND": colors.plum,  # colors.white,
    "FONTNAME": "Helvetica-Bold",
    "ALIGN": "LEFT",
}

body_style = {
    "BACKGROUND": colors.red,
    "FONTNAME": "Helvetica",
    "ALIGN": "RIGHT",
}


# Measure text width in points
def text_width(text, font="Helvetica", font_size=10):
    return pdfmetrics.stringWidth(str(text), font, font_size)


def get_widths(data, style=body_style):
    col_widths = []
    for col_idx in range(len(data[0])):
        col_data = [str(row[col_idx]) for row in data]
        max_width = max(
            text_width(cell, font=style["font_name"], font_size=style["font_size"])
            for cell in col_data
        )
        col_widths.append(max_width + style["padding"])
    return col_widths


def compute_column_widths(total_width, weights):
    """
    Computes column widths proportional to given weights.

    Args:
        total_width (float): Total width to be divided.
        weights (list of int/float): Relative weight of each column.

    Returns:
        list of float: Widths for each column.
    """
    total_weight = sum(weights)
    unit_width = total_width / total_weight
    return [w * unit_width for w in weights]


def get_table_style(style=body_style, table_data=None, add_stripes=True):
    """
    Create a default TableStyle with font and layout settings.

    Args:
        style (dict): Dictionary with keys 'font_name' and 'font_size'.
        table_data (list, optional): The table data to apply striped rows if enabled.
        add_stripes (bool): Whether to add alternating background stripes for rows.

    Returns:
        TableStyle: A configured TableStyle object.
    """
    base_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), style.get("ALIGN", "CENTER")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), style.get("FONTNAME", "Helvetica")),
        ("FONTSIZE", (0, 0), (-1, -1), style.get("FONTSIZE", 10)),
    ]

    # Add striped row backgrounds if requested and table_data is provided
    if add_stripes and table_data is not None:
        for row_idx in range(1, len(table_data)):
            if row_idx % 2 == 0:
                base_style.append(
                    ("BACKGROUND", (0, row_idx), (-1, row_idx), colors.lightgrey)
                )

    return TableStyle(base_style)


def row_table(
    data_dict,
    cols=None,
    width=None,
    style=None,
    wrap=True,
    index=False,
):
    df = pd.DataFrame(data_dict)

    # Build table data including index
    if index:
        data = [[df.index.name or ""] + df.columns.tolist()]
        data += [[idx] + row.tolist() for idx, row in zip(df.index, df.values)]
    else:
        data = [df.columns.tolist()] + df.values.tolist()

    # Determine column widths
    if width and cols:
        col_widths = compute_column_widths(total_width=width, weights=cols)
    elif width:
        col_width = width / len(data[0])
        col_widths = [col_width for _ in range(len(data[0]))]
    else:
        col_widths = get_widths(data, style)

    # Wrap cells with Paragraphs if needed
    if wrap:
        data = [
            [Paragraph(str(cell), styles["Normal"]) for cell in row] for row in data
        ]

    # Create the table
    table = Table(data, colWidths=col_widths)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), c1),  # Header background
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),  # Header text color
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),  # HEADER
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),  # header
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Header font
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),  # Header padding
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),  # 'index'
                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "RIGHT",
                ),  # second col
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.white,
                ),  # index/body
            ]
        )
    )

    return table


def statement_table(data_dict, cols=None, width=None, style=body_style):
    cols = [1 for _ in range(len(list(data_dict.keys())))]
    cols[0] = 3
    table = row_table(
        data_dict,
        cols=cols,
        width=width,
        index=True,
    )
    return table


def create_list(story, list_of_items, style):
    list_items = [
        ListItem(Paragraph(item, style), spaceAfter=6) for item in list_of_items
    ]

    story.append(ListFlowable(list_items, bulletType="bullet"))


def create_link_list(story, source_list, style):
    link_list = []
    for item in source_list:
        link_list.append(f'<a href="{item.get('link','')}">{item.get('title','')}</a>')
    create_list(story, list_of_items=link_list, style=style)
