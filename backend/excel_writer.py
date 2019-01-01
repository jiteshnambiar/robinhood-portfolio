import pandas as pd
import xlsxwriter

"""
Creates New Excel Workbook
Usage:
>> xls = ExcelWriter(filename)
>> xls.add_sheet('sheet1', data_frame1)
>> xls.add_sheet('sheet2', data_frame2)
>> xls.default_formatting('sheet2')
>> xls.save()
"""


class ExcelWriter(object):
    def __init__(self, filename):
        """
        https://xlsxwriter.readthedocs.io/working_with_pandas.html

        # Create a Pandas dataframe from the data.
        df = pd.DataFrame({'Data': [10, 20, 30, 20, 15, 30, 45]})

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name='Sheet1')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
        """
        self.filename = filename + '.xlsx'
        self.writer = pd.ExcelWriter(self.filename)
        self.workbook = self.writer.book
        self.sheets = {}

    def add_sheet(self, sheetname, data_frame):
        if sheetname in self.sheets:
            raise Exception("Sheet already exists: [%s]" % sheetname)
        data_frame.to_excel(self.writer, sheet_name=sheetname)
        self.sheets[sheetname] = self.writer.sheets[sheetname]

    def writesheet(self, sheetname, data_frame):
        data_frame.to_excel(self.workbook, sheet_name=sheetname)

    def add_cell_format(self, bg_color, font_color):
        # Add a format with bg_color background fill and font_color text.
        return self.workbook.add_format({'bg_color': bg_color,
                                       'font_color': font_color})

    def freeze_top_row(self, sheetname):
        self.sheets[sheetname].freeze_panes(1, 0)

    def freeze_first_column(self, sheetname):
        self.sheets[sheetname].freeze_panes(0, 1)

    def adjust_column_width(self, sheetname):
        for colname, width in self.columnwidth[sheetname].items():
            self.sheets[sheetname].set_column(self.headerindex[sheetname][colname],
                                              self.headerindex[sheetname][colname], width)

    def default_formatting(self, sheetname):
        if sheetname not in self.sheets:
            raise Exception("Sheet doesn't exist: [%s]" % sheetname)
        # Add a format. Light red fill with dark red text.
        format_red = self.workbook.add_format({'bg_color': '#FFC7CE',
                                       'font_color': '#9C0006'})

        # Add a format. Green fill with dark green text.
        format_green = self.workbook.add_format({'bg_color': '#C6EFCE',
                                       'font_color': '#006100'})

        # self.adjust_column_width(sheetname)
        self.freeze_top_row(sheetname)
        self.freeze_first_column(sheetname)
        # Highlight Cells greater than 0.6 to show green
        row_count = self.sheets[sheetname].dim_rowmax
        column_count = self.sheets[sheetname].dim_colmax
        first_col = 'B'
        first_row = 2
        last_col = xlsxwriter.utility.xl_col_to_name(column_count)
        last_row = row_count + 1
        range = first_col + str(first_row) + ':' + last_col + str(last_row)
        self.sheets[sheetname].conditional_format(range, {'type': 'cell',
                                                'criteria': '>=',
                                                'value': 0.6,
                                                'format': format_green})

        # Highlight Cells less than -0.6 to show red
        self.sheets[sheetname].conditional_format(range, {'type': 'cell',
                                                'criteria': '<',
                                                'value': -0.6,
                                                'format': format_red})

    #########
    # Close #
    #########
    def save(self):
        # self.workbook.save()
        self.workbook.close()

    def close(self):
        self.save()