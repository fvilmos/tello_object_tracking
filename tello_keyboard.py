###########################################
# Tello simple kyeboard commands
# Author: fvilmos
###########################################

from utils.telloconnect import TelloConnect
import signal


if __name__=="__main__":
    
    # signal handler
    def signal_handler(sig, frame):
        raise Exception

    # capture signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    tello = TelloConnect(DEBUG=False)
    
    # wait till connected, than proceed
    tello.wait_till_connected()
    tello.start_communication()


    while True:

        try:            
            k = input()
                    
            # exit
            if k == 'q':
                tello.stop_communication()
                break

            if k == 't':
                tello.send_cmd('takeoff')
            
            if k == 'l':
                tello.send_cmd('land')

            if k == 'w':
                tello.send_cmd('up 20')
            
            if k == 's':
                tello.send_cmd('down 20')

            if k == 'a':
                tello.send_cmd('cw 20')

            if k == 'd':
                tello.send_cmd('ccw 20')

        except Exception:
            tello.stop_communication()
            break
