import signal

from visionSystem import VisionSystem

# globals for signal handling
RUNNING = True
PICTURE = False


def sigint_handler(signal, frame):
    """
    When SIGINT received, exit program
    """
    global RUNNING
    print("Received sigint")
    running = False


signal.signal(signal.SIGINT, sigint_handler)


def sigusr1_handler(signal, frame):
    """
    When SIGUSR1 received, take picture and print results to STDout
    """
    global PICTURE
    print("Received SIGUSR1")
    PICTURE = True


signal.signal(signal.SIGUSR1, sigusr1_handler)


def main():
    global RUNNING
    global PICTURE

    # instantiate vision object
    vision = VisionSystem()
    while RUNNING:
        if PICTURE:
            # take picture and get coordinates/orientation
            coordinates = vision.processOneFrame()
            print(coordinates)

            # set PICTURE to False to indicate ARM not waiting for picture
            PICTURE = False


if __name__ == "__main__":
    main()
