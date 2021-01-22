import time
import socket

class message:
    def __init__(self, msg, facility=16, servity=5, timestamp=time.localtime(), 
        hostname="esp32", appname="logger", procid="-", msgid="-"):
        """Creates a log messag object, that can later be turned into a Protocol-23-Format-String.

        Args:
            msg (str): the message, that is logged
            facility (int, optional): facility code, see ietf-syslog-protocol-23. Defaults to 16.
            servity (int, optional): servity code, see ietf-syslog-protocol-23. Defaults to 5.
            timestamp (tuple, optional): Defaults to utime.localtime().
            hostname (str, optional): hostename of the device. Defaults to "esp32".
            appname (str, optional): app, that is sending the msg. Defaults to "logger".
            procid (int, optional): Should be unique for each instance of the app. Defaults to -.
            msgid (int, optional): Should describe the topic of the message. Defaults to -.
        """
        self.facility = facility
        self.servity = servity
        self.timestamp = timestamp
        self.hostname = hostname
        self.appname = appname
        self.procid = procid
        self.msgid = msgid
        self.msg = msg
    
    def __str__(self):
        return "<{}>1 {:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.0Z {} {} {} {} {}".format(
            self.facility*8+self.servity,
            self.timestamp[0], self.timestamp[1], self.timestamp[2], self.timestamp[3], 
            self.timestamp[4], self.timestamp[5],
            self.hostname, self.appname, self.procid, self.msgid, self.msg
        )

class logger:
    def __init__(self, syslog_host, port=514, facility=16, hostname="esp32", 
        appname="logger"):
        """Creates a logger, that sends log messages per udp to a syslog server.

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


        Servity Codes:
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

        Args:
            syslog_host (str or ip): address of the server
            port (int, optional): port. Defaults to 514.
            facility (int, optional): facility code. Defaults to 16.
            hostname (str, optional): hostename of the device. Defaults to "esp32".
            appname (str, optional): app, that is sending the msg. Defaults to "logger".
        """

        self.syslog_host = syslog_host
        self.port = port
        self.facility = facility
        self.hostname = hostname
        self.appname = appname
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.debug = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 7), "utf-8"),(self.syslog_host,self.port))
        self.info = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 6), "utf-8"),(self.syslog_host,self.port))
        self.notice = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 5), "utf-8"),(self.syslog_host,self.port))
        self.warning = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 4), "utf-8"),(self.syslog_host,self.port))
        self.error = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 3), "utf-8"),(self.syslog_host,self.port))
        self.critical = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 2), "utf-8"),(self.syslog_host,self.port))
        self.alert = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 1), "utf-8"),(self.syslog_host,self.port))
        self.emergency = lambda msg: self.sock.sendto(bytes(self._create_msg(msg, 0), "utf-8"),(self.syslog_host,self.port))

    def _create_msg(self, msg, servity):
        m = message(msg, facility=self.facility, servity=servity, hostname=self.hostname,
            appname=self.appname)
        return str(m)
    