from flask import Flask, render_template, request, abort
from report_of_monaco_buchatskiy.report_racing import *

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'report_of_monaco_buchatskiy/file_data')
REQUIRED_ARGS = {'driver_id', 'order'}


def get_drivers(desc: bool) -> list:
    start_times = parse_log_file(file_name=START_LOG, files=DATA_DIR)
    end_times = parse_log_file(file_name=END_LOG, files=DATA_DIR)
    drivers_list = parse_txt_file(file_name=ABBREVIATIONS_FILENAME, files=DATA_DIR)
    return built_report(start_times, end_times, drivers_list, desc=desc)


@app.route('/')
def general():
    return render_template('general.html')


@app.route('/report/', methods=['GET'])
def report():
    drivers = get_drivers(desc=False)
    if request.args:
        if validate_request(request.args):
            order = request.args.get('order')
            if order == 'desc':
                drivers = get_drivers(desc=True)
            elif order == 'asc':
                drivers = get_drivers(desc=False)
            else:
                abort(404)
            return render_template('report.html', drivers=drivers)
        abort(400)
    else:
        return render_template('report.html', drivers=drivers)


@app.route('/report/drivers/', methods=['GET'])
def drivers():
    drivers = get_drivers(desc=False)
    if request.args:
        if validate_request(request.args):
            driver_id = request.args.get('driver_id')
            driver = (get_driver_by_id(drivers, driver_id))
            if driver is not None:
                return render_template('show_driver.html', driver=driver)
            abort(404)
        abort(400)
    else:
        return render_template('drivers.html', drivers=drivers)


def validate_request(args: dict) -> bool:
    args_values = []
    for arg, value in args.items():
        if arg in REQUIRED_ARGS:
            if value is not None and value != '':
                args_values.append(value)
    if all(args_values):
        if not args_values:
            return False
    return True


@app.errorhandler(400)
def page_not_found(error):
    return render_template('page_not_found.html'), 400


if __name__ == '__main__':
    app.run(debug=False)
