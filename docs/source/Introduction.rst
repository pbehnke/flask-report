############
Introduction
############

*Flask-Report* is a flask plugin to display a list of records in web pages,
these list of records simply are query results. It is not a RAD tool like BIRT, 
you must write configurations to generate report. And it is not versatile as
other report engines. It is meant to be simple, easy to extend/re-develop (once
you understand it).

.. image:: /_static/infrastructure.png
  
Features
========

* reports are interactive, eg. filter on certain columns, sort by certain column
* downloaded as CSV
* drill down on certain column
* send reports through email periodically



Glossary
========

* Data Set
The definition of the query results. A report is a representation or projection
of a data set. You must define a data set before you could generate a report

* Report
Representaion of a list of records

* Notification
A series of scheduled report pushing actions (through emails).



Pages
=====

* /report-list

display a list of reports

* /report/<int:id>

display details of a given report

* /data-set-list

display a list of data set

* /data-set/<int:id>

display details ofa given data set

* /notification-list

display a list of notifications

* /notification/<int:id>

display details of a given notification
 
