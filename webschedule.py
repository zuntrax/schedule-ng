#!/usr/bin/env python3

import logging

from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from functools import reduce

from fahrplan.model.schedule import Schedule

import schedule
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

log = logging.getLogger(__name__)

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, config, import_handlers, export_handlers, *args, **kwargs):
        self.config = config
        self.import_handlers = import_handlers
        self.export_handlers = { h.config["path"]: h for h in export_handlers }
        super().__init__(*args, **kwargs)

    def do_GET(self):
        log.info(f'Get {self.path}')
        url = urlparse(self.path)
        path = url.path[1:]

        if path not in self.export_handlers:
            self.send_error(404, 'Path not found')
            return

        try:
            schedule = self.make_schedule()
            if schedule is None:
                self.send_error(204)
                return
            handler = self.export_handlers[path]
            body = handler.export(schedule)
            if body is not None and not isinstance(body, bytes):
                body = body.encode()
            content_type = handler.content_type
        except Exception as err:
            self.send_error(500, str(err))
            raise

        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def make_schedule(self):
        imported_schedules = []
        log.info('Running import handlers')
        for handler in self.import_handlers:
            log.info(f'Running import handler "{handler.name}".')
            imported_schedules.append(handler.run())
        log.debug('Finished running import handlers')

        if not any(imported_schedules):
            return None

        log.info('Merging schedules.')
        final_schedule = reduce(Schedule.merge, imported_schedules)
        log.debug('Finished merging schedules.')

        return final_schedule

def main():
    ap = ArgumentParser()
    ap.add_argument('--verbose', '-v', action='count')
    ap.add_argument('--quiet', '-q', action='count')
    ap.add_argument('--config', '-c', nargs='?', type=FileType('r'), default='./config.ini')
    ap.add_argument('--logfile', '-l')
    ap.add_argument('--debug', '-d', action='store_true')
    ap.add_argument('--interface', '-i', default='localhost')
    ap.add_argument('--port', '-p', type=int, default=8080)
    args = ap.parse_args()

    schedule.configure_logging(args)

    log.info(f'Using config file "{args.config.name}".')
    config = ConfigParser()
    config.read_file(args.config)
    log.debug('Basic initialization done.')

    import_handlers = schedule.initialize_import_handlers(config)
    if not import_handlers:
        log.critical("No import handlers to run, aborting.")
        sys.exit(1)

    export_handlers = schedule.initialize_export_handlers(config)
    if not export_handlers:
        log.critical("No export handlers to run, aborting.")
        sys.exit(1)

    req_handler = partial(HTTPRequestHandler, config, import_handlers, export_handlers)
    httpd = HTTPServer((args.interface, args.port), req_handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
