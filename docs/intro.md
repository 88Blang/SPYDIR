# Stock Analysis in Python

Key Features:

- Caching System: Uses a simple key-value store (Python dictionary) to cache API calls.
- JSON Compatible: Cache structure supports JSON serialization for web or API integration.
- Report Generation: Capable of producing Excel spreadsheets and PDF reports.


See `docs/AAPL_Report.pdf` for an example report generated by the code below:
```python
from SPYDIR import Stock
aapl_stock = Stock('AAPL')
aapl_stock.create_report()
```


## Install:
```
pip install git+https://github.com/88Blang/SPYDIR.git
```