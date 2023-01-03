from PyQt5 import uic, QtGui, QtCore
import cv2
from src.utils import singleton, Utils
from src.processor import Processor

@singleton
class QtWindow:
    '''
    Class to create the window of the application and manage the events.
    '''
    
    def __init__(self):
        '''
        Constructor of the class.
        '''
        # Load the utils
        self.utils = Utils()
        # Load the video
        self.video = cv2.VideoCapture(self.utils.getValueFromConfigOf("video_relative_path"))
        # Load the processor
        self.processor = Processor()
        # Load the ui file
        self.ui = uic.loadUi(self.utils.getValueFromConfigOf("ui", "ui_relative_path"))
        # Set the window title
        self.ui.setWindowTitle(self.utils.getValueFromConfigOf("ui", "window_title"))
        # Set the counter
        value = self.utils.getValueFromConfigOf("ui", "counter_text")
        self.ui.counter.setText(value.format(0))
        # Set the speeds
        self.ui.spinSpeed.setValue(self.utils.getValueFromConfigOf("FPS"))
        self.ui.spinSpeed.valueChanged.connect(self.__speedButton__)
        # Set to show all the windows
        self.ui.buttonDebug.clicked.connect(self.__startDebug__)
        self.ui.buttonCloseDebug.clicked.connect(self.__stopDebug__)
        # Set the pause button
        self.ui.buttonPause.clicked.connect(self.__pauseButton__)
        # Set the restart button
        self.ui.buttonRestart.clicked.connect(self.__restartButton__)
        # Set the barriers conections
        self.ui.sliderBarrera2.valueChanged.connect(self.__change_barrier_upper_value__)
        self.ui.spinBarrera2.valueChanged.connect(self.__change_barrier_upper_value__)
        self.ui.sliderBarrera1.valueChanged.connect(self.__change_barrier_lower_value__)
        self.ui.spinBarrera1.valueChanged.connect(self.__change_barrier_lower_value__)
        # Create the timer
        self.timer = QtCore.QTimer(self.ui)
        # Connect the timer to the update function
        self.timer.timeout.connect(self.__update__)
        # Restart all de window values
        self.__restartButton__()
        # Start the video
        self.ui.show()
    
    def __speedButton__(self):
        '''
        ### Private method.
        Allow to change the speed of the video.

        ### Parameters:
        None

        ### Returns:
        None

        ### Rules:
        - The speed can't be greater than the max speed value defined in the config file. If the max speed value is not defined, the max speed value will be 99.
        '''
        speed = self.ui.spinSpeed.value()
        max_speed = self.utils.getValueFromConfigOf("MAX_SPEED")
        max_speed = max_speed if max_speed is not None else 99
        if speed == 0:
            self.timer.stop()
        else:
            self.timer.start()
            speed = max_speed - speed
            self.timer.setInterval(speed)

    def __startDebug__(self):
        '''
        ### Private method.
        Allow to show all the windows.

        ### Parameters:
        None

        ### Returns:
        None

        ### Rules:
        - The debug mode can't be activated if the video is paused.
        '''
        self.debug = True
    
    def __stopDebug__(self):
        '''
        ### Private method.
        Allow to close all the windows.

        ### Parameters:
        None

        ### Returns:
        None

        ### Rules:
        - The debug mode can't be deactivated if the video is paused.
        '''
        cv2.destroyAllWindows()
        self.debug = False

    def __pauseButton__(self):
        '''
        ### Private method.
        Allow to pause the video.

        ### Parameters:
        None

        ### Returns:
        None
        '''
        if self.timer.isActive():
            self.timer.stop()
        else:
            speed = self.ui.spinSpeed.value()
            self.timer.start(speed)
    
    def __restartButton__(self):
        '''
        ### Private method.
        Allow to restart the video and all the values of the window to the default values.

        ### Parameters:
        None

        ### Returns:
        None

        ### Rules:
        - If the debug mode is activated, the debug mode will be deactivated.
        - The barriers values will be set to the default values defined in the config file.
        - The video will be set to the default video defined in the config file.
        - The speed will be set to the default speed defined in the config file like FPS value, and the timer will be started.
        '''
        # Reset the processor to the default values
        self.processor.reset()
        # Close all the windows
        cv2.destroyAllWindows()
        # Stop the debug mode if it is activated closing all the windows
        self.__stopDebug__()
        # Set the default values of the barriers.
        lower_barrier = self.utils.getValueFromConfigOf("barriers", "lower", "y")
        upper_barrier = self.utils.getValueFromConfigOf("barriers", "upper", "y")
        self.__set_default_barriers__(lower_barrier, upper_barrier)
        # Set the default video
        self.video = cv2.VideoCapture(self.utils.getValueFromConfigOf("video_relative_path"))
        # Set the first frame
        self.firstFrame = cv2.cvtColor(self.video.read()[1], cv2.COLOR_BGR2GRAY)
        # Set the default timer speed value and start the timer
        self.timer.start(self.utils.getValueFromConfigOf("FPS"))
    
    def __set_default_barriers__(self, lower, upper):
        '''
        ### Private method.
        Set the default barriers values.

        ### Parameters:
        - lower: The lower barrier value.
        - upper: The upper barrier value.

        ### Returns:
        None

        ### Rules:
        - The lower barrier value can't be greater than the upper barrier value.
        - The upper barrier value can't be lower than the lower barrier value.
        - The barriers values can't be greater than 99.
        '''
        if lower is not None and upper is not None:
            if lower > upper:
                lower, upper = upper, lower
            self.__change_barrier_upper_value__(
                upper,
                self.utils.getValueFromConfigOf("barriers", "upper", "color"),
                self.utils.getValueFromConfigOf("barriers", "upper", "thickness")
            )
            self.__change_barrier_lower_value__(
                lower,
                self.utils.getValueFromConfigOf("barriers", "lower", "color"),
                self.utils.getValueFromConfigOf("barriers", "lower", "thickness")
            )
        else:
            self.__set_default_barriers__(0, 99)

    def __change_barrier_lower_value__(self, lower, color=None, thickness=None):
        '''
        ### Private method.
        Allow to change the lower barrier value.

        ### Parameters:
        - lower: The new lower barrier value.
        - color: The new color of the lower barrier.
        - thickness: The new thickness of the lower barrier.

        ### Returns:
        None

        ### Rules:
        - The lower barrier value can't be greater than the upper barrier value.
        '''
        if lower is None:
            return
        upper = self.ui.spinBarrera2.value()
        lower = lower if lower <= upper else upper
        self.ui.spinBarrera1.setValue(lower)
        self.ui.sliderBarrera1.setValue(lower)
        self.__lower_barrier__ = { "y": lower, "color": color if color is not None else [255, 0, 0], "thickness": thickness if thickness is not None else 5 }
    
    def __change_barrier_upper_value__(self, upper, color=None, thickness=None):
        '''
        ### Private method.
        Allow to change the upper barrier value.

        ### Parameters:
        - upper: The new upper barrier value.
        - color: The new color of the upper barrier.
        - thickness: The new thickness of the upper barrier.
        
        ### Returns:
        None

        ### Rules:
        - The upper barrier value can't be lower than the lower barrier value.
        '''
        if upper is None:
            return
        lower = self.ui.spinBarrera1.value()
        upper = upper if upper >= lower else lower
        self.ui.spinBarrera2.setValue(upper)
        self.ui.sliderBarrera2.setValue(upper)
        self.__upper_barrier__ = { "y": upper, "color": color if color is not None else [0, 255, 0], "thickness": thickness if thickness is not None else 5 }

    def __update__(self):
        '''
        ### Private method.
        Update the ui for each frame.

        ### Parameters:
        None

        ### Returns:
        None
        '''
        ret, image = self.video.read()
        if (ret):
            # Process and get the contours
            processed = self.processor.fromFrameToContours(image, self.firstFrame)
            cnts = processed["cnts"]
            contours = processed["contours"]
            # Get the width and height of the video_source
            width = self.ui.video_source.width()
            height = self.ui.video_source.height()
            # Get the centroid of the person
            centroid = None
            if len(cnts) != 0:
                # Get the contour of the person
                contours = processed["contours"]
                # Get the centroid of the person
                centroid = self.processor.fromContoursToCentroid(contours)
                # Get the position of the centroid in the video_source window
                x = int(centroid[0] * width / self.video.get(3))
                y = int(centroid[1] * height / self.video.get(4))
                # Draw the centroid of the person
                cv2.drawContours(image, [contours], -1, self.utils.getValueFromConfigOf("contours", "color"), 1)
                cv2.circle(image, center=centroid, radius=7, color=(92, 200, 200), thickness=-1)
            # Resize the image
            image = cv2.resize(image, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
            # Draw the barriers
            image = self.__show_lines__(image)
            # Get the pixmap from the image and show it
            pixmap = QtGui.QPixmap(QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888))
            self.ui.video_source.setPixmap(pixmap)
            # Update the counter
            if centroid is not None:
                counter = self.processor.process(centroid=(x, y), barriers=self.__barriers__)
                self.ui.counter.setText(self.utils.getValueFromConfigOf("ui", "counter_text").format(counter))
            # Show the debug windows
            if self.debug:    
                gray = processed["gray"]
                frameDelta = processed["frameDelta"]
                blurred = processed["blurred"]
                thresh = processed["thresh"]
                cv2.imshow("Gray", gray)
                cv2.imshow("Frame Delta", frameDelta)
                cv2.imshow("Blurred", blurred)
                cv2.imshow("Thresh", thresh)
                cv2.imshow("Frame", image)

    def __calculate_position_barriers__(self, image):
        '''
        Calculate the position of the barriers in the image.

        ### Parameters:
        - image: The image to calculate the barriers.

        ### Returns:
        The barriers in the image: (lower_barrier, upper_barrier)
        '''
        # Get the width and height of the image
        height = image.shape[0]
        # Get the barriers from the ui position of y (0 to 100)
        lower_barrier = self.ui.sliderBarrera1.value()
        upper_barrier = self.ui.sliderBarrera2.value()
        # Invert the barriers
        lower_barrier = 100 - lower_barrier
        upper_barrier = 100 - upper_barrier
        # Calculate the real position of the barriers
        lower_barrier = int(lower_barrier * height / 100)
        upper_barrier = int(upper_barrier * height / 100)
        # Save the barriers
        self.__barriers__ = (lower_barrier, upper_barrier)
        # Return the barriers
        return (lower_barrier, upper_barrier)

    def __show_lines__(self, image):
        '''
        Draw the barriers in the image.

        ### Parameters:
        - image: The image to draw the barriers.

        ### Returns:
        The image with the barriers.
        '''
        # Get the barriers
        lower_barrier, upper_barrier = self.__calculate_position_barriers__(image)
        # Get the colors and thickness of the barriers
        lower_barrier_color = self.__lower_barrier__["color"]
        upper_barrier_color = self.__upper_barrier__["color"]
        lower_barrier_thickness = self.__lower_barrier__["thickness"]
        upper_barrier_thickness = self.__upper_barrier__["thickness"]
        # Draw the lower barrier
        y = lower_barrier
        point1 = (0, y)
        point2 = (image.shape[1], y)
        cv2.line(image, pt1=point1, pt2=point2, color=lower_barrier_color, thickness=lower_barrier_thickness)
        # Draw the upper barrier
        y = upper_barrier
        point1 = (0, y)
        point2 = (image.shape[1], y)
        cv2.line(image, pt1=point1, pt2=point2, color=upper_barrier_color, thickness=upper_barrier_thickness)
        return image