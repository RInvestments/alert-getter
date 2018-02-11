# Alert Getter

Daily downloads the google alerts with RSS feeds. Idea is to download the RSS feed
from google alerts. Push it all onto mongodb for analysis/NLP later. Also
retrive raw text from those URLs.


## Author
Manohar Kuse <mpkuse@ust.hk>

## How to run
Setup a few RSS alerts in google alerts. Just Ctrl+S  https://www.google.com/alerts from
browser (I used chrome) in this folder with html file name as google-alerts.html.
You can configure a few params from the file `retrive_news_multi.py`.

```
python retrive_news_multi.py
```

If you wish to just wish to retrive everything once, try running `retrive_news.py`


## Prerequisits
- Pygoose (see [https://github.com/grangier/python-goose](https://github.com/grangier/python-goose))
