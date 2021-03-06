# -*- coding: UTF-8 -*-
import os
import functools

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint

from flask.ext.report import views
from flask.ext.report.notification import Notification
from flask.ext.report.report import Report


class FlaskReport(object):
    '''
    This is the class that add reports to a flask app.

    the usage is:

        app = Flask(__name__)
        db = SQLAlchemy(app)
        FlaskReport(app, db, )

    '''

    def __init__(self, app, db, models, blueprint=None, table_label_map=None,
                 mail=None):
        '''
        :param app: flask app instance
        :param db: database instance
        :param models: a list of models
        :param flaks.Blueprint blueprint: provide blueprint if you want register
            web pages under this blueprint
        :param dict table_label_map: a dict from table to label, the keys are
            the table name, the values are the labels of each table
        :param mail: the mail instance if you want send email, see
            `Flask-Mail <https://pypi.python.org/pypi/Flask-Mail>`_
        '''
        self.db = db
        self.app = app
        host = blueprint or app
        self.conf_dir = app.config.get("REPORT_CONFIG_DIR", "report-conf")
        self.report_dir = os.path.join(self.conf_dir, "reports")
        self.notification_dir = os.path.join(self.conf_dir, "notifications")
        self.data_set_dir = os.path.join(self.conf_dir, "data_sets")
        self.table_label_map = table_label_map or {}

        self._model_map = dict((model.__name__, model) for model in models)

        if not os.path.exists(self.conf_dir):
            os.makedirs(self.conf_dir)
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        if not os.path.exists(self.data_set_dir):
            os.makedirs(self.data_set_dir)

        host.add_url_rule("/report-list/", 'report_list',
                          functools.partial(views.report_list, self))
        host.add_url_rule("/graphs/report/<int:id_>", 'report_graphs',
                          functools.partial(views.report_graphs, self))
        report_view = functools.partial(views.report, self)
        host.add_url_rule("/report", 'report', report_view,
                          methods=['POST'])
        host.add_url_rule("/report/<int:id_>", 'report', report_view,
                          methods=['GET', 'POST'])
        host.add_url_rule("/report_csv/<int:id_>", 'report_csv',
                          functools.partial(views.report_csv, self))
        host.add_url_rule("/drill-down-detail/<int:report_id>/<int:col_id>",
                          'drill_down_detail',
                          functools.partial(views.drill_down_detail, self))

        host.add_url_rule("/data-set-list/", 'data_set_list',
                          functools.partial(views.data_set_list, self))
        host.add_url_rule("/data-set/<int:id_>", 'data_set',
                          functools.partial(views.data_set, self))
        host.add_url_rule("/notification-list", 'notification_list',
                          functools.partial(views.notification_list, self))
        view_func = functools.partial(views.notification, self)
        host.add_url_rule("/notification/<int:id_>", 'notification',
                          view_func,
                          methods=['GET', 'POST'])
        host.add_url_rule("/notification/", 'notification',
                          view_func,
                          methods=['GET', 'POST'])
        host.add_url_rule("/push_notification/<int:id_>", 'push_notification',
                          functools.partial(views.push_notification, self),
                          methods=['POST'])
        host.add_url_rule("/start_notification/<int:id_>", 'start_notification',
                          functools.partial(views.start_notification, self))
        host.add_url_rule("/stop_notification/<int:id_>", 'stop_notification',
                          functools.partial(views.stop_notification, self))
        host.add_url_rule("/schedule-list",
                          'schedule_listl',
                          functools.partial(views.schedule_list, self))

        # register it for using the templates of data browser
        self.blueprint = Blueprint("report____", __name__,
                                   static_folder="static",
                                   template_folder="templates")
        app.register_blueprint(self.blueprint, url_prefix="/__report__")

        @app.template_filter("dpprint")
        def dict_pretty_print(value):
            if isinstance(value, list):
                return '[' + ', '.join(dict_pretty_print(i) for i in value) + \
                    ']'
            return '{' + ','.join('%s:%s' % (k, v) for k, v in value.items()) \
                + '}'

        if mail:
            self.mail = mail
            self.sched = BackgroundScheduler()
            self.sched.start()

            with app.test_request_context():
                for notification in self.notifications:
                    if notification.enabled:
                        self.start_notification(notification.id_)

    @property
    def notifications(self):
        if os.path.exists(self.notification_dir):
            return [Notification(self, id_) for id_ in
                    os.listdir(self.notification_dir)]
        else:
            return []

    @property
    def model_map(self):
        '''
        a dictionary of which keys are the model classes' names, values are
        the model classes
        '''
        return self._model_map

    def try_view_report(self):
        '''
        this function will be invoked before accessing report or report-list,
        throw an exception if you don't want them to be accessed,
        I prefer *flask.ext.principal.PermissionDenied* personally
        '''
        pass

    def try_edit_data_set(self):
        '''
        this function will be invoked before creating/editing data set,
        throw an exception if you don't want them to be accessed,
        I prefer *flask.ext.principal.PermissionDenied* personally
        '''
        pass

    def try_edit_notification(self):
        '''
        this function will be invoked before creating/editing notification
        throw an exception if you don't want them to be accessed,
        I prefer *flask.ext.principal.PermissionDenied* personally
        '''
        pass

    @property
    def report_list(self):
        '''
        return all the reports
        '''
        return [Report(self, int(dir_name)) for dir_name in
                os.listdir(self.report_dir) if
                dir_name.isdigit() and dir_name != '0']

    def get_model_label(self, table):
        return self.table_label_map.get(table.name) or \
            self.table_map[table.name].__name__

    def report_list_template_param(self, report_list):
        '''
        extra template parameter provide to report list page, override this
        method if you want override default report list template
        '''
        return None

    def report_template_param(self, report):
        '''
        extra template parameter provide to report page, override this
        method if you want override default report template
        '''
        return None

    def data_set_list_template_param(self, data_set_list):
        '''
        extra template parameter provide to data set list page, override this
        method if you want override default data set list template
        '''
        return None

    def data_set_template_param(self, data_set):
        '''
        extra template parameter provide to data set page, override this
        method if you want override default data set template
        '''
        return None

    def notification_list_template_param(self, notification_list):
        '''
        extra template parameter provide to notification list page, override
        this method if you want override default notification list template
        '''
        return None

    def notification_template_param(self, notification):
        '''
        extra template parameter provide to notification page, override this
        method if you want override default notification template
        '''
        return None
