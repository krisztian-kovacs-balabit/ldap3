from time import time, sleep
from ldap3 import Server, Connection, BASE, ALL_ATTRIBUTES

SERVER = 'ldap://edir1.hyperv'
CONNECT_TIMEOUT = 2
RECEIVE_TIMEOUT = 3
log = open('timeouts_test_ldap3.txt', 'w')


def ask(connection_working, connection=None):
    message = 'Please ' + ('ensure server is REACHABLE' if connection_working else 'make server UNAVAILABLE') + ', then press Enter'
    if not connection:
        if str != bytes:  # python 3
            input(message)
        else:
            raw_input(message)
    else:
        done = False
        print('Please ensure server is ' + ('REACHABLE' if connection_working else 'UNAVAILABLE'))
        while not done:
            available = connection.server.check_availability()
            if (connection_working and available) or (not connection_working and not available):
                done = True
            sleep(2)


def get_connection(connect_timeout, receive_timeout):
    if connect_timeout:
        s = Server(SERVER, connect_timeout=connect_timeout)
    else:
        s = Server(SERVER)
    if receive_timeout:
        c = Connection(s, receive_timeout=receive_timeout)
    else:
        c = Connection(s)
    return c


def test_connection(connect_timeout, receive_timeout):
    print('Starting testing CONNECT TIMEOUT %s - RECEIVE TIMEOUT %s' % (connect_timeout, receive_timeout))
    c = get_connection(connect_timeout, receive_timeout)

    ask(False, c)
    print('Testing binding')
    t = time()
    try:
        c.open()
        c.bind()
        p0 = 'established connection: %010f' % (time() - t)
    except:
        p0 = 'connection timeout    : %010f' % (time() - t)

    ask(True, c)

    c = get_connection(connect_timeout, receive_timeout)
    print('Testing searching')
    try:
        c.open()
        c.bind()
        ask(False, c)
        t = time()
        try:
            c.search('', '(objectclass=*)', BASE, attributes=ALL_ATTRIBUTES)
            p1 = 'searching data        : %010f' % (time() - t)
        except:
            p1 = 'search timeout        : %010f' % (time() - t)
    except:
        p1 = 'ERROR opening the connection for searching'

    ask(True, c)
    c = get_connection(connect_timeout, receive_timeout)
    print('Testing StartTls')

    try:
        c.bind()
        if not c.start_tls():
            raise Exception('unable to start TLS on open socket')
        ask(False, c)
        t = time()
        try:
            c.search('', '(objectclass=*)', BASE, attributes=ALL_ATTRIBUTES)
            p1 = 'searching data (TLS)  : %010f' % (time() - t)
        except:
            p1 = 'search timeout (TLS)  : %010f' % (time() - t)
    except:
        p1 = 'ERROR opening the connection for searching with StartTls'

    ask(True, c)
    t = time()
    try:
        c.unbind()
        p2 = 'close connection      : %010f' % (time() - t)
    except:
        p2 = 'close timeout         : %010f' % (time() - t)
    h0 = '*' * 50
    h1 = 'CONNECT TIMEOUT %s - RECEIVE TIMEOUT %s' % (connect_timeout, receive_timeout)
    print(h0)
    print(h1)
    print(p0)
    print(p1)
    print(p2)
    print()
    log.writelines([h0 + '\n', h1 + '\n', p0 + '\n', p1 + '\n', p2 + '\n'])


if __name__ == '__main__':
    test_connection(CONNECT_TIMEOUT, RECEIVE_TIMEOUT)
    test_connection(CONNECT_TIMEOUT, None)
    test_connection(None, RECEIVE_TIMEOUT)
    test_connection(None, None)
    log.close()
