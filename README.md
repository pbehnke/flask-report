Flask-Report
============

*Flask-Report* is a [Flask](flask.pooco.org) plugin. I write this plugin to generate interactive reports in web pages. It supports several types of representations:
    
    * list table 
    * pie chart
    * curve chart
    * bar chart

And the reports could be downloaded as CSV.


Quick Start
-----------

```
$ git clone https://github.com/puzheng/flask-report.git
$ cd flask-report
$ pip install -r requirements.txt
$ python setup.py install
$ ./make_test_data.sh
$ cd flask_report; sass --update static/sass;static/css
$ python example
```
then open *http://127.0.0.1:5001/report/report/1* to see what happens.


[Documentaions](https://puzheng.github.io/flask-report)

[Screenshots](https://puzheng.github.io/flask-report/Screenshots.html)
