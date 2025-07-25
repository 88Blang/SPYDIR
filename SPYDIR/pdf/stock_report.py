# import os
import plotly.graph_objects as go
from plotly.io import write_image
import pandas as pd
from io import BytesIO

import numpy as np
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Image,
    NextPageTemplate,
    FrameBreak,
    Table,
    TableStyle,
    ListFlowable,
    Spacer,
    NextPageTemplate,
    ListItem,
)
from reportlab.lib.colors import HexColor  # for c1
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from SPYDIR.utils.helpers import *

sample_styles = getSampleStyleSheet()

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


# Var
## Size ref
offset = inch / 100
rem = inch / 4
page_width, page_height = letter
main_column_width = 2 * page_width / 3
side_column_width = page_width / 3
col_start_height = page_height - 2.5 * inch


class Stock_Template(BaseDocTemplate):
    """
    Stock Report Template for PDF document
    """

    def __init__(self, filename, **kw):
        super().__init__(
            filename,
            pagesize=letter,
            leftMargin=0,
            topMargin=0,
            rightMargin=0,
            bottomMargin=0,
            **kw,
        )
        self.setup_page_templates()

    def setup_page_templates(self):

        ## Set Frames
        self.width, self.height = self.pagesize

        main_column_width = 2 * self.width / 3
        side_column_width = self.width / 3

        header_height = inch
        footer_height = inch
        body_height = self.height - header_height - footer_height

        ## Header // Title
        self.title_frame = Frame(
            x1=0,
            y1=self.height,
            width=self.width,
            height=header_height,
            showBoundary=0,
        )

        ## Page 1
        main_col_start = rem
        side_col_start = main_column_width

        left_main_col_frame = Frame(
            x1=main_col_start,
            y1=footer_height,
            width=main_column_width - 2 * rem,
            height=body_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            showBoundary=0,
        )
        right_side_col_frame = Frame(
            x1=side_col_start,
            y1=footer_height,
            width=side_column_width - rem,
            height=body_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            showBoundary=0,
        )

        ## Page 2
        main_col_start = side_column_width + rem
        side_col_start = rem
        bottom_height = 1.5 * inch

        right_main_col_frame = Frame(
            x1=main_col_start,
            y1=footer_height + bottom_height,
            width=main_column_width - 2 * rem,
            height=body_height - bottom_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            showBoundary=0,
        )

        left_side_col_frame = Frame(
            x1=side_col_start,
            y1=footer_height + bottom_height,
            width=side_column_width - rem,
            height=body_height - bottom_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            showBoundary=0,
        )

        bottom_frame = Frame(
            x1=side_col_start,
            y1=footer_height + rem / 2,  # table move up an inch
            width=self.width - 2 * rem,
            height=bottom_height + 3 * inch / 4,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            showBoundary=0,
        )

        ## Page 3
        main_body_frame = Frame(
            x1=side_col_start,
            y1=footer_height,
            width=self.width - 2 * rem,
            height=body_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            showBoundary=0,
        )

        first_page = PageTemplate(
            id="first_page",
            frames=[
                self.title_frame,
                left_main_col_frame,
                right_side_col_frame,
            ],
            onPage=self._draw_page_1,
            onPageEnd=self._page_header,
        )
        second_page = PageTemplate(
            id="second_page",
            frames=[
                self.title_frame,
                right_main_col_frame,
                left_side_col_frame,
                bottom_frame,
            ],
            onPage=self._draw_page_2,
            onPageEnd=self._page_header,
        )
        third_page = PageTemplate(
            id="third_page",
            frames=[
                self.title_frame,
                main_body_frame,
            ],
            onPage=self._draw_page_3,
            onPageEnd=self._page_header,
        )

        self.addPageTemplates(
            [
                first_page,
                second_page,
                third_page,
            ]
        )

    def setup_style(self):

        # Styles
        self.normal_style = sample_styles["Normal"]
        self.title_style = sample_styles["Title"]

        default_hex = "#7798AB"
        # self.c1 = colors.HexColor(default_hex)
        self.c1 = get_img_color(self.logo)

        self.h1_style = sample_styles["Heading1"]
        self.h1_style.textColor = self.c1

        self.h2_style = sample_styles["Heading2"]
        self.h2_style.textColor = self.c1
        self.h2_style.fontName = "Helvetica-Bold"

        self.h3_style = sample_styles["Heading3"]
        self.h3_style.textColor = self.c1
        self.h3_style.fontName = "Helvetica-Bold"

    def _page_header(self, canvas, doc):
        canvas.saveState()

        ## Header
        title = self.h1_style
        title.alignment = 1  # center
        report_title = f"{self.name} Stock Report"
        header_text = Paragraph(report_title, title)
        header_text.wrapOn(canvas, self.width, self.title_frame.height)
        header_text.drawOn(
            canvas,
            self.title_frame.x1,
            self.title_frame.y1 - 3 * rem,  # Positive goes down
        )

        try:
            img_path = self.logo
            img = Image(img_path)

            # Natural size
            natural_width, natural_height = img.wrap(0, 0)
            aspect_ratio = natural_width / natural_height

            # Target max dimensions
            max_height = 1 * inch - rem
            max_width = 2 * inch - rem

            # Scale proportionally to fit within both constraints
            scaled_height = min(max_height, max_width / aspect_ratio)
            scaled_width = scaled_height * aspect_ratio

            # Apply scaled dimensions
            img.drawHeight = scaled_height
            img.drawWidth = scaled_width

            # Top Right Position
            # x_position = (
            #     self.pagesize[0] - scaled_width - rem / 2
            # )  # Right-aligned within margin
            # y_position = (
            #     self.pagesize[1] - scaled_height - rem / 2
            # )  # Top-aligned within margin

            x_position = (
                self.width / 2 - scaled_width / 2
            )  # Right-aligned within margin
            y_position = (
                # scaled_height
                0.35
                * inch  # + rem  # Top-aligned within margin
            )

            img.drawOn(canvas, x_position, y_position)
        except:
            raise FileNotFoundError("IMG ERROR")

        ## Footer
        y_offset1 = 0.5 * inch  # Adjust Y for second line
        y_offset2 = 0.35 * inch  # Adjust Y for second line

        canvas.setFont("Times-Roman", 10)
        # Left
        canvas.drawString(inch / 2, y_offset1, f"{self.name} Report")
        canvas.drawString(inch / 2, y_offset2, f"Page: {doc.page}")
        # Right
        # canvas.drawRightString(self.width - inch / 2, y_offset1, f"Made with SPYDIR")
        canvas.drawRightString(self.width - inch / 2, y_offset2, f"Made with SPYDIR")

        canvas.restoreState()

    def _draw_page_1(self, canvas, doc):
        canvas.line(
            2 * self.width / 3 - 5 * offset,
            self.height - inch,
            2 * self.width / 3 - 5 * offset,
            self.height * 0.05,
        )
        canvas.line(
            rem,
            col_start_height + 1.5 * inch,
            self.width - rem,
            col_start_height + 1.5 * inch,
        )

    def _draw_page_2(self, canvas, doc):
        canvas.line(
            side_column_width + 5 * offset,
            self.height - inch,
            side_column_width + 5 * offset,
            3 * inch,
        )
        canvas.line(
            rem,
            col_start_height + 1.5 * inch,
            self.width - rem,
            col_start_height + 1.5 * inch,
        )

    def _draw_page_3(self, canvas, doc):
        canvas.line(
            rem,
            col_start_height + 1.5 * inch,
            self.width - rem,
            col_start_height + 1.5 * inch,
        )

    def build_story(self, context):
        self.logo = context.get("wiki", {}).get("img", "")
        self.name = context.get("name", "NAME NOT FOUND")
        self.ticker = context.get("ticker", "")

        self.setup_style()

        # add the various elements to the story
        story = []

        ## PAGE 1
        story.append(NextPageTemplate("second_page"))
        story = self._populate_page1(story, context)

        ## PAGE 2
        story.append(NextPageTemplate("third_page"))

        story = self._populate_page2(story, context)

        ## PAGE 3
        story = self._populate_page3(story, context)

        return story

    def _populate_page1(self, story: list, context: dict) -> list:

        ## Title content
        # EMPTY FOR TITLE
        story.append(FrameBreak())

        ## Profile
        story.append(Spacer(0, 10))
        story.append(Paragraph("Profile", self.h1_style))
        story.append(Paragraph(context["summary"]["yq"], self.normal_style))

        story.append(Spacer(0, 10))

        story.append(Spacer(0, 10))
        story.append(Paragraph("Company Officers", self.h2_style))

        co_df = pd.DataFrame(context["esg"]["company_officers"])[["Name", "Title"]]

        co_table = self.df_table(
            co_df,
            show_index=False,
            col_widths=None,
            width=main_column_width - 2 * rem,
            wrap=True,
        )

        story.append(co_table)

        story.append(FrameBreak())

        ## Snapshot Table
        story.append(Spacer(0, 10))

        profile_table = self.dict_table(data_dict=context["info"], title="Snapshot")
        story.append(profile_table)

        ## News
        story.append(Spacer(0, 10))

        story.append(Paragraph("News", self.h3_style))

        create_link_list(story, context["news"], self.normal_style)

        ## Sources
        story.append(Spacer(0, 10))

        story.append(Paragraph("Sources", self.h3_style))

        create_link_list(story, context["sources"], self.normal_style)

        story.append(FrameBreak())

        return story

    def _populate_page2(self, story: list, context: dict) -> list:

        # # title
        story.append(FrameBreak())

        ## Bull / Bear
        story.append(Spacer(0, 10))  # 10 points of vertical space
        story.append(Paragraph("Pitch", self.h1_style))

        if context["summary"]["pitch"]:
            story.append(Paragraph(context["summary"]["pitch"], self.normal_style))
        else:
            story.append(Paragraph("Analysis Not Available", self.normal_style))

        story.append(Spacer(0, 10))
        if context["summary"]["bull"]:
            story.append(Paragraph("Bull Case", self.h2_style))
            create_list(story, context["summary"]["bull"], self.normal_style)

        story.append(Spacer(0, 10))
        if context["summary"]["bear"]:
            story.append(Paragraph("Bear Case", self.h2_style))
            create_list(story, context["summary"]["bear"], self.normal_style)

        story.append(FrameBreak())

        ## Value Table
        story.append(Spacer(0, 10))
        val_table = self.dict_table(
            data_dict=context["financial"]["ratios"]["info"], title="Valuation"
        )
        story.append(val_table)

        story.append(Spacer(0, 25))
        val_table = self.dict_table(
            data_dict=context["analyst"]["info"], title="Rating"
        )
        story.append(val_table)

        story.append(FrameBreak())

        ## Peer Table
        story.append(Paragraph("Peer Metrics", self.h3_style))
        peer_table = self.dicts_table(
            context["related"],
            title="Peers",
            width=self.width - 2 * rem,
        )
        story.append(peer_table)

        story.append(FrameBreak())

        return story

    def _populate_page3(self, story: list, context: dict) -> list:

        ## Title
        story.append(FrameBreak())

        # Create image
        img_buffer = self.create_candlestick_chart(data=context["chart_data"])
        story.append(
            Image(img_buffer, width=main_column_width * 1.5, height=self.height / 2)
        )

        story.append(Paragraph("Technical Analysis", style=self.h1_style))
        story.append(Paragraph("Short Term:", style=self.h3_style))
        story.append(
            Paragraph(
                """The overall market sentiment is currently Bullish, with bearish events outweighing bullish events, as indicated by a score of 4, suggesting Very Strong Bullish Evidence. Despite this, the sector is showing a Neutral direction, supported by a 0, which reflects Neutral Evidence. However, the broader market index is also in a Bullish direction, with a score of 3, reinforcing Strong Bullish Evidence at the index level.""",
                style=self.normal_style,
            )
        )

        story.append(Paragraph("Long Term:", style=self.h3_style))
        story.append(
            Paragraph(
                """The long-term market outlook is currently Bearish, with bearish events consistently outweighing bullish events, as reflected by a score of 3, indicating Strong Bearish Evidence. In contrast, the sector is experiencing a Bullish trend, supported by a 2, signifying Bullish Evidence. However, when considering the broader market index, it is also trending in a Bullish direction, with a score of 2, reinforcing Bullish Evidence at the index level.""",
                style=self.normal_style,
            )
        )

        story.append(FrameBreak())
        story.append(FrameBreak())

        story.append(Spacer(0, 10))
        story.append(Paragraph("Income Statement:", style=self.h1_style))

        is_table = self.df_table(
            df=pd.DataFrame(context["statements"]["income_statement"]),
            show_index=True,
            col_widths=[2, 1, 1, 1, 1],
            width=main_column_width + 4 * rem,
            wrap=True,
        )
        story.append(is_table)

        story.append(FrameBreak())
        story.append(FrameBreak())

        story.append(Spacer(0, 10))
        story.append(Paragraph("Balance Sheet:", style=self.h1_style))

        bs_table = self.df_table(
            df=pd.DataFrame(context["statements"]["balance_sheet"]),
            show_index=True,
            col_widths=[2, 1, 1, 1, 1],
            width=main_column_width + 4 * rem,
            wrap=True,
        )
        story.append(bs_table)

        story.append(FrameBreak())
        story.append(FrameBreak())
        story.append(Spacer(0, 10))
        story.append(Paragraph("Cash Flow:", style=self.h1_style))

        cf_table = self.df_table(
            df=pd.DataFrame(context["statements"]["cash_flow"]),
            show_index=True,
            col_widths=[2, 1, 1, 1, 1],
            width=main_column_width + 4 * rem,
            wrap=True,
        )
        story.append(cf_table)

        story.append(FrameBreak())

        return story

    def df_table(
        self,
        df,
        show_index=True,
        col_widths=None,
        width=main_column_width - rem,
        wrap=False,
    ):

        if show_index:
            df.reset_index(inplace=True)
            df.rename(columns={"index": ""}, inplace=True)

        if not col_widths:
            col_width = width / (
                len(df.columns.tolist())
            )  # Adjust for double width of rec col
            colWidths = [col_width for _ in range(len(df.columns.tolist()))]
        else:
            total_weight = sum(col_widths)
            unit_width = width / total_weight
            colWidths = [w * unit_width for w in col_widths]

        table_data = [df.columns.tolist()] + df.values.tolist()

        if wrap:
            table_data = [
                [Paragraph(str(cell), self.normal_style) for cell in row]
                for row in table_data
            ]

        table = Table(table_data, colWidths=colWidths)  # Adjust column widths as needed

        # Define table style
        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), self.c1),  # Header background
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),  # Align text left by default
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),  # Align text left by default
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Header font
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),  # Header padding
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.white,
                ),
            ]
        )
        table.setStyle(table_style)
        # Add alternating gray background for rows, starting after the header
        for row_idx in range(1, len(table_data)):
            if row_idx % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [("BACKGROUND", (0, row_idx), (-1, row_idx), colors.lightgrey)]
                    )
                )
        return table

    def dict_table(self, data_dict, title, width=side_column_width - rem):

        table_data = [[title]]  # Header row
        for key, value in data_dict.items():
            table_data.append([key, f"{value}"])

        # Create the table
        table = Table(
            table_data, colWidths=[(width) / 2, (width) / 2]
        )  # Adjust column widths as needed

        # Define table style
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.c1),  # Header background
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
        # Add alternating gray background for rows, starting after the header
        for row_idx in range(1, len(table_data)):
            if row_idx % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [("BACKGROUND", (0, row_idx), (-1, row_idx), colors.lightgrey)]
                    )
                )

        return table

    def dicts_table(self, data_dict, title, cols=None, width=main_column_width - rem):

        if not cols:
            cols = list(data_dict[0].keys())
        header = cols
        col_width = width / (len(header) + 1)  # Adjust for double width of rec col
        try:
            col_widths = [col_width for _ in range(len(header))]
            col_widths[2] = col_width * 2  # double rec col
        except:
            return Table(["Not Available"])

        table_data = [header]  # Header row
        for item_dict in data_dict:
            if item_dict != {}:
                item_row = [f"{value}" for _, value in item_dict.items()]
                table_data.append(item_row)
        # Create the table
        table = Table(
            table_data, colWidths=col_widths
        )  # Adjust column widths as needed

        # Define table style
        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), self.c1),  # Header background
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),  # Align text left by default
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),  # Align text left by default
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Header font
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),  # Header padding
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.white,
                ),
            ]
        )
        table.setStyle(table_style)
        # Add alternating gray background for rows, starting after the header
        for row_idx in range(1, len(table_data)):
            if row_idx % 2 == 0:
                table.setStyle(
                    TableStyle(
                        [("BACKGROUND", (0, row_idx), (-1, row_idx), colors.lightgrey)]
                    )
                )
        return table

    def create_candlestick_chart(self, data):
        """
        Creates a candlestick chart using Plotly and saves it as an image.

        Args:
            data (dict): Dictionary containing 'open', 'high', 'low', 'close' values.
            image_file (str): Path to save the chart image.
        """
        candlestick = go.Candlestick(
            x=data["date"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            name="Candlestick",
        )

        # Add 5-day moving average line
        ma_5 = go.Scatter(
            x=data["date"],
            y=data["MA_5"],
            mode="lines",
            name="MA 5 Day",
            line=dict(color="rgba(24, 27, 212, 0.4)", width=1.5),
        )

        # Add 20-day moving average line
        ma_20 = go.Scatter(
            x=data["date"],
            y=data["MA_20"],
            mode="lines",
            name="MA 20 Day",
            line=dict(color="rgba(212, 24, 24, 0.4)", width=1.5),
        )

        # # Combine the data
        plot_data = [candlestick, ma_5, ma_20]

        layout = go.Layout(
            title=f"{self.name} Stock Chart with Moving Averages",
            xaxis=dict(title="Date"),
            yaxis=dict(
                title="Price",
                side="left",  # Move the y-axis to the right
            ),
            legend=dict(
                x=0.5,  # Center horizontally
                y=1,  # Place at the bottom
                xanchor="center",
                yanchor="top",
                orientation="h",
                bgcolor="rgba(255, 255, 255, 0.5)",  # Transparent background
                bordercolor="gray",
                borderwidth=1,
            ),
            template="plotly_white",
            xaxis_rangeslider_visible=False,
        )

        fig = go.Figure(data=plot_data, layout=layout)

        image_buffer = BytesIO()

        # Save as an image
        try:
            write_image(
                fig, image_buffer, format="png", width=1000, height=600, scale=4
            )
            image_buffer.seek(0)
            return image_buffer
        except Exception as e:

            print(e)


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
