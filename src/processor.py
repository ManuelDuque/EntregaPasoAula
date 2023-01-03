import enum
from src.utils import singleton, Utils

class State(enum.Enum):
    '''
    Define the states of the centroid position in the image. The states are:
    - INSIDE: The centroid is above the upper barrier.
    - OUTSIDE: The centroid is below the lower barrier.
    - ENTERING: The centroid is between the barriers and is going to the inside.
    - EXITING: The centroid is between the barriers and is going to the outside.
    '''
    INSIDE = 1
    OUTSIDE = 2
    ENTERING = 3
    EXITING = 4

@singleton
class Processor:
    '''
    Class to process the counter based on the centroid position and the barriers.
    '''

    def __init__(self):
        '''
        ## Constructor
        Initialize the processor.
        '''
        self.__utils__ = Utils()
        self.reset()

    def reset(self):
        self.__image_state__ = None
        self.__state__ = State.INSIDE
        self.__counter__ = 0

    def fromFrameToContours(self, image, comparative_image):
        '''
        Get the contours of the moving object in the image.

        ### Parameters:
        image: The image to process (numpy.ndarray).
        comparative_image: The image to compare with the current image (numpy.ndarray).

        ### Returns:
        Dictionary with the following keys:
        - contours: The contours of the moving object in the image (list).
        - gray: The image transformed to gray (numpy.ndarray).
        - frameDelta: The difference between the first frame and the current frame (numpy.ndarray).
        - blurred: The image with a blur applied (numpy.ndarray).
        - thresh: The image with a threshold applied (numpy.ndarray).
        - cnts: The contours of the moving object in the image (list).
        '''
        import cv2, imutils
        # Transform the image to gray
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Calculate the difference between the first frame and the current frame
        frameDelta = cv2.absdiff(comparative_image, gray)
        # Apply a blur to the difference image
        blurred = cv2.GaussianBlur(frameDelta, (21, 21), 0)
        # Threshold the difference image
        thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)[1]
        # Find the centroid of the moving object
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # Get the contours
        contours = None
        if len(cnts) != 0:
        # Get the biggest contour
            contours = max(cnts, key=cv2.contourArea)
        state = {"gray": gray, "frameDelta": frameDelta, "blurred": blurred, "thresh": thresh, "cnts": cnts, "contours": contours}
        self.__image_state__ = {"state": state, "frame": image}
        return state

    def getSavedImageState(self):
        '''
        Get the last state of the image frame processed.

        ### Returns:
        Dictionary with the following keys:
        - contours: The contours of the moving object in the image (list).
        - gray: The image transformed to gray (numpy.ndarray).
        - frameDelta: The difference between the first frame and the current frame (numpy.ndarray).
        - blurred: The image with a blur applied (numpy.ndarray).
        - thresh: The image with a threshold applied (numpy.ndarray).
        - cnts: The contours of the moving object in the image (list).
        '''
        return self.__image_state__

    def fromContoursToCentroid(self, contours):
        '''
        Get the centroid of the moving object in the image.

        ### Parameters:
        cnts: The contours of the moving object in the image (list).

        ### Returns:
        The centroid position in the image (tuple).
        '''
        import cv2
        # Get the moments of the contour
        moments = cv2.moments(contours)
        # Get the centroid of the person
        centroid = (int(moments["m10"] / moments["m00"] if moments["m00"] != 0 else 1), int(moments["m01"] / moments["m00"] if moments["m00"] != 0 else 1))
        return centroid

    def process(self, centroid, barriers):
        '''
        Calculate the counter based on the centroid position and the barriers.

        ### Parameters:
        centroid: The position of the centroid in the image.
        barriers: The position of the barriers in the image.

        ### Returns:
        The counter value after the process is done (int).
        '''
        # Get the barriers
        lower_barrier, upper_barrier = barriers
        # Handle the centroid position in the image (above, between or below the barriers)
        centroidY = centroid[1]
        self.__centroid_above_upper_barrier__(centroidY, upper_barrier)
        self.__centroid_between_barriers__(centroidY, upper_barrier, lower_barrier)
        self.__centroid_below_lower_barrier__(centroidY, lower_barrier)
        return self.__counter__
    
    def __update_counter__(self, increment):
        '''
        ### Private method.
        Update the counter value.        

        ### Parameters:
        increment: The value to increment the counter (int).

        ### Rules:
        - The counter can't be negative

        ### Returns:
        The counter value after the process is done (int).
        '''
        self.__counter__ += increment
        if self.__counter__ < 0:
            self.__counter__ = 0
        return self.__counter__

    def __centroid_between_barriers__(self, centroidY, upper_barrier, lower_barrier):
        '''
        ### Private method.
        Handle the centroid position between the barriers (entering or exiting).

        ### Parameters:
        centroidY: The Y position of the centroid (int).
        upper_barrier: The Y position of the upper barrier (int).
        lower_barrier: The Y position of the lower barrier (int).

        ### Rules:
        - If the centroid is between the barriers and the state is INSIDE, then the new state is EXITING.
        - If the centroid is between the barriers and the state is OUTSIDE, then the new state is ENTERING.
        '''
        if centroidY >= upper_barrier and centroidY <= lower_barrier:
            # print(f"Centroid {centroidY} between barriers: {lower_point} - {upper_point}")
            if self.__state__ == State.INSIDE:
                self.__state__ = State.EXITING
            elif self.__state__ == State.OUTSIDE:
                self.__state__ = State.ENTERING

    def __centroid_below_lower_barrier__(self, centroidY, lower_barrier):
        '''
        ### Private method.
        Handle the centroid position below the lower barrier (outside).

        ### Parameters:
        centroidY: The Y position of the centroid (int).
        lower_barrier: The Y position of the lower barrier (int).

        ### Rules:
        - If the centroid is below the lower barrier and the state is EXITING, then the new state is OUTSIDE and the counter is decremented.
        - If the centroid is below the lower barrier and the state is ENTERING, then the new state is OUTSIDE but the counter is not decremented.
        '''
        if centroidY > lower_barrier:
            # print(f"Centroid {centroidY} above upper barrier: {upper_point}")
            if self.__state__ == State.EXITING:
                self.__state__ = State.OUTSIDE
                self.__update_counter__(-1)
            elif self.__state__ == State.ENTERING:
                self.__state__ = State.OUTSIDE

    def __centroid_above_upper_barrier__(self, centroidY, upper_barrier):
        '''
        ### Private method.
        Handle the centroid position above the upper barrier (inside).

        ### Parameters:
        centroidY: The Y position of the centroid (int).
        upper_barrier: The Y position of the upper barrier (int).

        ### Rules:
        - If the centroid is above the upper barrier and the state is ENTERING, then the new state is INSIDE and the counter is incremented.
        - If the centroid is above the upper barrier and the state is EXITING, then the new state is INSIDE but the counter is not incremented.
        '''
        if centroidY < upper_barrier:
            # print(f"Centroid {centroidY} below lower barrier: {lower_point}")
            if self.__state__ == State.EXITING:
                self.__state__ = State.INSIDE
            elif self.__state__ == State.ENTERING:
                self.__state__ = State.INSIDE
                self.__update_counter__(1)