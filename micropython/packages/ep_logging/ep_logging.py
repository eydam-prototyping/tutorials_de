import time
import socket


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class message:
    def __init__(self, msg, facility=16, severity=5, timestamp=time.localtime(), 
        hostname="esp32", appname="logger", procid="-", msgid="-", format="Protocol-23-Format"):
        """Creates a log messag object, that can later be turned into a Protocol-23-Format-String.

        Args:
            msg (str): the message, that is logged
            facility (int, optional): facility code, see ietf-syslog-protocol-23. Defaults to 16.
            severity (int, optional): severity code, see ietf-syslog-protocol-23. Defaults to 5.
            timestamp (tuple, optional): Defaults to utime.localtime().
            hostname (str, optional): hostename of the device. Defaults to "esp32".
            appname (str, optional): app, that is sending the msg. Defaults to "logger".
            procid (int, optional): Should be unique for each instance of the app. Defaults to -.
            msgid (int, optional): Should describe the topic of the message. Defaults to -.
        """
        self.facility = facility
        self.severity = severity
        self.timestamp = timestamp
        self.hostname = hostname
        self.appname = appname
        self.procid = procid
        self.msgid = msgid
        self.msg = msg
        self.format = format
    
    def __str__(self):
        return "<{}>1 {:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.0Z {} {} {} {} {}".format(
            self.facility*8+self.severity,
            self.timestamp[0], self.timestamp[1], self.timestamp[2], self.timestamp[3], 
            self.timestamp[4], self.timestamp[5],
            self.hostname, self.appname, self.procid, self.msgid, self.msg
        )

class default_logger:
    def __init__(self, **kwargs):
        self.facility = kwargs.get("facility", 16)
        self.hostname = kwargs.get("hostname", "esp32")
        self.appname = kwargs.get("appname", "logger")
        self.level = kwargs.get("level", 7)

        self.debug = lambda msg: self._output(self._create_msg(msg, 7))
        self.info = lambda msg: self._output(self._create_msg(msg, 6))
        self.notice = lambda msg: self._output(self._create_msg(msg, 5))
        self.warning = lambda msg: self._output(self._create_msg(msg, 4))
        self.error = lambda msg: self._output(self._create_msg(msg, 3))
        self.critical = lambda msg: self._output(self._create_msg(msg, 2))
        self.alarm = lambda msg: self._output(self._create_msg(msg, 1))
        self.emergency = lambda msg: self._output(self._create_msg(msg, 0))

    def _create_msg(self, msg, severity):
        if severity<=self.level:
            m = message(msg, facility=self.facility, severity=severity, hostname=self.hostname,
                appname=self.appname)
            return str(m)
        return ""
    
    def _output(self, str_msg):
        if str_msg != "":
            print(str_msg)


class colored_logger(default_logger):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _create_msg(self, msg, severity):
        if severity<=self.level:
            m = message(msg, facility=self.facility, severity=severity, hostname=self.hostname,
                appname=self.appname)
            if severity <= 1:
                return bcolors.FAIL + bcolors.BOLD + str(m) + bcolors.ENDC
            if severity <= 3:
                return bcolors.FAIL + str(m) + bcolors.ENDC
            if severity <= 4:
                return bcolors.WARNING + str(m) + bcolors.ENDC
            if severity <= 5:
                return bcolors.OKGREEN + str(m) + bcolors.ENDC
            return str(m)
        return ""

class syslog_logger(default_logger):
    def __init__(self, syslog_host, **kwargs):
        """Creates a logger, that sends log messages per udp to a syslog server.
        Args:
            syslog_host (str or ip): address of the server
            port (int, optional): port. Defaults to 514.
            facility (int, optional): facility code. Defaults to 16.
            hostname (str, optional): hostename of the device. Defaults to "esp32".
            appname (str, optional): app, that is sending the msg. Defaults to "logger".
            level (int, optional): log level: 7=debug, 0=emergency. Defaults to 7.
        """

        super().__init__(**kwargs)

        self.syslog_host = syslog_host
        self.port = kwargs.get("port", 514)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def _output(self, str_msg):
        if str_msg != "":
            self.sock.sendto(bytes(str_msg, "utf-8"),(self.syslog_host, self.port))

    
"""
Facility Codes:
        Numerical             Facility
        Code

        0             kernel messages
        1             user-level messages
        2             mail system
        3             system daemons
        4             security/authorization messages
        5             messages generated internally by syslogd
        6             line printer subsystem
        7             network news subsystem
        8             UUCP subsystem
        9             clock daemon
        10             security/authorization messages
        11             FTP daemon
        12             NTP subsystem
        13             log audit
        14             log alert
        15             clock daemon (note 2)
        16             local use 0  (local0)
        17             local use 1  (local1)
        18             local use 2  (local2)
        19             local use 3  (local3)
        20             local use 4  (local4)
        21             local use 5  (local5)
        22             local use 6  (local6)
        23             local use 7  (local7)


Severity Codes:
    Numerical         Severity
        Code

        0       Emergency: system is unusable
        1       Alert: action must be taken immediately
        2       Critical: critical conditions
        3       Error: error conditions
        4       Warning: warning conditions
        5       Notice: normal but significant condition
        6       Informational: informational messages
        7       Debug: debug-level messages
"""